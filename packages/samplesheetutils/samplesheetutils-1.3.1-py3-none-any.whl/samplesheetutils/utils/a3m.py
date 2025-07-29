from samplesheetutils.utils.sample import Sample
from samplesheetutils.utils.alignment import Alignment
from typing import Union
import re 

def read_a3m(fp, read_data=True):
    """
    Read in an a3m file and return an array containing the alignment hits and their names.
    read_data: Controls if you wish to read the a3m residue hits. Set to false if you only want to read the names of the hits
    """

    align_samples = []

    lines = fp.readlines()

    temp_aln_object = None

    for fasta_line in lines:
        if re.search("^\\>.*$", fasta_line):
            # This is to add support for fixed-width fasta files
            if temp_aln_object is not None:
                align_samples.append(temp_aln_object)
            temp_aln_object = Sample(fasta_line[1:].strip(), fp.name, "")
        elif temp_aln_object is not None:
            temp_aln_object.data += fasta_line.strip()

    if temp_aln_object is not None:
        align_samples.append(temp_aln_object)

    fp.close()

    return align_samples 


def make_a3m(fp, sample: Union[Alignment, list], header='>', fixed_width=False, fixed_width_column_count=80):
    """
    Write an A3M file given a list of Alignment objects
    sample: List of Alignment objects
    header: The header character for each sample. It is recommended not to change this
    fixed_width: Controls if data is written with line breaks every n characters, or not
    fixed_width_column_count: Controls how often the data is broken up.
    """
    if type(sample) is not list:
        sample = [sample]

    for si in sample:
        sample_data = si.data
        if fixed_width:
            sample_data = '\n'.join([sample_data[i:i+fixed_width_column_count] for i in range(0, len(sample_data), fixed_width_column_count)]) 
        fp.write(f"{header}{si.name}\n{sample_data}\n")
        fp.flush()

