import argparse
import collections
import csv
import matplotlib.pyplot as plt
import multiprocessing
import os

from collections import Counter

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
    plt.hist(all_outbreak_sizes)
    plt.xlabel("Outbreak size")
    plt.ylabel("Frequency")
    plt.legend(scenario_names)
    plt.show()

'''
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


labels = ['G1', 'G2', 'G3', 'G4', 'G5']
men_means = [20, 34, 30, 35, 27]
women_means = [25, 32, 34, 20, 25]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, men_means, width, label='Men')
rects2 = ax.bar(x + width/2, women_means, width, label='Women')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Scores')
ax.set_title('Scores by group and gender')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

plt.show()
'''

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

def get_new_cases_per_day(output_dir, scenario_name, experiment_id):
    summary_file = os.path.join(output_dir, scenario_name, scenario_name + "_summary.csv")
    num_days = 0
    with open(summary_file) as csvfile:
        reader = csv.DictReader(csvfile)
        num_days = int(next(reader)["num_days"])
    log_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    days = {}
    for day in range(num_days):
        days[day] = 0
    with open(log_file) as f:
        for line in f:
            line = line.split(' ')
            tag = line[0]
            if tag == "[TRAN]":
                sim_day = int(line[6])
                days[sim_day] += 1
    return days

def get_effective_r_on_day(output_dir, scenario_name, experiment_id, sim_day):
    # Get max number of days
    summary_file = os.path.join(output_dir, scenario_name, scenario_name + "_summary.csv")
    num_days = 0
    with open(summary_file) as csvfile:
        reader = csv.DictReader(csvfile)
        num_days = int(next(reader)["num_days"])
    if sim_day >= num_days:
        print("Sim day out of range")
        return -1

    # Get infectors on day sim_day
    log_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    infector_on_day_ids = []
    with open(log_file) as f:
        for line in f:
            line = line.split(" ")
            tag = line[0]
            if tag == "[TRAN]":
                day = int(line[6])
                if day == sim_day:
                    infector_id = int(float(line[2]))
                    infector_on_day_ids.append(infector_id)

    # Remove duplicates
    infector_on_day_ids = list(set(infector_on_day_ids))
    # TODO get all secondary cases of infectors
    all_secondary_cases = get_secondary_cases_by_individual(output_dir, scenario_name, experiment_id)
    effective_r_day = []
    for infector_id in infector_on_day_ids:
        effective_r_day.append(all_secondary_cases[infector_id])
    if len(effective_r_day) > 0:
        mean_er = sum(effective_r_day) / len(effective_r_day)
    else:
        mean_er = 0
    return mean_er



def main(output_dir, scenario_names):
    all_secondary_cases = {}
    all_means_no_extinction = {}
    all_effective_rs_60 = []
    for scenario in scenario_names:
        print(scenario)
        exp_ids = get_experiment_ids(output_dir, scenario)
        with multiprocessing.Pool(processes=4) as pool:
            effective_r_d_60 = pool.starmap(get_effective_r_on_day,
                                            [(output_dir, scenario, exp_id, 60) for exp_id in exp_ids])
            all_effective_rs_60.append([x for x in effective_r_d_60 if x > 0])
            #secondary_cases = pool.starmap(get_secondary_cases_by_individual,
            #                                [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            #total_cases = [sum(x.values()) for x in secondary_cases]
            #counter = Counter(total_cases)
            #keys = list(counter.keys())
            #keys.sort()
            #print(["{}: {}".format(x, counter[x]) for x in keys])
            #all_secondary_cases[scenario] = secondary_cases
            #plot_secondary_cases_frequency(scenario, secondary_cases)
            #new_cases_by_day = pool.starmap(get_new_cases_per_day,
            #                                [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            #for run in new_cases_by_day:
            #    num_days = max(run.keys())
            #    plt.plot(range(num_days), [run[x] for x in range(num_days)])
            #plt.xlabel("Simulation day")
            #plt.ylabel("New infections")
            #plt.ylim(0, 180000)
            #plt.title(scenario)
            #plt.show()
            #individual_transmission_probabilities = pool.starmap(get_individual_transmission_probabilities,
            #                                [(output_dir, scenario, exp_id) for exp_id in exp_ids])
            #means = [sum(x) / len(x) for x in individual_transmission_probabilities]
            #print(sum(means) / len(means))
            #means_no_extinction = [sum(x) / len(x) for x in individual_transmission_probabilities if len(x) > 15]
            #all_means_no_extinction[scenario] = means_no_extinction
            #print(sum(means_no_extinction) / len(means_no_extinction))
            #plt.hist(run)
            #    plt.title(scenario)
            #    plt.show()

    #plot_outbreak_size_frequency(all_secondary_cases)
    plt.boxplot(all_effective_rs_60, labels=scenario_names)
    plt.ylabel("ER day 60")
    plt.yticks(range(0, 11))
    plt.ylim(0, 10.5)
    plt.xticks(rotation=35)
    plt.tight_layout()
    plt.show()
    '''plt.boxplot([all_means_no_extinction[name] for name in scenario_names], labels=scenario_names)
    plt.xticks(rotation=35)
    plt.ylabel("Mean individual transmission probability per run")
    plt.ylim(0.05, 0.1)
    plt.tight_layout()
    plt.show()'''

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("scenario_names", type=str, nargs="+")
    args = parser.parse_args()
    main(args.output_dir, args.scenario_names)
