#!/opt/software/pc2/EB-SW/software/Anaconda3/2021.11/bin/python
import sys


import sys
import psutil
import subprocess
import os
from datetime import datetime

from threading import Thread
from queue import Queue, Empty
import time
import argparse
import resource
import signal
import json
import re

import numpy as np
import multiprocessing as mp
from pymoo.indicators.hv import HV


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        line = line.decode("utf-8")
        queue.put(line)
    out.close()

    
def get_command_line_args(instance, cutoff, seed, config):

    binary = "./input/target_algorithms/CPLEX-22_1_1/cplex/bin/x86-64_linux/cplex"

    params = []
    if config["simplex_perturbation_switch"] == "yes":
        simplex_perturbation_value = config["simplex_perturbation_switch"] + " " + config["perturbation_constant"]
    else:
        simplex_perturbation_value = config["simplex_perturbation_switch"] + " 0.00000001"
    params.append("set simplex perturbationlimit %s " % (simplex_perturbation_value))
    try:
        del config["simplex_perturbation_switch"]
        del config["perturbation_constant"]
    except KeyError:
        pass

    for name, value in config.items():
        params.append("%s %s" % (name.replace("_", " "), value))

    metaparams = [
        "set logfile *",
        "read %s" % instance,
        "set clocktype 1",
        "set threads 1",
        f"set timelimit 300", # set this high since we measure the cpu time from the outside
        "set mip limits treememory 2000",  # this should also be handled outside
        "set workdir .",
        "set mip tolerances mipgap 0"]
    if seed != -1:
        metaparams.append("set randomseed %d" % seed)

    metaparams.extend(params)
    metaparams.append("change sense obj maximum")
    metaparams.append("display settings all")
    metaparams.append("opt")
    metaparams.append("quit")

    return binary + " -c \"" + "\" \"".join(metaparams) + "\""


if __name__ == "__main__":
    instance, cutoff, seed = sys.argv[1:4]

    rest_args = sys.argv[4:]

    memory_limit = 1024 * 2

    ref_path = "./input/instances/mip/sets/cvrp_500_750_1000/ref_quality.json"
    with open(ref_path) as f:
        ref_points = f.read()
    ref_points = json.loads(ref_points)

    conf = {}
    for i in range(0, len(rest_args),2):
        conf[rest_args[i]] = rest_args[i + 1]

    cmd = get_command_line_args(instance, float(cutoff),int(seed), conf )

    p = psutil.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     preexec_fn=os.setsid)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True
    t.start()
    timeout = False
    out_put = []
    cpu_time_p = 0
    line = ""
    status = "SUCCESS"
    memory_p = 0

    pareto = []
    while True:
        try:
            line = q.get(timeout=.5)
            empty_line = False

            cpu_time_p = p.cpu_times().user
            memory_p = p.memory_info().rss / 1024 ** 2

            if float(cpu_time_p) >= float(cutoff):
                status = "TIMEOUT"
                cpu_time_p = cutoff
                if p.poll() is None:
                    p.terminate()
                time.sleep(1)
                if p.poll() is None:
                    p.kill()
                time.sleep(1)
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except Exception as e:
                    pass

        except Empty:

            cpu_time_p = p.cpu_times().user
            memory_p = p.memory_info().rss / 1024 ** 2

            empty_line = True

            if float(cpu_time_p) >= float(cutoff):

                status = "TIMEOUT"
                cpu_time_p = cutoff
                if p.poll() is None:
                    p.terminate()
                time.sleep(1)
                if p.poll() is None:
                    p.kill()
                time.sleep(1)


            if float(memory_p) >= memory_limit:
                status = "MEMOUT"
                cpu_time_p = cutoff
                if p.poll() is None:
                    p.terminate()
                time.sleep(1)
                if p.poll() is None:
                    p.kill()
                time.sleep(1)
            pass

        if "Integer optimal solution" in line:
            pareto.append([cpu_time_p, 0])
        else:
            if len(line) != 0:
                if line[0] == "*":
                    quality = re.findall(f"(\d+\.\d+)%", line)
                    if len(quality) > 0:
                        pareto.append([cpu_time_p, float(quality[0])])

        if empty_line and p.poll() != None:
            break

    p.stdout.close() 
    p.wait()

    while not q.empty():
        dc = q.get()

    mp.active_children()
    t.join()

    ind_hv = HV(ref_point=[1, 1])
    if len(pareto) != 0:
        # Multiply quality by 1.5 to be on the safe side.
        # Divide by 1.1 to get a scale suitable for a reference hypervolume of 1.
        full_pareto_front_norm = ((np.array(pareto)) /(np.array([cutoff, ref_points[instance]*1.5])*1.1))
        hv_full_front = ind_hv(full_pareto_front_norm)
        # Safeguards, but should not happen.
        if hv_full_front < 0:
            hv_full_front = 1
        else:
            hv_full_front  = 1 - hv_full_front
    else:
        hv_full_front = 1
    print(f"GGA SUCCESS {hv_full_front}")









