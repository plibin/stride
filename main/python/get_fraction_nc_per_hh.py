import argparse
import csv
import os
import xml.etree.ElementTree as ET

def main(population_dir, population_name, use_pct_of_exprob):
    # Get proportion of non-compliers per NIS code
    nc_by_nis = {}
    with open("WAVE6_nc_by_nis.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nc_by_nis[int(row["nis_code"])] = float(row["fraction_non_compliers"])

    # Match NIS codes to district IDs in the simulator population
    nc_by_district = {}
    with open(os.path.join(population_dir, population_name + "_all", population_name + "_district_data.csv")) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            district_nis_code = int(row["city"])
            if district_nis_code in nc_by_nis:
                nc = nc_by_nis[district_nis_code]
            else:
                nc = 0
            district_id = int(row["id"])
            nc_by_district[district_id] = nc


    # Match households to districts
    households_by_district = {}
    with open(os.path.join(population_dir, population_name + "_all", population_name + "_household_data.csv")) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            district_id = int(row["district_id"])
            hh_id = int(row["hh_id"])
            if district_id in households_by_district:
                households_by_district[district_id].append(hh_id)
            else:
                households_by_district[district_id] = [hh_id]

    # Write to file
    root = ET.Element("hotspots")
    for district_id in households_by_district:
        new_district = ET.SubElement(root, "district")
        new_district_id = ET.SubElement(new_district, "id")
        new_district_id.text = str(district_id)
        new_district_fraction_nc = ET.SubElement(new_district, "fraction_non_compliers")
        new_district_fraction_nc.text = str(nc_by_district[district_id])
        new_households = ET.SubElement(new_district, "households")
        for hh_id in households_by_district[district_id]:
            new_hh_id = ET.SubElement(new_households, "hh_id")
            new_hh_id.text = str(hh_id)

    ET.ElementTree(root).write(population_name + "_non_compliers_by_exceedance_prob_" + str(use_pct_of_exprob) + ".xml")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--population_dir", type=str, default=".")
    parser.add_argument("--population_name", type=str, default="pop_belgium3000k_c500_teachers_censushh")
    parser.add_argument("--use_pct_of_exprob", type=float, default=100)
    args = parser.parse_args()
    main(args.population_dir, args.population_name, args.use_pct_of_exprob)
