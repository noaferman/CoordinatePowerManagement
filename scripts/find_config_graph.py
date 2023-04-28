
import os
import csv
import matplotlib.pyplot as plt
# import oapackage

batch_min = 1
batch_max = 10
batch_step = 2

concurrency_min = 1
concurrency_max = 10
concurrency_step = 2

pairs_concurrency_batch = [] 

# commands
bechmark = "inception_graphdef"
results_dir = "../data/config_settings"
setup = "./reset_intel.sh"

# find sum of cpu_limit and gpu_limit equal to total
def find_pairs():
    pairs = []
    for concurrency_limit in range(concurrency_min, concurrency_max, concurrency_step):
        for batch_limit in range(batch_min, batch_max, batch_step):
           pairs.append([concurrency_limit, batch_limit])
    return pairs


# main
def main():
    pairs_concurrency_batch = find_pairs()

    latency = []
    title = []

   
    for pair in pairs_concurrency_batch:
        title.append(str(pair))
        data_abs_dir = os.path.join(results_dir, f"{pair[0]}_{pair[1]}")
        data_abs_path = os.path.join(data_abs_dir, "perf_analyzer.csv")

        with open(data_abs_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                latency.append(float(row["p99 latency"]))
    
    sorted_latency, sorted_title = zip(*sorted(zip(latency, title)))
    plt.barh(range(len(sorted_title)), sorted_latency)
    plt.yticks(range(len(sorted_title)), sorted_title)
    plt.autoscale(axis='x')
    plt.title("latency with [concurrency #, batch #] configuration settings")
    plt.xlabel("latency (uSec)")
    plt.xlabel("[concurrency #, batch #]")

    print("show")
    plt.savefig("data.png")
            

if __name__ == "__main__":
    main()