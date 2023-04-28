
import os
import csv
import matplotlib.pyplot as plt
# import oapackage


# configs
cpu_set = "0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46"
gpu_set = "0"

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
graph_dir = "/home/noa/graph_performance/{benchmark}"
data_dir = "/home/noa/results_performance/{benchmark}"

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
    x_cpu_gpu_total = []
    y_latency = []
    y_throughput = []
    total_power_latency =[]
    total_power_throughput = []

    os.makedirs(graph_dir.format(benchmark = bechmark), exist_ok=True)
    
    for total in total_limits:
        if total >= 225:
            continue
        print("Total: %d" % total)
        pairs = find_pairs(cpu_limits, gpu_limits, total)

        # get the dir for the data we want to parse
        data_total_dir = os.path.join(data_dir.format(benchmark=bechmark), str(total))

        # add total to x
        x_cpu_gpu_total.append(total)

        max_throughput = 0
        min_latency = 1000000000000000

        # data for the graph of pairs
        throuput_pair = []
        latency_pair = []
        cpu_power = []


        latency = 0
        throughput = 0

        for pair in pairs:
            cpu_limit = pair[0]
            gpu_limit = pair[1]
            print("CPU: %d, GPU: %d" % (cpu_limit, gpu_limit))
 
            # to get csv data
            data_abs_dir = os.path.join(data_total_dir, f"{cpu_limit}_{gpu_limit}")
            data_abs_path = os.path.join(data_abs_dir, "perf_analyzer.csv")
            path_latency_graph = os.path.join(data_total_dir, "powerVsLatency.png")
            path_throughput_graph = os.path.join(data_total_dir, "powerVsThroughput.png")

            with open(data_abs_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    latency = float(row["p99 latency"])
                    throughput = float(row["Inferences/Second"])
            total_power_latency.append([total, latency])
            total_power_throughput.append([total, throughput])
                
            # cpu power
            cpu_power.append(cpu_limit)

            # avg latency
            min_latency = min(min_latency, latency)
            latency_pair.append(latency)


            # total throughput
            max_throughput = max(max_throughput, throughput)
            throuput_pair.append(throughput)

        #plot latency
        plt.clf()
        plt.plot(cpu_power, latency_pair)
        plt.title(f"Total power limit {total}: CPU Power Limit vs. P99 Latency")
        plt.xlabel("Power (uW)")
        plt.ylabel("Latency (usec)")
        plt.savefig(path_latency_graph)

        #plot throughput
        plt.clf()
        plt.plot(cpu_power, throuput_pair)
        plt.title(f"Total power limit {total}: CPU Power Limit vs. P99 Latency")
        plt.xlabel("Power (uW)")
        plt.ylabel("Inferences/Second")
        plt.savefig(path_throughput_graph)
    
        y_latency.append(min_latency)
        print("min latency")
        print(min_latency)
        y_throughput.append(max_throughput)

    # # # plot paretto-optimality curves
    paretto_optimality_latency_path = os.path.join(data_dir.format(benchmark=bechmark), "ParettoOptimalityLatency.png")
    paretto_optimality_throughput_path = os.path.join(data_dir.format(benchmark=bechmark), "ParettoOptimalityThroughput.png")
    # pareto = oapackage.ParetoDoubleLong()

    # for ii in range(0, len(total_power_latency) - 1):  
    #     print(ii)  
    #     w=oapackage.doubleVector((total_power_latency[ii][0], total_power_latency[ii][1]))
    #     pareto.addvalue(w, ii)

    # pareto.show(verbose=1)

    # lst = pareto.allindices() # the indices of the Pareto optimal designs

    # # print(lst)
    # # optimal_datapoints = total_power_latency[lst]
    # optimal_datapoints = [total_power_latency[i] for i in lst]

    # x = []
    # y = []
    # for i in range(0, len(optimal_datapoints) - 1):
    #     x.append(optimal_datapoints[i][0])
    #     y.append(optimal_datapoints[i][1])

    # plt.clf()
    # plt.title(f"Total Power Limit vs. Latency")
    # hp=plt.plot(x_cpu_gpu_total, y_latency, '.b', markersize=16, label='Non-Pareto optimal')
    # hp=plt.plot(x, y, '.r', markersize=16, label='Pareto optimal')
    # plt.xlabel('Power (W)', fontsize=16)
    # plt.ylabel('Latency (usec)', fontsize=16)
    # plt.xticks([])
    # plt.yticks([])
    # _=plt.legend(loc=3, numpoints=1)
    # plt.savefig(paretto_optimality_latency_path)

    # # throughput paretto optimality
    # pareto=oapackage.ParetoDoubleLong()

    # for ii in range(0, len(total_power_throughput) - 1):  
    #     print(ii)  
    #     w=oapackage.doubleVector((total_power_throughput[ii][0], total_power_throughput[ii][1]))
    #     pareto.addvalue(w, ii)

    # pareto.show(verbose=1)

    # lst = pareto.allindices() # the indices of the Pareto optimal designs

    # # print(lst)
    # # optimal_datapoints = total_power_latency[lst]
    # optimal_datapoints = [total_power_throughput[i] for i in lst]

    # x = []
    # y = []
    # for i in range(0, len(optimal_datapoints) - 1):
    #     x.append(optimal_datapoints[i][0])
    #     y.append(optimal_datapoints[i][1])
        
    # plt.clf()
    # plt.title(f"Total Power Limit vs. Throughput")
    # hp=plt.plot(x_cpu_gpu_total, y_throughput, '.b', markersize=16, label='Non-Pareto optimal')
    # hp=plt.plot(x, y, '.r', markersize=16, label='Pareto optimal')
    # plt.xlabel('Power (W)', fontsize=16)
    # plt.ylabel('Throughput (Inferences / Second)', fontsize=16)
    # plt.xticks([])
    # plt.yticks([])
    # _=plt.legend(loc=3, numpoints=1)
    # plt.savefig(paretto_optimality_throughput_path)

    plt.clf()
    plt.plot(total_limits[:9], y_latency)
    print(y_latency)
    plt.title(f"Total Power Limit vs. Latency")
    plt.xlabel("Power (uW)")
    plt.ylabel("Latency (usec)")
    # plt.ylim([0.99, 1.01])
    plt.savefig(paretto_optimality_latency_path)
    
    plt.clf()
    plt.plot(total_limits[:9], y_throughput)
    print(y_throughput)
    plt.title(f"Total Power Limit vs. Throughput")
    plt.xlabel("Power (uW)")
    plt.ylabel("Throughput (Inferences/Second)")
    plt.savefig(paretto_optimality_throughput_path)

if __name__ == "__main__":
    main()
    print(set_gpu_limit.format(gpu_limit=100))

    # htop shows cpu core utilization
    # tmux
    # tmux ls
    # tmux attatch -t 0
