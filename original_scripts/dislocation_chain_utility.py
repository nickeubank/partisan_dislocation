import geopandas as gp
import numpy as np
import random
graph_path =  "../00_source_data/00_precinct_shapefiles/PA/PA_VTDALL.json"
plot_path = "../00_source_data/00_precinct_shapefiles/PA/VTD_FINAL.shp"
point_path = "../00_source_data/00_merged_points/Pennsylvania_USHouse_merged_geoid.shp"


unique_label = "GEOID10"
pop_col = "TOT_POP"
district_col = "2011_PLA_1"
county_col =  "COUNTYFP10"

pf = gp.read_file(point_path)

df = gp.read_file(plot_path)

##############################################################
# New functions for dislocation

def dislocation(partition,pf=pf,election="PRES16"):
  
    #df
    pf["current"]=pf["GEOID10"].map(dict(partition.assignment))
    #pf["dislocate"]=pf["KnnShrDem"]-pf["current"].map(partition[election])#was from rundmcmc
    
    pvec = partition[election].percents("Democratic")

    id_dict = {tuple(partition[election].races)[x]:x for x in range(len(partition.parts.keys()))}

    
    pdict = {x:pvec[id_dict[x]] for x in partition.parts.keys()}
    
    #pf["dislocate"]=pf["KnnShrDem"]-pf["current"].map(partition[election])#was from rundmcmc
    
    pf["dislocate"]=pf["KnnShrDem"]-pf["current"].map(pdict)

    #pf.groupby('current')['dislocate'].mean() #was sum

    #print(partition.assignment)

    #print(pf.groupby('current')['dislocate'].mean())
 
    district_averages = {x: pf.groupby('current')['dislocate'].mean()[x] for x in partition.parts}        


    return np.mean(pf["dislocate"]), district_averages

    

def dloc_accept(partition): 
    bound = 1
    if partition.parent is not None:
        if abs(dislocation(partition)[0]) > abs(dislocation(partition.parent)[0]):
                bound = .05         
        
    return random.random() < bound








##############################################################
# Functions for chain

#Initialize:
"""
df = gp.read_file(plot_path) 

cpops = df.groupby('COUNTYFP10')['TOT_POP'].sum()

con_ideal = sum(df['TOT_POP'])/18
sen_ideal = sum(df['TOT_POP'])*1.05/50
hou_ideal = sum(df['TOT_POP'])*1.05/203

sen_target = np.ceil(cpops/sen_ideal)
hou_target = np.ceil(cpops/hou_ideal)
con_target = np.ceil(cpops/con_ideal)

con_target_bill = con_target + 1
sen_target_bill = sen_target + 1
hou_target_bill = hou_target + 1
"""




#Measure:

def num_splits(partition):


    df["current"] = df[unique_label].map(dict(partition.assignment))
    

    splits = sum(df.groupby('COUNTYFP10')['current'].nunique() >1)
    


    return splits
    
    
def num_bill_violations(partition):

    df["current"] = df[unique_label].map(dict(partition.assignment))
    
    current_splits = df.groupby('COUNTYFP10')['current'].nunique()

    current_diff_bill = current_splits - con_target_bill


    splits = sum(current_diff_bill > 0)


    return splits
    
    
def num_ideal_violations(partition):

    df["current"] = df[unique_label].map(dict(partition.assignment))
    
    current_splits = df.groupby('COUNTYFP10')['current'].nunique()

    current_diff = current_splits - con_target

    splits = sum(current_diff > 0)


    return splits
    
    
def sum_bill_violations(partition):

    df["current"] = df[unique_label].map(dict(partition.assignment))
    
    current_splits = df.groupby('COUNTYFP10')['current'].nunique()

    current_diff_bill = current_splits - con_target_bill


    splits = sum(current_diff_bill[current_diff_bill > 0])


    return splits    
    
    
def sum_ideal_violations(partition):

    df["current"] = df[unique_label].map(dict(partition.assignment))
    
    current_splits = df.groupby('COUNTYFP10')['current'].nunique()

    current_diff = current_splits - con_target


    splits = sum(current_diff[current_diff > 0])


    return splits    
    
#Optimize: 

def bill_accept(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_bill_violations(partition) > num_bill_violations(partition.parent):
            bound = 0
        
    return random.random() < bound

def ideal_accept(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_ideal_violations(partition) > num_ideal_violations(partition.parent):
            bound = 0
        
    return random.random() < bound


def bill_ideal_accept(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_ideal_violations(partition) > num_ideal_violations(partition.parent) or num_bill_violations(partition) > num_bill_violations(partition.parent):
            bound = 0
        
    return random.random() < bound
    
    
    
    
def bill_accept05(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_bill_violations(partition.parent) > 0:
        
            if num_bill_violations(partition) > num_bill_violations(partition.parent):
                bound = .05
                
        else:
            if num_bill_violations(partition) > num_bill_violations(partition.parent):
                bound = 0         
        
    return random.random() < bound
    
    
def split_accept(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_splits(partition) > num_splits(partition.parent):
            bound = 0
         
    return random.random() < bound

 
def ideal_sum_accept(partition):
    
    bound = 1
    if partition.parent is not None:
        if sum_ideal_violations(partition) > sum_ideal_violations(partition.parent):
            bound = 0
        
    return random.random() < bound
    
def bill_accept_then_ideal(partition):
    
    bound = 1
    if partition.parent is not None:
        if num_bill_violations(partition.parent) > 0:
        
            if num_bill_violations(partition) > num_bill_violations(partition.parent):
                bound = 0
                
        else:
            if num_ideal_violations(partition) > num_ideal_violations(partition.parent):
                bound = 0         
        
    return random.random() < bound        
    
    

