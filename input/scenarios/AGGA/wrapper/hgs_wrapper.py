import os
import argparse
import numpy as np


class HGS_Wrapper():

    def get_command_line_args(self, runargs, config):
            
        instance = runargs["instance"]
        configuration =""
    
        for param, value in config.items():
            if value == True and isinstance(value, (bool, np.bool_))  : 
                configuration += f"-{param} "
            elif value == False and isinstance(value, (bool, np.bool_)): 
                configuration += f"-no-{param} "
            else:
                configuration = configuration + f"-{param} {value} "

        instance_p = f'"./input/{instance}"'
        exc = './input/target_algorithms/HGS-CVRP-main/build/hgs'

        
        cmd = f'stdbuf -oL {exc} {instance_p} mySolution.sol -seed {runargs["seed"]} {configuration} -round 0'

        return cmd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=dict)
    parser.add_argument("--runargs", type=dict)


    wrapper = HGS_Wrapper()
    print(wrapper.get_command_line_args(parser.runargs, parser.config))

