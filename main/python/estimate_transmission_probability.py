import argparse
import csv
import numpy
import random
import xml.etree.ElementTree as ET

def get_contact_rates(pooltype, contact_rate_tree, maxAge):
    # Create matrix of zeroes
    contact_rates = []
    for age in range(maxAge + 1):
        contact_rates.append([0] * (maxAge + 1))
        #contact_rates.append(0)

    # Get contact rates for the right pooltype from xml tree
    max_participant_age = 0
    pooltype_contacts = contact_rate_tree.find(pooltype)
    '''# FIXME This is for aggregated contacts by age (participants -> contacts -> contact -> age = all)
    for participant in pooltype_contacts.findall("participant"):
        participant_age = int(participant.find("age").text)
        if (participant_age > max_participant_age):
            max_participant_age = participant_age
        contact_rate = float(participant.find("contacts/contact/rate").text)
        contact_rates[participant_age] = contact_rate'''

    # Get contact rates for the right pooltype from xml tree
    max_participant_age = 0
    pooltype_contacts = contact_rate_tree.find(pooltype)
    for participant in pooltype_contacts.findall("participant"):
        age1 = int(participant.find("age").text)
        if (age1 > max_participant_age):
            max_participant_age = age1
        contacts = participant.find("contacts")
        for contact in contacts.findall("contact"):
            age2 = int(contact.find("age").text)
            contact_rate = float(contact.find("rate").text)
            contact_rates[age1][age2] = contact_rate

    '''# Fill in contact rates for ages > max_participant_age
    # Set contact_rate[age] = contact_rate[max_participant_age] if age > max_participant_age
    for age in range(max_participant_age + 1, maxAge + 1):
        contact_rates[age] = contact_rates[max_participant_age]'''

    # Fill in contact rates for ages > max_participant_age
    # Set contact rage [age1, age2] = [max_participant_age, age2] if age2 <= max_participant_age
    # Else [age1, age2] = [max_participant_age, max_participant_age]
    for age1 in range(max_participant_age + 1, maxAge + 1):
        for age2 in range(maxAge + 1):
            if age2 <= max_participant_age:
                contact_rates[age1][age2] = contact_rates[max_participant_age][age2]
                contact_rates[age2][age1] = contact_rates[age2][max_participant_age]
            else:
                contact_rates[age1][age2] = contact_rates[max_participant_age][max_participant_age]
                contact_rates[age2][age1] = contact_rates[max_participant_age][max_participant_age]

    return contact_rates

def add_to_pool(pools, pool_id, person_id, age):
    if pool_id > 0:
        if pool_id in pools:
            pools[pool_id].append((person_id, age))
        else:
            pools[pool_id] = [(person_id, age)]

def get_effective_contacts(person_id, age, pools, pooltype, pool_id, contact_rates,
    infectious_period_lengths, transmission_probability):
    effective_contacts = 0

    # Iterate over pool members
    if pool_id > 0:
        pool_members = pools[pool_id]
        pool_size = len(pool_members)
        for infectious_period in infectious_period_lengths:
            for member in pool_members:
                member_id = member[0]
                member_age = member[1]
                if member_id != person_id: # Check that this is not the same person
                    contact_rate = contact_rates[pooltype][age][member_age]
                    of_same_age_in_pool = sum([1 for x in pool_members if x[1] == member_age])
                    contact_probability = contact_rate / of_same_age_in_pool
                    # FIXME This is for aggregated contacts by age (participants -> contacts -> contact -> age = all)
                    #contact_rate1 = contact_rates[pooltype][age]
                    #contact_rate2 = contact_rates[pooltype][member_age]
                    #contact_probability = min(contact_rate1, contact_rate2) / pool_size
                    # Households are assumed to be fully connected in Stride
                    if pooltype == "household":
                        contact_probability = 0.999
                        #contact_probability = 1
                    if contact_probability >= 1:
                        contact_probability = 0.999
                    effective_contacts += 1 - ((1 - (transmission_probability * contact_probability))**infectious_period)
    # Assuming uniform distribution of infectious period lengths
    effective_contacts /= len(infectious_period_lengths)
    return effective_contacts

