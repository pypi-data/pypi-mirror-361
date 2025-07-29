import argparse, tempfile, logging, os
from samplesheetutils.utils.sample import *
from samplesheetutils.utils.output import *
from samplesheetutils.utils.fasta import *
from samplesheetutils.utils.input import *
from samplesheetutils.utils.alignment import *
from samplesheetutils.utils.a3m import *

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig()

def version():
    print("samplesheet-utils 1.3.1")

#if __name__ == "__main__":
def truncate_msa():
    parser = argparse.ArgumentParser(
        prog="Truncate MSA",
        description="Utility for truncating MSAs for targeting a specified region.",
        epilog="Written by nbtm-sh @ unsw.edu.au")

    parser.add_argument('input_file', default='?', help='Path to input file')
    parser.add_argument('region_start', default='?', help='The index of the first residue to target.')
    parser.add_argument('region_end', default='?', help='The index of the final residue to target.')
    parser.add_argument('-o', '--output', help='Path to output file', default='output.a3m', dest='output')
    parser.add_argument('-i', '--in-place', help='Replace the target file with the modified output (in-place)', default=False, action='store_true', dest='in_place')
    parser.add_argument('-r', '--inverse', help='Invert output (delete residues within the target region)', default=False, action='store_true', dest='inverse')
    parser.add_argument('--version', help='Show version number', default=False, action='store_true', dest='version')
    parser.add_argument('--debug', help='Show debug output', default=False, action='store_true', dest='debug')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if (args.version):
        version()
        exit(0)

    if (args.debug):
        version()

    # Check that all arguments are valid
    args_valid = 0
    args_valid |= args.input_file == '?'
    args_valid |= args.region_start == '?'
    args_valid |= args.region_end == '?'

    if args_valid:
        logger.error("Please specify all input arguments. Use --help to display required arguments")
        exit(1)

    # Validate that an input was provided
    logger.debug(f"Loading {args.input_file}...")
    samples = []

    # Try to load variables
    try:
        r_start = int(args.region_start)
        r_end = int(args.region_end)
    except ValueError:
        logger.error("Please enter only real numbers for region_start and region_end")

    logger.debug(f"Region Start: {r_start}, Region End: {r_end}")

    try:
        with open(args.input_file, "r") as fp:
            logger.debug(f"Opened input file {args.input_file} for reading")
            samples = read_a3m(
                    fp,
                    read_data=True
                )
            logger.debug(f"Imported {len(samples)} samples.")
    except FileNotFoundError:
        logger.error(f"Input file {args.input_file} does not exist")
        exit(1)
    except PermissionError:
        logger.error(f"Input file {args.input_file} could not be opened due to a permission error")
        exit(1)
    
    # Edit the a3m file and preserve the first entry
    # First check to make sure that the file is longer than 1
    if len(samples) == 1:
        logger.error("The a3m file only cotnains one sample. The first sample of the a3m file is always preserved, so no changes to the file are needed")
        exit(1)

    for i, o in enumerate(samples):
        # Skip the first entry
        if i == 0:
            continue

        # Get a list of elements from the string
        aln_l = [el for el in o.data]
        # Edit the string
        aln_sub = ['-' if (i > r_start and i < r_end) ^ args.inverse else k for i, k in enumerate(aln_l)]
        samples[i].data = ''.join(aln_sub)

    output_file = args.output if not args.in_place else args.input_file
    logger.debug(f"Opening output file {output_file} for writing...")
    with open(output_file, "w") as fp:
        make_a3m(fp, samples)

    
