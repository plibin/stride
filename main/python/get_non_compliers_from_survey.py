import csv

question_ids = {
    "age": "Q3",
    "zipcode": "Q5",
    "single": "Q7",
    "in_belgium": "Q68",
    "handshake_kiss_last_week": "Q10",
    "handshake_kiss_last_week_single": "Q63"
}

with open("2020_UA_Corona_golf6_data_weights.csv", encoding="latin-1") as csvfile:
    reader = csv.DictReader(csvfile)
    total = 0
    nc = 0
    total_by_nis = {}
    nc_by_nis = {}
    for row in reader:
        single = int(row[question_ids["single"]])
        nis_code = int(row["niscode"])
        # TODO "NA"?
        if single == 1:
            non_complier = False if int(row[question_ids["handshake_kiss_last_week_single"]]) == 1 else True
        else:
            non_complier = False if int(row[question_ids["handshake_kiss_last_week"]]) == 1 else True

        weight = float(row["w2"])
        total += weight
        if non_complier:
            nc += weight
        if nis_code in total_by_nis:
            total_by_nis[nis_code] += weight
        else:
            total_by_nis[nis_code] = weight
        if non_complier:
            if nis_code in nc_by_nis:
                nc_by_nis[nis_code] += weight
            else:
                nc_by_nis[nis_code] = weight


    fraction_nc_by_nis = {}

    for nis_code in total_by_nis:
        total = total_by_nis[nis_code]
        if nis_code in nc_by_nis:
            nc = nc_by_nis[nis_code]
        else:
            nc = 0
        fraction_nc_by_nis[nis_code] = nc / total

    with open("WAVE6_nc_by_nis.csv", "w") as csvfile:
        fieldnames = ["nis_code", "fraction_non_compliers"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nis_code in fraction_nc_by_nis:
            writer.writerow({"nis_code": nis_code, "fraction_non_compliers": fraction_nc_by_nis[nis_code]})







'''
['', 'UNID6',
'StartDate',
'EndDate',
'Status',
'IPAddress',
'Progress',
'Duration__in_seconds_',
'Finished',
'RecordedDate',
'ResponseId',
'RecipientLastName',
'RecipientFirstName',
'RecipientEmail',
'ExternalReference', 'LocationLatitude', 'LocationLongitude',
'DistributionChannel', 'UserLanguage',
'Q2_1', 'Q2_2', 'Q2_4', 'Q2_5', 'Q2_7',
'Q2_6', 'Q2_3', 'Q160_Browser', 'Q160_Version', 'Q160_Operating_System', 'Q160_Resolution',
'Q3', 'Q4', 'Q5', 'Q68', 'Q6', 'Q6_8_TEXT', 'Q7', 'Q64', 'Q65', 'Q66', 'Q67', 'Q9', 'Q10', 'Q62', 'Q63', 'Q136', 'Q137_1', 'Q137_2', 'Q137_3', 'Q137_4', 'Q137_5', 'Q137_6', 'Q137_7', 'Q137_8', 'Q137_9', 'Q137_10', 'Q137_11', 'Q11', 'Q69', 'Q15_1', 'Q15_2', 'Q15_3', 'Q15_4', 'Q15_5', 'Q15_6', 'Q15_7', 'Q15_8', 'Q15_9', 'Q15_10', 'Q15_11', 'Q15_12', 'Q15_13', 'Q15_14', 'Q15_15', 'Q15_16', 'Q15_17', 'Q15_17_TEXT', 'Q16', 'Q12', 'Q13', 'Q14', 'Q14_8_TEXT', 'Q17', 'Q17_20_TEXT', 'Q18', 'Q19_1', 'Q19_2', 'Q19_3', 'Q19_4', 'Q19_5', 'Q19_6', 'Q19_7', 'Q20_1', 'Q20_2', 'Q20_3', 'Q20_4', 'Q20_5', 'Q20_6', 'Q20_7', 'Q21', 'Q21_4_TEXT', 'Q22', 'Q23', 'Q24', 'Q24_10_TEXT', 'Q25', 'Q25_3_TEXT', 'Q26', 'Q26_4_TEXT', 'Q27', 'Q27_5_TEXT', 'Q28', 'Q29_1', 'Q29_2', 'Q29_3', 'Q29_4', 'Q29_5', 'Q29_6', 'Q29_7', 'Q29_8', 'Q29_9', 'Q29_10', 'Q29_11', 'Q29_12', 'Q29_13', 'Q29_14', 'Q29_15', 'Q29_16', 'Q29_14_TEXT', 'Q30', 'Q31', 'Q32', 'Q33', 'Q34', 'Q35', 'Q36', 'Q127', 'Q128', 'Q40_1', 'Q40_2', 'Q40_3', 'Q40_4', 'Q40_5', 'Q40_6', 'Q40_7', 'Q40_8', 'Q87_1', 'Q87_2', 'Q87_3', 'Q87_4', 'Q163_1', 'Q163_2', 'Q163_3', 'Q163_20', 'Q163_4', 'Q163_5', 'Q163_6', 'Q163_7', 'Q163_8', 'Q163_9', 'Q163_10', 'Q163_11', 'Q163_12', 'Q163_13', 'Q163_14', 'Q163_15', 'Q163_16', 'Q163_17', 'Q163_21', 'Q163_18', 'Q163_19', 'Q163_19_TEXT', 'Q162_1_1', 'Q162_2_1', 'Q162_3_1', 'Q162_36_1', 'Q162_4_1', 'Q162_5_1', 'Q162_6_1', 'Q162_7_1', 'Q162_8_1', 'Q162_9_1', 'Q162_10_1', 'Q162_11_1', 'Q162_12_1', 'Q162_13_1', 'Q162_14_1', 'Q162_15_1', 'Q162_16_1', 'Q162_17_1', 'Q162_18_1', 'Q162_37_1', 'Q162_19_1', 'Q162_1_2', 'Q162_2_2', 'Q162_3_2', 'Q162_36_2', 'Q162_4_2', 'Q162_5_2', 'Q162_6_2', 'Q162_7_2', 'Q162_8_2', 'Q162_9_2', 'Q162_10_2', 'Q162_11_2', 'Q162_12_2', 'Q162_13_2', 'Q162_14_2', 'Q162_15_2', 'Q162_16_2', 'Q162_17_2', 'Q162_18_2', 'Q162_37_2', 'Q162_19_2', 'Q162_1_3', 'Q162_2_3', 'Q162_3_3', 'Q162_36_3', 'Q162_4_3', 'Q162_5_3', 'Q162_6_3', 'Q162_7_3', 'Q162_8_3', 'Q162_9_3', 'Q162_10_3', 'Q162_11_3', 'Q162_12_3', 'Q162_13_3', 'Q162_14_3', 'Q162_15_3', 'Q162_16_3', 'Q162_17_3', 'Q162_18_3', 'Q162_37_3', 'Q162_19_3', 'Q75_1', 'Q75_2', 'Q75_3', 'Q75_4', 'Q75_5', 'Q76', 'Q80', 'Q79_1', 'Q79_2', 'Q79_3', 'Q79_4', 'Q79_5', 'Q81', 'Q78', 'Q82_1', 'Q82_2', 'Q82_3', 'Q82_4', 'Q82_5', 'Q83', 'Q84', 'Q85_1', 'Q85_2', 'Q85_3', 'Q85_4', 'Q85_5', 'Q86', 'Q87', 'Q91_1', 'Q91_2', 'Q91_3', 'Q91_4', 'Q91_5', 'Q91_6', 'Q91_5_TEXT', 'Q38_1', 'Q38_2', 'Q38_3', 'Q39_1', 'Q39_2', 'Q39_3', 'Q42', 'Q43', 'Q44', 'Q45', 'Q46', 'Q47', 'Q48', 'Q49', 'Q50', 'Q51', 'Q52', 'Q53', 'Q54', 'Q55', 'Q199_1', 'Q199_2', 'Q199_3', 'Q199_4', 'Q199_5', 'Q199_6', 'Q150_1', 'Q57_1', 'Q57_2', 'Q57_3', 'Q57_4', 'Q57_5', 'Q151', 'Q197', 'Q92', 'Q92_9_TEXT', 'Q196', 'Q58_1', 'Q58_2', 'Q58_3', 'Q58_4', 'Q58_5', 'Q58_6', 'Q58_7', 'Q58_8', 'Q59', 'Q74', 'niscode', 'gemeente', 'provin', 'Q64_group', 'Q65_group', 'Q66_group', 'Q67_group', 'Q8_child', 'Q8_child_group', 'Q9_group', 'Q8_sum', 'Q8_sum_group', 'gewest', 'COVID_symptoms', 'Single_HH', 'Q59_teller', 'Q74_teller', 'age_range', 'WB_1', 'Age_9klas', 'Q9_Q62', 'Q10_Q63', 'echt_alleen', 'centrumstad', 'male', 'fam_symp', 'covid', 'single', 'wb_2binary', 'uls6_score', 'gender', 'agecat', 'province', 'w1', 'w2']
'''
