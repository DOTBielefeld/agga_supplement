import os
import argparse
import numpy as np



class Loandra_Wrapper():

    def get_command_line_args(self, runargs, config):
            
        instance = runargs["instance"]
        configuration =""
    
        for param, value in config.items():
            if param in ["cb-i-varres", "cb-varCG", "cb-varres", "cb-del", "cb-cglim", "cb", "preprocess", "pr-rec", "pr-min", "cb-r-2-s", "cb-del"]:
                if value == True and isinstance(value, (bool, np.bool_))  :
                    configuration += f"{param} "
                elif value == False and isinstance(value, (bool, np.bool_)): 
                    configuration += f"no-{param} "
                else:
                    configuration = configuration + f"{param}={value} "
            else:
                if value == True and isinstance(value, (bool, np.bool_))  : 
                    configuration += f"-{param} "
                elif value == False and isinstance(value, (bool, np.bool_)): 
                    configuration += f"-no-{param} "
                else:
                    configuration = configuration + f"-{param}={value} "

        instance_p = f'"./input/{instance}"'

        exc = './input/target_algorithms/loandra/loandra'

        
        cmd = f'stdbuf -oL {exc} {instance_p} -verbosity=1 -no-adapt -no-rnd-init -rnd-seed={runargs["seed"]} {configuration}'
        return cmd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=dict)
    parser.add_argument("--runargs", type=dict)


    wrapper = Loandra_Wrapper()
    print(wrapper.Loandra_Wrapper(parser.runargs, parser.config))

