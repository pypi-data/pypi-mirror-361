import MDAnalysis as md
from MDAnalysis.transformations import center_in_box
import numpy as np
import argparse
import sys

def check_gro_file(filename):
    '''
    Makes sure that the files are gros. As is, this script fails with PDBs as they
    do not have the box sizes... So input should be gro.
    '''
    if not filename.lower().endswith(".gro"):
        sys.exit(f"Error: '{filename}' is not a .gro file.")
        
def enlarge_and_center(inputstructure, outputstructure, inp_size=200):
    """
    Takes in a structure and enlarges its box. Afterwards centers it 
    in the new large box.

    Enlargment works as follows:  take the maximum between inp_size and the 
    average box size found in the input file. Avg. box size is used for cases
    where the size might be something ridiculous like [10, 10, 200]. This is 
    doubled and used to generate final box with mol centered. If a PDB is used
    as the input, its boxsize will be 0.

    This only works if the input structure is WHOLE. We cannot make structures
    whole without connectivity information... so its important that the input is
    whole.
    """
    u = md.Universe(inputstructure)

    cur_size = np.mean(u.dimensions[:3])
    largest = max(inp_size, cur_size)
    u.dimensions = [largest*2, largest*2, largest*2, 90., 90., 90.]

    u.trajectory.add_transformations(center_in_box(u.atoms))
    u.atoms.write(outputstructure)

def main():
    parser = argparse.ArgumentParser(description="Enlarge a box and center the structure using MDAnalysis. WARNING: Make sure your molecule is whole.")
    parser.add_argument("-i", "--input", required=True, help="Input structure file (e.g., PDB, GRO).")
    parser.add_argument("-o", "--output", required=True, help="Output structure file (use GRO only).")
    parser.add_argument("-s", "--size", type=float, default=200.0, help="Minimum half-box size (in Å). Default: 200.")

    args = parser.parse_args()
    check_gro_file(args.output)
    enlarge_and_center(args.input, args.output, args.size)
