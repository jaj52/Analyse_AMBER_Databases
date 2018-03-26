#!/usr/bin/python
#########################################
#           Common Functions for 
#       Analysing Wales DPS Databases
#
# Author:JA Joseph (jaj52@cam.ac.uk)
########################################


################################################################
# Functions to analyse files already produced by cpptraj/ptraj # 
################################################################
def total_parm(alist):
    """Takes a list of values and returns the sum"""
    total_val = 0.0
    for val in alist:
        total_val += float(val)
    return total_val 



def get_data(cpptraj_data_file):
    """Extracts the values (e.g H-bond distances) from the cpptraj data file. And returns a 
    list of sums for the order parameter"""
    data_list = []
    with open(cpptraj_data_file, 'r') as lines:
        for line in lines:
            if not 'Frame' in line:
                data = line.split()
                total_data = total_parm(data[1:])
                data_list.append(total_data)
    return data_list 



def parm_out(parm_name, parm_list):
    """ Writes the ouput file for the order parameter"""
    output = open('%s.out' % parm_name, 'w')
    for num in parm_list:
        output.write(str(num))
        output.write('\n')
    output.close
    return



def get_parm(traj_data_file):
    """Use this function instead for order parameters when sums are not 
    needed"""
    parm_list = []
    with open(traj_data_file, 'r') as plines:
        for line in plines:
            if not 'Frame' in line:
                value = line.split()
                parm_list.append(value[1])
    return parm_list

