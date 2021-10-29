import save_objects as so
import os
import analytic_functions as af
import re

# add to this
us_notus = so.load_obj_json("../us_them_final")
year_regex = re.compile("[1-2][0-9]{2}[0-9]")
party_regex = re.compile("(Republican)|(Democrat)")

# extract top 10 and less 10 for american for each
d = dict()
root = "analysis_results/combined/"
for sd in os.listdir(root):
    complete_path = root + sd
    if os.path.isdir(complete_path):
        for f in os.listdir(complete_path):
            if "matrix" in f:
                match_year = year_regex.search(sd).group(0)
                match_party = party_regex.search(sd)
                if match_party:
                    match_party = match_party.group(0)
                else:
                    continue
                # compute
                matrix_tuple = so.load_obj(
                    (complete_path + "/" + f).split(".pkl")[0])
                top_10 = af.find_top_k_similar(matrix_tuple, "american", 10)
                bottom_10 = af.find_bottom_k_similar(
                    matrix_tuple, "american", 10)
                # put in dict
                us_notus[match_year][match_party]["american"] = [
                    list((w, v)) for v, w in top_10]
                us_notus[match_year][match_party]["not american"] = [
                    list((w, v)) for v, w in bottom_10]

so.save_obj_json(us_notus, "../us_american_final")
