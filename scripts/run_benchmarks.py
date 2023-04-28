import os
import time

# configs
zone_1 = "1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47"
zone_0 = "0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46"

cpu_min_limit = 35 # uW
cpu_max_limit = 125 # uW (TDP)
cpu_step = 10 # uW

gpu_min_limit = 100 # W
gpu_max_limit = 260 # W (TDP)
gpu_step = 10 # W

total_min_limit = cpu_min_limit + gpu_min_limit
total_max_limit = cpu_max_limit + gpu_max_limit
total_step = 10

cpu_limits = range(cpu_min_limit, cpu_max_limit + 1, cpu_step)
gpu_limits = range(gpu_min_limit, gpu_max_limit + 1, gpu_step)
total_limits = range(total_min_limit, total_max_limit + 1, total_step)

# commands
bechmark = "inception_graphdef"
results_dir = "/home/noa/results_performance/{benchmark}"

get_statistics = "taskset -c {cpus} \
    ./clients/bin/perf_analyzer \
        -m {benchmark} \
        --percentile=90 \
        --measurement-mode count_windows \
        --measurement-request-count 10000 \
        --concurrency-range 64 \
        -f {output_dir}/perf_analyzer.csv > {output_dir}/perf_analyzer.txt \
        -b 16"
# setup = "cd clients/bin"
setup = ""
reset = "./reset_intel.sh"

# cpu in uW
set_cpu_limit = "sudo powercap-set intel-rapl -z 0 -c 0 -l {cpu_limit}"

# gpu in W
set_gpu_limit = "sudo nvidia-smi -i 0 -pl {gpu_limit}"

# find sum of cpu_limit and gpu_limit equal to total
def find_pairs(cpu_limits, gpu_limits, total):
    pairs = []
    for cpu_limit in cpu_limits:
        for gpu_limit in gpu_limits:
            if cpu_limit + gpu_limit == total:
                pairs.append((cpu_limit, gpu_limit))
    return pairs

# main
def main():
    os.system(setup)

    for total in total_limits:
        print("Total: %d" % total)
        pairs = find_pairs(cpu_limits, gpu_limits, total)
        output_total_dir = os.path.join(results_dir.format(benchmark=bechmark), str(total))
        os.makedirs(output_total_dir, exist_ok=True)

        for pair in pairs:
            cpu_limit = pair[0]
            gpu_limit = pair[1]
            print("CPU: %d, GPU: %d" % (cpu_limit, gpu_limit))
            os.system(set_cpu_limit.format(cpu_limit=cpu_limit * 10**6))
            os.system(set_gpu_limit.format(gpu_limit=gpu_limit))

            output_dir = os.path.join(output_total_dir, f"{cpu_limit}_{gpu_limit}")
            os.makedirs(output_dir, exist_ok=True)
            os.system(get_statistics.format(cpus= zone_1, benchmark = bechmark, output_dir = output_dir))
    os.system(reset)


if __name__ == "__main__":
    main()
    print(set_gpu_limit.format(gpu_limit=100))