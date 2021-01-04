import argparse
import csv
import matplotlib.pyplot as plt
import multiprocessing
import os

from collections import Counter

from estimate_transmission_probability import estimate_transmission_probabilities

def get_trans_prob_by_exp(output_dir, scenario_name):
    experiments = {}
    summary_file = os.path.join(output_dir, scenario_name, scenario_name + "_summary.csv")
    with open(summary_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            exp_id = int(row["exp_id"])
            transmission_probability = float(row["transmission_probability"])
            experiments[exp_id] = transmission_probability

    return experiments

def get_secondary_cases_per_index_case(output_dir, scenario_name, experiment_id):
    secondary_cases = {}

    transmissions_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
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

    return (experiment_id, secondary_cases_per_index_case)

def get_index_case_ids(output_dir, scenario_name, experiment_id):
    index_case_ids = []

    transmissions_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    with open(transmissions_file) as f:
        for line in f:
            line = line.split(" ")
            tag = line[0]
            if tag == "[PRIM]":
                index_case_id = int(float(line[1]))
                index_case_ids.append(index_case_id)

    return (experiment_id, index_case_ids)

def get_individual_transmission_probabilities(output_dir, scenario_name, experiment_id):
    tps = {}
    log_file = os.path.join(output_dir, scenario_name, "exp" + "{:04}".format(experiment_id), "event_log.txt")
    with open(log_file) as f:
        for line in f:
            line = line.split(' ')
            tag = line[0]
            if tag == "[PRIM]":
                index_case_id = int(float(line[1]))
                tp = float(line[13])
                tps[index_case_id] = tp
    return tps

def main(output_dir, scenario_names):
    all_means = []
    all_means_no_extinction = []
    all_tps = []
    for scenario in scenario_names:
        experiments = get_trans_prob_by_exp(output_dir, scenario)
        with multiprocessing.Pool(processes=4) as pool:
            secondary_cases = pool.starmap(get_secondary_cases_per_index_case,
                                        [(output_dir, scenario, exp_id) for exp_id in experiments.keys()])
            index_case_ids = pool.starmap(get_index_case_ids,
                                        [(output_dir, scenario, exp_id) for exp_id in experiments.keys()])
            individual_transmission_probabilities = pool.starmap(get_individual_transmission_probabilities,
                                        [(output_dir, scenario, exp_id) for exp_id in experiments.keys()])


            # Group by transmission_probability
            secondary_cases_by_tp = {}
            for experiment_id, cases in secondary_cases:
                tp = experiments[experiment_id]
                if tp in secondary_cases_by_tp:
                    secondary_cases_by_tp[tp].append(cases)
                else:
                    secondary_cases_by_tp[tp] = [cases]
            tps = list(secondary_cases_by_tp.keys())
            tps.sort()
            all_tps.append(tps)


            '''population_file = os.path.join(output_dir, "..", "data", "pop_belgium3000k_c500_teachers_censushh.csv")
            contact_matrix_file = os.path.join(output_dir, "..", "data", "contact_matrix_flanders_conditional_teachers.xml")
            infectious_period_lengths = [6]
            theoretical_contacts = estimate_transmission_probabilities(population_file,
                                                                    contact_matrix_file,
                                                                    infectious_period_lengths,
                                                                    tps,
                                                                    person_ids=[person_id[1][0] for person_id in index_case_ids],
                                                                    get_mean=False, contacts_only=True)
            print(theoretical_contacts)
            for i in range(len(index_case_ids)):
                index_case_id = index_case_ids[i][1][0]
                print(index_case_id)
                #print(individual_transmission_probabilities[i])
                #print("Q = {}, CR/d = {}".format(individual_transmission_probabilities[index_case_ids[i][1][0]], theoretical_contacts[i]))'''

            secondary_cases_by_tp_no_extinction = {}
            for tp in tps:
                secondary_cases_by_tp_no_extinction[tp] = [cases for cases in secondary_cases_by_tp[tp] if cases > 0]

            means_no_extinction = [sum(secondary_cases_by_tp_no_extinction[tp]) / len(secondary_cases_by_tp_no_extinction[tp]) if len(secondary_cases_by_tp_no_extinction[tp]) > 0 else 0 for tp in tps]
            all_means_no_extinction.append(means_no_extinction)

            means = [sum(secondary_cases_by_tp[tp]) / len(secondary_cases_by_tp[tp]) for tp in tps]
            all_means.append(means)

            for tp in tps:
                sc = secondary_cases_by_tp[tp]
                ms = []
                for i in range(len(sc)):
                    sc_selection = sc[len(sc) - 1 - i:]
                    m = sum(sc_selection) / len(sc_selection)
                    ms.append(m)
                plt.plot(range(len(sc)), ms)
            plt.legend(tps)
            plt.xlabel("Number of simulations")
            plt.xlim(0, 1000)
            plt.ylabel("Mean # of secondary cases of index case")
            plt.title(scenario)
            plt.show()

            #plt.boxplot([secondary_cases_by_tp[tp] for tp in tps], labels=tps)
            ''''plt.violinplot([secondary_cases_by_tp[tp] for tp in tps], showmeans=True)
            plt.xlabel("Transmission probability")
            plt.xticks(range(1, len(tps) + 1),tps)
            plt.ylabel("Secondary cases per index case")
            plt.ylim(0, 165)
            plt.title(scenario)
            plt.show()'''

    for i in range(len(all_means)):
        plt.plot(all_tps[i], all_means_no_extinction[i])

    #plt.plot(all_tps[i], theoretical)
    plt.xlabel("Transmission probability")
    plt.xticks(all_tps[0])
    plt.ylabel("Mean # of secondary cases per index case")
    plt.legend(scenario_names)
    plt.title("Without extinction cases")
    plt.show()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("scenario_names", type=str, nargs="+")

    args = parser.parse_args()
    main(args.output_dir, args.scenario_names)
