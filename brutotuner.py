#!/usr/bin/python3
# Auto-tuner prototype
# Built for INE5540 robot overlords

import subprocess # to run stuff
import sys # for args, in case you want them
import time # for time
import itertools
import os
from functools import reduce

def tuner(options, input_size, num_trials):
    exec_file = "matmult"
    compilation_line = ["gcc","-o",exec_file,"mm.c"]

    best_runtime = float("inf")
    best_combination = None

    devnull = open(os.devnull, "w")

    all_combinations = list(itertools.product(*options))
    for i, combination in enumerate(all_combinations):
        combination = list(combination)
        combination[0] = "-DSTEP=%d" % combination[0]
        filtered_combination = list(filter(None, combination))

        # Compile code
        compilation_try = subprocess.run(compilation_line + filtered_combination)
        if (compilation_try.returncode == 0):
            print("Compilation #%d/%d: %s" % (i + 1, len(all_combinations), filtered_combination))
        else:
            print("Sad compilation")

        times = []
        for trial in range(num_trials):
            # Run code
            t_begin = time.time() # timed run
            run_trial = subprocess.run(["./"+exec_file, input_size], stdout=devnull)
            t_end = time.time()
            if run_trial.returncode != 0:
                print("Sad execution")
                break
            times.append(t_end - t_begin)

        # print("Happy execution in "+str(t_end-t_begin))
        elapsed_time = reduce(lambda x, y: x + y, times) / len(times)
        if elapsed_time < best_runtime:
            best_runtime = elapsed_time
            best_combination = combination

    print("Compilation completed. Best combination: %s" % list(filter(None, best_combination)))
    devnull.close()

if __name__ == "__main__":
    options = [
        [8, 16, 32, 64], # possible step values
        ["-funroll-loops", "-funroll-all-loops", ""],
        ["-march=native", ""],
        ["-mfpmath=sse", ""],
        ["-O3", "-Ofast", "-O2"],
    ]

    if len(sys.argv) > 1:
        input_size = sys.argv[1]
    else:
        input_size = "8"

    tuner(options, input_size, 30) # go auto-tuner
