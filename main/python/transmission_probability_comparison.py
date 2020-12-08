import argparse
import csv
import matplotlib.pyplot as plt
import os

from estimate_transmission_probability import estimate_transmission_probabilities

def main(output_dir, scenario_name):
    # Get transmission probability per experiment
    experiments = {}
    summary_file = os.path.join(output_dir, scenario_name, scenario_name + "_summary.csv")
    with open(summary_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            exp_id = int(row["exp_id"])
            transmission_probability = float(row["transmission_probability"])
            experiments[exp_id] = transmission_probability

    # Get number of secondary cases caused by index case for each experiment
    secondary_cases_by_tp = {}
    for exp_id in experiments:
        print(exp_id)
        # Get transmission probability used
        tp = experiments[exp_id]
        # Get secondary cases of index case
        secondary_cases = {}
        transmissions_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(exp_id), "event_log.txt")
        with open(transmissions_file) as f:
            for line in f:
                line = line.split(" ")
                tag = line[0]
                if tag == "[PRIM]":
                    index_case_id = int(float(line[1]))
                    secondary_cases[index_case_id] = 0
                elif tag == "[TRAN]":
                    infector_id = int(float(line[2]))
                    if infector_id in secondary_cases:
                        secondary_cases[infector_id] += 1
                    else:
                        secondary_cases[infector_id] = 1

        if len(secondary_cases) > 1:
            print("WARNING: more than 1 index case")
        secondary_cases_per_index_case = sum(secondary_cases.values()) / len(secondary_cases)
        if tp in secondary_cases_by_tp:
            secondary_cases_by_tp[tp].append(secondary_cases_per_index_case)
        else:
            secondary_cases_by_tp[tp] = [secondary_cases_per_index_case]


    tps = list(secondary_cases_by_tp.keys())
    tps.sort()
    # Get mean r0 per transmission probability
    means = [sum(secondary_cases_by_tp[x]) / len(secondary_cases_by_tp[x]) for x in tps]

    # Get theoretical estimations
    print("Get theoretical estimation")
    population_file = os.path.join(output_dir, "..", "data", "pop_belgium3000k_c500_teachers_censushh.csv")
    contact_matrix_file = os.path.join(output_dir, "..", "data", "contact_matrix_flanders_conditional_teachers.xml")
    infectious_period_lengths = [6]
    #theoretical = estimate_transmission_probabilities(population_file, contact_matrix_file, infectious_period_lengths, tps)
    theoretical = {0.0: 0.0, 0.05: 7.930116415278281, 0.1: 15.442670627333122, 0.15: 22.60643305937693, 0.2: 29.480250412965912}
    print("Plot")
    theor_plot, = plt.plot(tps, [theoretical[x] for x in tps], color="orange")
    sim_plot, = plt.plot(tps, means, color="blue")
    for tp in secondary_cases_by_tp:
        plt.plot([tp] * len(secondary_cases_by_tp[tp]), secondary_cases_by_tp[tp], "bo")
    plt.legend([sim_plot, theor_plot], ["Simulations", "Theoretical"])
    plt.xlabel("Transmission probability")
    plt.ylabel("Secondary cases from index case")
    plt.xticks(tps)
    #plt.boxplot([secondary_cases_by_tp[tp] for tp in tps], labels=tps)
    #theor_plot, = plt.plot(range(1, len(tps) + 1), [theoretical[x] for x in tps], "ro")
    #plt.legend([theor_plot],["Theoretical description"])
    plt.show()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("scenario_name", type=str)

    args = parser.parse_args()
    main(args.output_dir, args.scenario_name)
