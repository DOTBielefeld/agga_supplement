#!/usr/bin/python3
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


if __name__ == "__main__":
    configuration_id = sys.argv[1]
    instance_id = sys.argv[2]
    seed = sys.argv[3]
    instance = sys.argv[4]
    rest_args = sys.argv[5:]
    cutoff = 60

    memory_limit = 1024 * 2

    configuration = ' '.join(rest_args)
            

    exc ='./input/target_algorithms/loandra/loandra'
    instance_p = f'"./input/{instance}"'

    cmd = [ f"stdbuf -oL {exc} {instance_p} -verbosity=1 -rnd-seed={seed} {configuration}"]
    

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
        output_tigger = re.search("o \d+", line)
        if output_tigger:
            quality = re.findall(f"\d+", line)
            if len(quality) != 0:
                if float(quality[0]) < last_quality:
                    last_quality = float(quality[0])
        if "OPTIMUM FOUND" in line:
            last_quality = 0

        if empty_line and p.poll() != None:
            break

    p.stdout.close()  
    p.wait()
    
    while not q.empty():
        dc = q.get()

    mp.active_children()
    t.join()

    print(last_quality, cpu_time_p)





