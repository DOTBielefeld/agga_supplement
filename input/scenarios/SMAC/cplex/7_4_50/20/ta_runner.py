import sys
import psutil
import subprocess
import os
from datetime import datetime

from threading  import Thread
from queue import Queue, Empty
import time
import resource
import signal

import multiprocessing as mp
import re

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        line = line.decode("utf-8")
        queue.put(line)
    out.close()

def get_command_line_args(instance, cutoff, seed, config):

    binary = "./input/target_algorithms/CPLEX-22_1_1/cplex/bin/x86-64_linux/cplex"

    params = []
    if config["-simplex_perturbation_switch"] == "yes":
        simplex_perturbation_value = config["-simplex_perturbation_switch"] + " " + config["-perturbation_constant"]
    else:
        simplex_perturbation_value = config["-simplex_perturbation_switch"] + " 0.00000001"
    params.append("set simplex perturbationlimit %s " % (simplex_perturbation_value))
    try:
        del config["-simplex_perturbation_switch"]
        del config["-perturbation_constant"]
    except KeyError:
        pass

    for name, value in config.items():
        params.append("set %s %s" % (name.replace("_", " ")[1:], value))

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
    instance, instance_specific, cutoff, runlength = sys.argv[1:5]
    seed = sys.argv[5]

    rest_args = sys.argv[6:]

    memory_limit = 1024 * 2

    instance_p = f'"./input/{instance}"'

    conf = {}
    for i in range(0, len(rest_args),2):
        conf[rest_args[i]] = rest_args[i + 1]

    cmd = get_command_line_args(instance_p, float(cutoff),int(seed), conf )
    

    p = psutil.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
    last_quality = 100000
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

        output_tigger = re.search("(\d+\.\d+)%", line)
        if output_tigger:
            quality = re.findall(f"(\d+\.\d+)%", line)
            if len(quality) != 0:
                if float(quality[0]) < last_quality:
                    last_quality = float(quality[0])
        elif "Integer optimal solution" in line:
                last_quality = 0

        if empty_line and p.poll() != None:
            break

    p.stdout.close() 
    p.wait()
    
    while not q.empty():
        dc = q.get()
        
    mp.active_children()
    t.join()

    print(f"Result for SMAC: SUCCESS, {cpu_time_p}, -1, {last_quality}, {seed}")



