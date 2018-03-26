#!/usr/bin/env python
#################################################
#                                               #
#  This script converts AMBER restart files     #
#  into .xyz files for OPTIM. Useful for        #
#  parsing trajectories from MD directly to     #
#  OPTIM, e.g for the purpose of minimising     #
#  trajectory frames.                           #    
#                                               #
#                                               #
# Author:JA Joseph (jaj52@cam.ac.uk)            #
#################################################
# Important (Preliminaries)
# 1. Extract frames using cpptraj (if necessary) and 
# create a list will the file names e.g ls *rst > rst_files
# 2. Create corresponding pdb file e.g using ambpdb program
# Usage: ./restart2xyz_multi.sh <rst_file_list> <pdb_file>'

import sys
import re


if len(sys.argv) == 3:
    print "This script converts restart files created by AMBER \
            to a .xyz files for OPTIM"
    rst_files = sys.argv[1]
    pdb = sys.argv[2]
else:
    print "This script converts a restart file created by AMBER \
                        to a .xyz file for OPTIM"
  
    rst_files = raw_input('List of AMBER restart files to convert: ')
    pdb = raw_input('PDB file: ')



def get_atom_coords(apdb, arst):
    """Parses the pdb and rst files to obtain an ordered list of 
    atom names and corresponding xyz coordinates"""

    # This list will contain sets of tuples - atom name and corresponding xyz coords
    atom_coords = []
    with open(apdb, 'r') as f_pdb:
        data = f_pdb.readlines()

    for line in data:
        if line.split()[0] == 'ATOM' :
        # storing the atom name and '0' (dummy value) as a tuple. Will remove the 0 later
            atom_set = (line[12:16], 0)
            atom_coords.append(atom_set)

    with open(arst, 'r') as f_rst:
        xyz_coords = f_rst.readlines()
   # remove the first two values in the coords list - ie first two lines of AMBER rst file
	xyz_coords.pop(0)
	xyz_coords.pop(0)
    
    i = 1
    for cline in xyz_coords:
	cline = cline.strip('\n')
	coords = []
	if len(cline) == 72 :
	    lbound = 0
   	    ubound = 12
            while ubound <= 72:
	    	coords.append(cline[lbound:ubound])
	    	lbound += 12
		ubound += 12

	    
	elif len(cline) == 36 :
	    lbound = 0
            ubound = 12
	    while ubound <= 36:
                coords.append(cline[lbound:ubound])
                lbound += 12
                ubound += 12
	
       	try:
       	    atom_coords[2 * i - 2] = atom_coords[2 * i - 2] + ("{:20.10f}".format(float(coords[0])), \
                        "{:20.10f}".format(float(coords[1])) , "{:20.10f}".format(float(coords[2]))) 
       	except IndexError:
            #print 'HERE'
            pass 
        
	try:
            atom_coords[2 * i - 1] = atom_coords[2 * i - 1] + ("{:20.10f}".format(float(coords[3])), \
                        "{:20.10f}".format(float(coords[4])) , "{:20.10f}".format(float(coords[5])))
            i = i + 1
        except IndexError:
	    #print 'HERE'
            pass

    return atom_coords    



def write_xyz(atom_coords_list, lnum):
    """Writes out XYZ files in correct format for OPTIM"""
    num_atoms = int(len(atom_coords_list))
    num1 = int(lnum[0])
    #num2 = int(lnum[1])
    out = open('AMBER.points.%d.xyz' %(num1), 'w')
    out.write('%d \n' % num_atoms)
    out.write('AMBER.points\n')

    for set_ in atom_coords_list:
        atomic_name = "{:<6}".format(set_[0])
        # remember the value at index 1 in the set_ is the '0' dummy variable
        x_coords = "{:<25}".format(set_[2])
        y_coords = "{:<25}".format(set_[3])
        z_coords = "{:<25}".format(set_[4])
        out.write("%s %s %s %s\n" % (atomic_name, x_coords, y_coords, z_coords))
    
    out.close()
    return 

######################################################################################
#######################################################################################
def main():
    """Code to run"""

    with open(rst_files, 'r') as g:
        rfiles = g.readlines()

    for rstfile in rfiles:
        rst = rstfile.strip('\n')
        nums = re.findall(r'\d+', rst)
        xyz_data = get_atom_coords(pdb,rst)
        write_xyz(xyz_data, nums)


if __name__ == "__main__":
    main()
