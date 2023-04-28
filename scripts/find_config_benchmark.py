import os
import time



batch_min = 1
batch_max = 10
batch_step = 2

concurrency_min = 1
concurrency_max = 10
concurrency_step = 2

pairs_concurrency_batch = [] 

# commands
bechmark = "inception_graphdef"
results_dir = "../data/config_settings/"

get_statistics = "../../model/clients/bin/perf_analyzer \
        -m {benchmark} \
        --percentile=99 \
        --measurement-mode count_windows \
        --measurement-request-count 10000 \
        --concurrency-range {concurrency_range} \
        -b {batch_size} \
        -f {output_dir}/perf_analyzer.csv > {output_dir}/perf_analyzer.txt "

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
    os.system(setup)
    pairs_concurrency_batch = find_pairs()

    for pair in pairs_concurrency_batch:
        print(pair)
        output_dirr = os.path.join(results_dir, f"{pair[0]}_{pair[1]}")
        print(output_dirr)
        os.makedirs(output_dirr, exist_ok=True)
        os.system(get_statistics.format(benchmark = bechmark, batch_size = pair[1], concurrency_range = pair[0],  output_dir = output_dirr))


if __name__ == "__main__":
    main()