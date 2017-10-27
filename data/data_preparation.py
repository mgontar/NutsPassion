
# coding: utf-8

import pandas as pd
import numpy as np
import csv

dict_prep_ukr = {"raw":" (без обробки)", "canned": " (консерва)", "boiled":" (варіння)", "roasted":" (смаження)"}
dict_prep_eng = {"raw":" (raw)", "canned": " (canned)", "boiled":" (boiled)", "roasted":" (roasted)"}


# Product names with translations

prod_name = pd.read_csv('input\\custom\\product_names.csv', sep = ",", quotechar = "\"", encoding='utf-8', keep_default_na=False, 
                       na_values=['N/A'])
prod_name = prod_name[['name_ukr', 'name_eng']].copy()
prod_name.to_csv("output\\product_names.csv", sep=',', quotechar = "\"", quoting = csv.QUOTE_NONNUMERIC, encoding='utf-8', index=False)

# USDA product nutrients database

usda_prod_desc_head = pd.read_csv('input\\custom\\headers\\FOOD_DES_HEAD.txt', sep = ",", encoding='utf-8', header = None)
usda_prod_desc = pd.read_csv('input\\nutrients\\usda\\FOOD_DES.txt', sep = "^", quotechar = "~", encoding='cp1252', header = None)
usda_prod_desc.columns = usda_prod_desc_head.values[0]

usda_ukrs_join = pd.read_csv('input\\custom\\join\\usda_ukrstat_data.csv', sep = ",", encoding='utf-8')
usda_cust_join = pd.read_csv('input\\custom\\join\\usda_custom_data.csv', sep = ",", encoding='utf-8')
new_head = ['name']
new_head.extend(usda_ukrs_join.columns[1:].values.tolist())
usda_ukrs_join.columns = new_head
usda_cust_join.columns = new_head
usda_join = pd.concat([usda_ukrs_join, usda_cust_join], ignore_index = True)
usda_join = pd.merge(usda_join, prod_name, how='inner', left_on="name", right_on="name_ukr")
usda_join['name_prep'] = usda_join['name']+usda_join['prep'].apply(lambda x: dict_prep_ukr[x])
usda_join['name_prep_eng'] = usda_join['name_eng']+usda_join['prep'].apply(lambda x: dict_prep_eng[x])

prod_skip_list = pd.read_csv('input\\custom\\products_skip_list.csv', sep = ",", encoding='utf-8', header = None)
prod_skip_list = prod_skip_list[0].values.tolist()
#Skip raw uneatable prodcuts
usda_join = usda_join[~usda_join['name_prep'].isin(prod_skip_list)]


usda_prod_desc = pd.merge(usda_join, usda_prod_desc, how='inner', left_on="usda_id", right_on="NDB_No")

usda_nutr_head = pd.read_csv('input\\custom\\headers\\NUT_DATA_HEAD.txt', sep = ",", encoding='utf-8', header = None)
usda_nutr_data = pd.read_csv('input\\nutrients\\usda\\NUT_DATA.txt', sep = "^", quotechar = "~", encoding='cp1252', header = None, low_memory=False)
usda_nutr_data.columns = usda_nutr_head.values[0]
usda_prod_nutr = pd.merge(usda_prod_desc, usda_nutr_data, how='inner', on="NDB_No", suffixes=('_food', '_nut'))

usda_nutr_def_head = pd.read_csv('input\\custom\\headers\\NUTR_DEF_HEAD.txt', sep = ",", encoding='utf-8', header = None)
usda_nutr_def = pd.read_csv('input\\nutrients\\usda\\NUTR_DEF.txt', sep = "^", quotechar = "~", encoding='cp1252', header = None, low_memory=False, keep_default_na=False, 
                       na_values=['N/A'])
usda_nutr_def.columns = usda_nutr_def_head.values[0]

# Fix some USDA nutrient codes

# Sum up plain and added nutients
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 320, "Tagname"] = "VITA"
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 323, "Tagname"] = "VITE"
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 573, "Tagname"] = "VITE"
# Rename for proper code
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 578, "Tagname"] = "VITB12"
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 429, "Tagname"] = "VITK1"
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 435, "Tagname"] = "VITB9"
# Remove nutrient from join
usda_nutr_def.loc[usda_nutr_def["Nutr_No"] == 324, "Tagname"] = "VITDIU"

usda_prod_nutr_data = pd.merge(usda_prod_nutr, usda_nutr_def, how='inner', on="Nutr_No", suffixes=('_food', '_nut'))


# AUSNUT database contains Iodine, Omega-3 and Omega-6 values

ausn_prod_nutr = pd.read_excel('input\\nutrients\\ausnut\\8b. AUSNUT 2011-13 AHS Food Nutrient Database.xls')
ausn_join = pd.read_csv('input\\custom\\join\\ausnut_data.csv', sep = ",", encoding='utf-8', keep_default_na=False, 
                       na_values=['N/A'])
