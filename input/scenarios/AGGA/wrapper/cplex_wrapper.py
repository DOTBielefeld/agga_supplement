
import sys
import re
import os
import math



class MipWrapper():
    '''
        Simple wrapper for a MIP solver (CPLEX)
    '''


    def get_command_line_args(self, runargs, config):
        config = config.copy()

        instance = runargs["instance"]
        id = runargs["id"]
        seed = runargs["seed"]

        binary = "./input/target_algorithms/CPLEX-22_1_1/cplex/bin/x86-64_linux/cplex"
        instance_p = f'"./input/{instance}"'


        params = []
        if config["simplex_perturbation_switch"] == True:
            simplex_perturbation_value = "yes" + " " + str(config["perturbation_constant"])
        else:
            simplex_perturbation_value = "no" + " 0.00000001"
        params.append("set simplex perturbationlimit %s " % (simplex_perturbation_value))
        try:
            del config["simplex_perturbation_switch"]
            del config["perturbation_constant"]
        except KeyError:
            pass

        for name, value in config.items():
            if value == True:
                value = "yes"
            elif value == False:
                value = "no"
            params.append("set %s %s" % (name.replace("_", " "), value))

        # "set logfile *" disables the log file; important to not fill the disk
        metaparams = [
            "set logfile *",
            "read %s" % instance_p,
            "set clocktype 1",
            "set threads 1",
            "set timelimit 600",
            "set mip limits treememory 3000",
            "set workdir .",
            "set mip tolerances mipgap 0"]
        if seed != -1:
            metaparams.append("set randomseed %d" % seed)

        metaparams.append("change sense obj max")

        metaparams.extend(params)
        metaparams.append("display settings all")
        metaparams.append("opt")
        metaparams.append("quit")
        conf = f"{binary} -c {' '.join(metaparams)}"
        return conf


if __name__ == "__main__":
    wrapper = MipWrapper()
    wrapper.main()
