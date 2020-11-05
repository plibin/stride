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

def get_secondary_cases_by_individual(output_dir, scenario_name, experiment_id):
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

def plot_secondary_cases_frequency(scenario_name, all_secondary_cases):
    for sim_run in all_secondary_cases:
        secondary_cases = sim_run.values()
        total_infections = sum(secondary_cases)
        # Count frequencies of number of secondary cases / person
        counter = collections.Counter(secondary_cases)
        # Scale frequencies to percentage of total infected cases
        if total_infections > 0:
            for num_secondary_cases in counter:
                counter[num_secondary_cases] = (counter[num_secondary_cases] / total_infections) * 100
        num_secondary_cases_sorted = list(counter.keys())
        num_secondary_cases_sorted.sort()
        # Plot results for this simulation run
        plt.plot(num_secondary_cases_sorted, [counter[x] for x in num_secondary_cases_sorted], "o")
    plt.xlabel("Number of secondary cases")
    plt.xlim(-2, 85)
    plt.ylabel("Percentage of infected individuals")
    plt.ylim(-2, 105)
    plt.title(scenario_name)
    plt.show()

def plot_outbreak_size_frequency(all_secondary_cases_by_scenario):
    scenario_names = []
    all_outbreak_sizes = []
    for scenario in all_secondary_cases_by_scenario:
        scenario_names.append(scenario)
        all_outbreak_sizes.append([sum(x.values()) for x in all_secondary_cases_by_scenario[scenario]])
    plt.hist(all_outbreak_sizes, histtype="barstacked")
    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.legend(scenario_names)
    plt.show()

def get_individual_transmission_probabilities(output_dir, scenario_name, experiment_id):
    tps = []
    log_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    with open(log_file) as f:
        for line in f:
            line = line.split(' ')
            tag = line[0]
            if tag == "[PRIM]":
                tp = float(line[13])
                tps.append(tp)
            elif tag == "[TRAN]":
                tp = float(line[13])
                tps.append(tp)
    return tps

def main(output_dir, scenario_names):
    all_secondary_cases = {}
    for scenario in scenario_names:
        exp_ids = get_experiment_ids(output_dir, scenario)
        with multiprocessing.Pool(processes=4) as pool:
            secondary_cases = pool.starmap(get_secondary_cases_by_individual,
                                            [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            all_secondary_cases[scenario] = secondary_cases
            plot_secondary_cases_frequency(scenario, secondary_cases)
            #individual_transmission_probabilities = pool.starmap(get_individual_transmission_probabilities,
            #                                [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            #for run in individual_transmission_probabilities:
            #   plt.hist(run)
            #    plt.title(scenario)
            #    plt.show()

    plot_outbreak_size_frequency(all_secondary_cases)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("scenario_names", type=str, nargs="+")
    args = parser.parse_args()
    main(args.output_dir, args.scenario_names)