ausn_prod_nutr_sel = pd.merge(ausn_join, ausn_prod_nutr, how='inner', left_on="ausnut_id", right_on="Food ID")
ausn_prod_nutr_sel_iod = ausn_prod_nutr_sel[['name','prep','usda_id', 'Iodine (I) (µg)']].copy()
ausn_prod_nutr_sel_omg6 = ausn_prod_nutr_sel[['name','prep','usda_id', 'Linoleic acid (g)']].copy()
ausn_prod_nutr_sel_omg3 = ausn_prod_nutr_sel[['name','prep','usda_id', 'Alpha-linolenic acid (g)']].copy()
ausn_prod_nutr_sel_iod.loc[:,"Tagname"] = "I"
ausn_prod_nutr_sel_iod.loc[:,"Units"] = "µg"
ausn_prod_nutr_sel_iod = ausn_prod_nutr_sel_iod.rename(columns={'Iodine (I) (µg)': 'Nutr_Val'})
ausn_prod_nutr_sel_omg6.loc[:,"Tagname"] = "OMG6"
ausn_prod_nutr_sel_omg6.loc[:,"Units"] = "g"
ausn_prod_nutr_sel_omg6 = ausn_prod_nutr_sel_omg6.rename(columns={'Linoleic acid (g)': 'Nutr_Val'})
ausn_prod_nutr_sel_omg3.loc[:,"Tagname"] = "OMG3"
ausn_prod_nutr_sel_omg3.loc[:,"Units"] = "g"
ausn_prod_nutr_sel_omg3 = ausn_prod_nutr_sel_omg3.rename(columns={'Alpha-linolenic acid (g)': 'Nutr_Val'})

ausn_prod_nutr_sel_full = pd.concat([ausn_prod_nutr_sel_iod, ausn_prod_nutr_sel_omg6, ausn_prod_nutr_sel_omg3], ignore_index = True)
ausn_prod_nutr_data = pd.merge(ausn_prod_nutr_sel_full, prod_name, how='inner', left_on="name", right_on="name_ukr")
ausn_prod_nutr_data.loc[:,'name_prep'] = ausn_prod_nutr_data['name']+ausn_prod_nutr_data['prep'].apply(lambda x: dict_prep_ukr[x])
ausn_prod_nutr_data.loc[:,'name_prep_eng'] = ausn_prod_nutr_data['name_eng']+ausn_prod_nutr_data['prep'].apply(lambda x: dict_prep_eng[x])

#Skip raw uneatable prodcuts same way as in USDA
ausn_prod_nutr_data = ausn_prod_nutr_data[~ausn_prod_nutr_data['name_prep'].isin(prod_skip_list)]

prod_nutr_data = pd.concat([usda_prod_nutr_data, ausn_prod_nutr_data], ignore_index = True)


# Nutrients RDA

nutr_rda = pd.read_csv('input\\rda\\rda.csv', sep = ",", encoding='utf-8', keep_default_na=False, 
                       na_values=['N/A'])

# Fill missing values with some large constants
nutr_rda = nutr_rda.fillna(1000000)

# Unify rda and nutrients measures to single units

# RDA in µg while USDA in mg
nutr_rda.loc[nutr_rda["nut_code"] == "CU", "rda"] /= 1000
nutr_rda.loc[nutr_rda["nut_code"] == "CU", "mda"] /= 1000
# RDA in mg while USDA in µg
nutr_rda.loc[nutr_rda["nut_code"] == "FLD", "rda"] *= 1000
nutr_rda.loc[nutr_rda["nut_code"] == "FLD", "mda"] *= 1000
# RDA in g while USDA in mg
nutr_rda.loc[nutr_rda["nut_code"] == "K", "rda"] *= 1000
nutr_rda.loc[nutr_rda["nut_code"] == "K", "mda"] *= 1000
# RDA in g while USDA in mg
nutr_rda.loc[nutr_rda["nut_code"] == "NA", "rda"] *= 1000
nutr_rda.loc[nutr_rda["nut_code"] == "NA", "mda"] *= 1000
# RDA in L (kg) while USDA in g
nutr_rda.loc[nutr_rda["nut_code"] == "WATER", "rda"] *= 1000
nutr_rda.loc[nutr_rda["nut_code"] == "WATER", "mda"] *= 1000

# Remove Fluorine since it is present in water 
nutr_rda = nutr_rda[nutr_rda.nut_code != "FLD"]

prod_nutr_rda_data = pd.merge(nutr_rda, prod_nutr_data, how='left', left_on="nut_code", right_on="Tagname")

unit_data = prod_nutr_rda_data[['Tagname', 'Units']].copy().drop_duplicates()
unit_data.to_csv("output\\data_units.csv", sep=',', encoding='utf-8', index=False)

rda_unit_data = prod_nutr_rda_data[['ukr_name', 'eng_name', 'Tagname', 'rda', 'mda', 'Units']].copy().drop_duplicates()
rda_unit_data.to_csv("output\\data_rda.csv", sep=',', encoding='utf-8', index=False)
rda_unit_data.to_excel("output\\data_rda.xlsx", encoding='utf-8', index=False)


# Product prices

