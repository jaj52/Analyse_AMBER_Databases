#!/usr/bin/python
#################################################
#                                               #
#       Analysing Wales DPS Databases           #
#                                               # 
# Computes several order parameters for         #
# the path betweeen two end-points.             #   
# Most useful for the fastest path, when trying #
# to decipher the folding mechanism.            #
#                                               #
# Author:JA Joseph (jaj52@cam.ac.uk)            #
#################################################
# Important: 
# (1) cpptraj must be in your path 
# (2) AMBER topology file 'coords.prmtop' must be 
#     in your cwd. 
# (3) Edit the script to include your PATHSAMPLE executable
# (4) The normal DPS database files should be in your cwd


from subprocess import check_call, Popen, PIPE
import os 
import sys 
import shutil 


##############################
# Useful functions (General) #
##############################

def pdb_from_rst(rstname, pdbname):
    """Creates a pdb file from an AMBER rst and prmtop file using ambpdb"""
    topname = 'coords.prmtop'
    devnull = open(os.devnull, 'w')
    with open(pdbname, 'w') as fname:
        check_call(['ambpdb', '-p', topname], stdout = fname, stdin = open(rstname, 'r'), stderr = devnull)
    return pdbname 



def run_cppraj(praj_in):
    """Run cpptraj program"""
    topname = 'coords.prmtop'
    trajin = praj_in
    devnull = open(os.devnull, 'w')
    with open('out' , 'w') as fout:
        check_call(['cpptraj', '-p', topname], stdout = fout, stdin = open(trajin, 'r'), stderr = devnull)
    return



def extract_ts(index):
    """Extract a transition state from a PATHSAMPLE database"""
    # Prepare input
    shutil.move('pathdata', 'pathdata_orig')
    with open('pathdata_orig') as f:
        lines = f.readlines()
    with open('pathdata', 'w') as newf:
        # write the appropriate EXTRACTTS line to the new pathdata file
        newf.write('EXTRACTTS %d\n' % index)
        # write the remaining lines to the new file unless it is EXTRACTTS or EXTRACTMIN
        for line in lines:
            if 'EXTRACTTS' not in line and 'EXTRACTMIN' not in line:
                newf.write('%s' % line)

    # Run PATHSAMPLE and deal with output
    devnull = open(os.devnull, 'w')
    check_call(['PATHSAMPLE_APR_17'], stdout = devnull, stderr = devnull) 
    # rename output file to include appropriate index
    e_ts = 'extractedts_%d.rst' % index
    shutil.move('extractedts.rst', e_ts)
    # move original pathdata file back
    shutil.move('pathdata_orig', 'pathdata')
    return e_ts
 

def extract_min(index):
    """Extract a minimum from a PATHSAMPLE database"""
    # Prepare input
    shutil.move('pathdata', 'pathdata_orig')
    with open('pathdata_orig') as f:
        lines = f.readlines()
    with open('pathdata', 'w') as newf:
        # write the appropriate EXTRACTTS line to the new pathdata file
        newf.write('EXTRACTMIN %d\n' % index)
        # write the remaining lines to the new file unless it is EXTRACTTS or EXTRACTMIN
        for line in lines:
            if 'EXTRACTTS' not in line and 'EXTRACTMIN' not in line:
                newf.write('%s' % line)

    # Run PATHSAMPLE and deal with output
    devnull = open(os.devnull, 'w')
    check_call(['PATHSAMPLE_APR_17'], stdout = devnull, stderr = devnull) 
    # rename output file to include appropriate index
    e_min =  'extractedmin_%d.rst' % index
    shutil.move('extractedmin.rst', e_min)
    # move original pathdata file back
    shutil.move('pathdata_orig', 'pathdata')
    return e_min
 


def create_trajin(index_list):
    """Create input file for cpptraj"""
    trajin = 'trajin'
    o = open(trajin, 'w')
    for k,v in enumerate(index_list):
        if (int(k) % int(2)) ==0:
            rst = extract_min(v)
            o.write('trajin %s' % rst)
            o.write("\n")
        else:
            rst = extract_ts(v)
            o.write('trajin %s' % rst)
            o.write("\n")
    o.close()
    return trajin