def main(population_file, contact_matrix_file, infectious_period_lengths, transmission_probabilities):
    maxAge = 111

    ############################################################################
    # Read contact matrices from file                                          #
    ############################################################################

    contact_rates = {
        "household": [],
        "workplace": [],
        "school": [],
        "primary_community": [],
        "secondary_community": []
    }

    # Parse xml file
    contact_matrix_tree = ET.parse(contact_matrix_file).getroot()
    contact_rates["household"] = get_contact_rates("household", contact_matrix_tree, maxAge)
    contact_rates["workplace"] = get_contact_rates("work", contact_matrix_tree, maxAge)
    contact_rates["school"] = get_contact_rates("school", contact_matrix_tree, maxAge)
    contact_rates["primary_community"] = get_contact_rates("primary_community", contact_matrix_tree, maxAge)
    contact_rates["secondary_community"] = get_contact_rates("secondary_community", contact_matrix_tree, maxAge)

    ############################################################################
    # From population file, get age constitutions                              #
    # and sizes of different contact pools                                     #
    ############################################################################

    households = {}
    workplaces = {}
    schools = {}
    primary_communities = {}
    secondary_communities = {}

    population = []
    person_id = 1

    with open(population_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            age = int(row["age"])
            # Keep track of pool constitutions
            add_to_pool(households, int(float(row["household_id"])), person_id, age)
            add_to_pool(workplaces, int(float(row["work_id"])), person_id, age)
            add_to_pool(schools, int(float(row["school_id"])), person_id, age)
            add_to_pool(primary_communities, int(float(row["primary_community"])), person_id, age)
            add_to_pool(secondary_communities, int(float(row["secondary_community"])), person_id, age)
            # Add person to population list
            population.append({"id": person_id, "age": age,
                                "household_id": int(float(row["household_id"])),
                                "work_id": int(float(row["work_id"])),
                                "school_id": int(float(row["school_id"])),
                                "primary_community_id": int(float(row["primary_community"])),
                                "secondary_community_id": int(float(row["secondary_community"]))})
            person_id += 1

    ############################################################################
    # For each transmission probability to be tested:                          #
    # iterate over all persons in the population,                              #
    # and calculate the number of secondary cases they would cause             #
    # if infected in a completely susceptible population                       #
    # (cfr. theoretical description by A. Torneri)                             #
    ############################################################################
    for tp in transmission_probabilities:
        all_effective_contacts = []
        for person in random.choices(population, k=100):
            # Get # of effective contacts in each of the contact pools
            # to which this person belongs
            hh_effective_contacts = get_effective_contacts(person["id"], person["age"],
                                                            households, "household", person["household_id"],
                                                            contact_rates, infectious_period_lengths, tp)
            work_effective_contacts = get_effective_contacts(person["id"], person["age"],
                                                            workplaces, "workplace", person["work_id"],
                                                            contact_rates, infectious_period_lengths, tp)
            school_effective_contacts = get_effective_contacts(person["id"], person["age"],
                                                            schools, "school", person["school_id"],
                                                            contact_rates, infectious_period_lengths, tp)
            primary_community_effective_contacts = get_effective_contacts(person["id"], person["age"],
                                                            primary_communities, "primary_community", person["primary_community_id"],
                                                            contact_rates, infectious_period_lengths, tp)
            secondary_community_effective_contacts = get_effective_contacts(person["id"], person["age"],
                                                            secondary_communities, "secondary_community", person["secondary_community_id"],
                                                            contact_rates, infectious_period_lengths, tp)

            total_effective_contacts = hh_effective_contacts + work_effective_contacts + school_effective_contacts + primary_community_effective_contacts + secondary_community_effective_contacts
            all_effective_contacts.append(total_effective_contacts)

        mean_effective_contacts = sum(all_effective_contacts) / len(all_effective_contacts)
        print("Transmission probability {}: {} effective contacts on average".format(tp, mean_effective_contacts))

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("population_file", type=str)
    parser.add_argument("contact_matrix_file", type=str)
    parser.add_argument("--infectious_period_lengths", type=int, nargs="+", default=[6,7,8,9], help="Mean length of infectious period (in days)")
    parser.add_argument("--transmission_probabilities", type=float, nargs="+", default=[0.02, 0.04, 0.06, 0.08, 0.10])
    args = parser.parse_args()
    main(args.population_file, args.contact_matrix_file, args.infectious_period_lengths, args.transmission_probabilities)
