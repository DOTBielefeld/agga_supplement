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



if __name__ == "__main__":

    instance_p, cutoff, seed = sys.argv[1:4]

    rest_args = sys.argv[4:]

    memory_limit = 1024 * 2

    ref_path = "./input/instances/sat/sets/maxcut/bipartite/ref_quality.json"
    with open(ref_path) as f:
        ref_points = f.read()
    ref_points = json.loads(ref_points)

    configuration = " "
    for count in range(0, len(rest_args),2):
        if rest_args[count+1]=="on":
            configuration += f"{rest_args[count]} "
        elif rest_args[count+1]=="off":
            configuration += f"-no{rest_args[count]} "
        else:
            configuration += f"{rest_args[count]}={rest_args[count+1]} "

    exc = './input/target_algorithms/Open-WBO-Inc-master/open-wbo-inc'

    cmd = f"stdbuf -oL {exc} {instance_p} -verbosity=1 -rnd-seed={seed} {configuration}"  # -q

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
    out_put = []

    pareto = []
    while True:
        try:
            line = q.get(timeout=.5)
            empty_line = False
            try:
                cpu_time_p = p.cpu_times().user
                memory_p = p.memory_info().rss / 1024 ** 2
            except:
                pass
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
                    print("killed")
                except Exception as e:
                    pass

        except Empty:
            try:
                cpu_time_p = p.cpu_times().user
                memory_p = p.memory_info().rss / 1024 ** 2
            except:
                pass
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

        if len(line) != 0:
            if line[0] == "o":
                quality = re.findall(f"\d+", line)
                pareto.append([cpu_time_p, float(quality[0])])
        if "OPTIMUM FOUND" in line:
            pareto.append([cpu_time_p, 0])
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










