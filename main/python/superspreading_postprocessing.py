import argparse
import collections
import csv
import matplotlib.pyplot as plt
import multiprocessing
import os

def get_experiment_ids(output_dir, scenario_name):
    experiment_ids = []
    summary_file = os.path.join(output_dir, scenario_name, scenario_name + "_summary.csv")
    with open(summary_file) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            exp_id = int(row["exp_id"])
            experiment_ids.append(exp_id)
    return experiment_ids

def get_effective_r(output_dir, scenario_name, experiment_id):
    log_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    potential_infectors = {}
    with open(log_file) as f:
        for line in f:
            line = line.split(" ")
            tag = line[0]
            if tag == "[PRIM]":
                infected_id = int(float(line[1]))
                if infected_id not in potential_infectors:
                    potential_infectors[infected_id] = 0
            elif tag == "[TRAN]":
                infector_id = int(float(line[2]))
                infected_id = int(float(line[1]))
                # Add infected to potential infectors
                if infected_id not in potential_infectors:
                    potential_infectors[infected_id] = 0
                # Add infector to infectors (if not yet done)
                # And add this infection to total secondary cases count
                if infector_id not in potential_infectors:
                    potential_infectors[infector_id] = 1
                else:
                    potential_infectors[infector_id] += 1
    return potential_infectors


def main(output_dir, scenario_names):
    for scenario in scenario_names:
        print(scenario)
        exp_ids = get_experiment_ids(output_dir, scenario)
        with multiprocessing.Pool(processes=4) as pool:
            effective_rs = pool.starmap(get_effective_r, [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            for result in effective_rs:
                total_infections = sum(result.values())
                secondary_cases = result.values()
                counter = collections.Counter(secondary_cases)
                if total_infections > 0:
                    for key in counter:
                        counter[key] = (counter[key] / total_infections) * 100
                keys_sorted = list(counter.keys())
                keys_sorted.sort()

                plt.plot(keys_sorted, [counter[x] for x in keys_sorted], "o")
            plt.xlabel("Number of secondary cases")
            plt.xlim(-2, 65)
            plt.ylabel("Percentage of infected individuals")
            plt.ylim(-2, 102)
            plt.show()
            total_infections = [sum(x.values()) for x in effective_rs]
            #plt.hist(total_infections)
            #plt.show()
            #for result in effective_rs:
                ##total_infections = sum(result.values())
                #print(total_infections)
                #plt.hist([x / len(result) for x in result.values()])
                #plt.title(scenario)
                #plt.show()
                #mean_er = sum(list(result.values())) / len(list(result.values))
                #print(mean_er)
        # TODO effective R?
        # TODO distribution of individual R0?
        # TODO outbreak size? outbreak frequency?

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("scenario_names", type=str, nargs="+")
    args = parser.parse_args()
    main(args.output_dir, args.scenario_names)