def format_output(output_file):
    """Format order parameter output for plotting"""
    old_lines = []
    new_lines = []	
    with open(output_file, 'r') as f:
        old_lines = f.readlines()
  
    for line in old_lines:
        if not "Frame" in line:
            value = line.split()
            data = '%s       %s' %(value[0], value[1])	
            new_lines.append(data)
            
    nf = open('%s.format' %output_file, 'w') 
    for val in new_lines:
        nf.write(val)
        nf.write('\n')
    nf.close()
    return 


##########################################
# Functions to compute order parameters  #
##########################################

def calc_SS(ss_in, ss_data, ss_mask):
    """Compute secondary structure content for path"""
    # append information to cpptraj input file for ss calculation
    o = open(ss_in, 'a')

    # unique name for cpptraj output
    op_out = 'Epath_SS_%s.dat' %ss_data
    o.write ('secstruct out %s :%s ptrajformat' %(op_out,ss_mask))
    o.close()

    # call to cpptraj
    run_cppraj(ss_in)
    return 



def calc_HB(hb_in, hb_data, hb_mask):
    """Compute H-bond content for path"""
    # append information to cpptraj input file for HB calculation
    o = open(hb_in, 'a')
    
    op_out = 'Epath_HB_%s.dat' %hb_data
    o.write('hbond out %s :%s@CA,C,N,O,H distance 3.5 angle 150' %(op_out, hb_mask))
    o.close()
    
    # call to cpptraj
    run_cppraj(hb_in)
    format_output(op_out)
    return



def calc_RMSD(rmsd_in, rmsd_data, rmsd_mask, rmsd_ref):
    """Compute rmsd for path"""
    # append information to cpptraj input file for rmsd calculation
    o = open(rmsd_in, 'a')
    
    op_out = 'Epath_RMSD_%s.dat' %rmsd_data
    o.write('reference %s\n' %rmsd_ref)
    o.write('rms out %s :%s reference' %(op_out, rmsd_mask))
    o.close()
    
    # call to cpptraj
    run_cppraj(rmsd_in)
    format_output(op_out)
    return



def calc_RG(rg_in, rg_data, rg_mask):
    """Compute radius of gyration for path"""
    # append information to cpptraj input file for rg calculation
    o = open(rg_in, 'a')
    
    op_out = 'Epath_RG_%s.dat' %rg_data
    o.write('radgyr out %s :%s' %(op_out, rg_mask))
    o.close()
    
    # call to cpptraj
    run_cppraj(rg_in)
    format_output(op_out)
    return

##################################################################################
##################################################################################

def main():
    """Code to run"""
    id_list = []

    with open('Epath', 'r') as f:
	    old_lines = f.readlines()

    for line in old_lines:
        value = line.split()
        id_ = int(value[2])
        id_list.append(id_)

    # Generate input file for cpptraj
    input_file = create_trajin(id_list)
    
    # 1. Compute secondary structure of min & ts along Epath
    shutil.copy(input_file, 'ss_input')
    ss_input = 'ss_input'
    data_file = 'test'
    mask = '1-18'
    calc_SS(ss_input, data_file, mask)

    # 2. Compute no. of Hydrogen bonds of min & ts along Epath
    shutil.copy(input_file, 'hb_input')
    hb_input = 'hb_input'
    data_file = 'test'
    mask = '1-18'
    calc_HB(hb_input, data_file, mask)

    # 3. Compute RMSD from ref for min & ts along Epath
    shutil.copy(input_file, 'rmsd_input')
    rmsd_input = 'rmsd_input'
    data_file = 'test'
    mask = '1-18'
    ref = 'extractedmin_1.rst'
    calc_RMSD(rmsd_input, data_file, mask, ref)

    # 4. Compute Radius of Gyration for min & ts along Epath
    shutil.copy(input_file, 'rg_input')
    rg_input = 'rg_input'
    data_file = 'test'
    mask = '1-18'
    calc_RG(rg_input, data_file, mask)



if __name__ == "__main__":
    main()