ukrs_prod_pric = pd.read_csv('input\\prices\\ukrstat_price.csv', sep = ",", encoding='utf-8')
cust_prod_pric = pd.read_csv('input\\prices\\custom_price.csv', sep = ",", encoding='utf-8')
new_head = ['name']
new_head.extend(ukrs_prod_pric.columns[1:].values.tolist())
ukrs_prod_pric.columns = new_head
cust_prod_pric.columns = new_head
prod_pric = pd.concat([ukrs_prod_pric, cust_prod_pric])

prod_nutr_rda_pric_data = pd.merge(prod_nutr_rda_data, prod_pric, how='left', left_on="name", right_on="name")
prod_prep_name = prod_nutr_rda_pric_data[['name_prep']].copy().drop_duplicates()
prod_prep_name.to_csv("output\\data_name.csv", sep=',', encoding='utf-8', index=False)

prod_pric_data = prod_nutr_rda_pric_data[['name_prep', 'name_prep_eng', 'price_kg_uah']].drop_duplicates()
weig_chng_coef = pd.read_csv('input\\custom\\prep_weight_change_coef.csv', sep = ",", encoding='utf-8')
prod_pric_coef_data = pd.merge(prod_pric_data, weig_chng_coef, how='inner', on="name_prep", suffixes=('_price', '_coeff'))
prod_pric_coef_data['price_kg_uah'] = np.round(prod_pric_coef_data['price_kg_uah']*prod_pric_coef_data['coeff'], decimals=2)
prod_pric_coef_data = prod_pric_coef_data[['name_prep_eng', 'price_kg_uah']].copy()

sorter = usda_join.name_prep_eng.values
sorter_index = dict(zip(sorter,range(len(sorter))))
prod_pric_coef_data['name_prep_Rank'] = prod_pric_coef_data['name_prep_eng'].map(sorter_index)
prod_pric_coef_data.sort_values(['name_prep_Rank'], ascending = [True], inplace = True)
prod_pric_coef_data.drop('name_prep_Rank', 1, inplace = True)

prod_pric_coef_data.to_csv("output\\data_price.csv", sep=',', encoding='utf-8', index=False)
prod_pric_coef_data.to_excel("output\\data_price.xlsx", encoding='utf-8', index=False)


# Final product/nutrient pivot table

prod_nutr_rda_data_cut = prod_nutr_rda_data[['name_prep_eng', 'eng_name', 'Nutr_Val']].copy()
prod_nutr_rda_data_cut.loc[:,'Nutr_Val'] = np.round(prod_nutr_rda_data_cut['Nutr_Val']*10,decimals=6)
prod_nutr_rda_data_cut_pivt = prod_nutr_rda_data_cut.pivot_table(index='name_prep_eng', columns='eng_name', values='Nutr_Val', 
                      aggfunc = np.sum, dropna = False, fill_value = 0).T
prod_nutr_rda_data_cut_pivt = prod_nutr_rda_data_cut_pivt.reindex(nutr_rda.eng_name)
prod_nutr_rda_data_cut_pivt = prod_nutr_rda_data_cut_pivt[usda_join.name_prep_eng]
prod_nutr_rda_data_cut_pivt.to_csv("output\\data_pivot.csv", sep=',', encoding='utf-8')
prod_nutr_rda_data_cut_pivt.to_excel("output\\data_pivot.xlsx", encoding='utf-8')


# Experimental Fullness Factor
def calcFullness(row):
    cal = max(30,row["Energy"]/10)
    pr = max(30,row["Proteins"]/10)
    fib = max(12,row["Fibers"]/10)
    fat = max(50,row["Fats"]/10)
    cal_part = 0 if cal==0 else 41.7/pow(cal,0.7)
    return round(max(0.5, min(5.0, cal_part  + 0.05*pr + 6.17E-4*pow(fib,3) - 7.25E-6*pow(fat,3) + 0.617)),2)


prod_nutr_rda_data_cut_pivt2 = prod_nutr_rda_data_cut.pivot_table(index='eng_name', columns='name_prep_eng', values='Nutr_Val', 
                      aggfunc = np.sum, dropna = False, fill_value = 0).T
prod_nutr_rda_data_cut_pivt2["Fullness"] = prod_nutr_rda_data_cut_pivt2.apply(calcFullness, axis=1)
prod_full = prod_nutr_rda_data_cut_pivt2.T.unstack().reset_index(name='value')
prod_full = prod_full.loc[prod_full.eng_name=="Fullness"]
prod_full = prod_full.rename(columns={'value': 'fullness'})
prod_full = prod_full[['name_prep_eng', 'fullness']]
sorter = usda_join.name_prep_eng.values
sorter_index = dict(zip(sorter,range(len(sorter))))
prod_full['name_prep_Rank'] = df['name_prep_eng'].map(sorter_index)
prod_full.sort_values(['name_prep_Rank'], ascending = [True], inplace = True)
prod_full.drop('name_prep_Rank', 1, inplace = True)

prod_full.to_csv("output\\data_pivot_fullness.csv", sep=',', encoding='utf-8', index=False)
prod_full.to_excel("output\\data_pivot_fullness.xlsx", encoding='utf-8', index=False)

