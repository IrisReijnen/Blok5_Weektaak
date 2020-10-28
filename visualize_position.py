# Michelle Memelink
# Iris Reijnen
# bvvbin
# 24-10-2020
# ---------------------------------
# CLI = Command Line Interface
# ---------------------------------
# Takes MSA file with sequences and count the amount of each
# aminoacid on a specific position.
# Visualizes this in a pie chart.
# ---------------------------------
# To start the program, enter this command on the CLI.
# Replace single quotes with own input.
# python3 create_dict.py 'final_msa.aln' 'positie_nummer'


import os
from sys import argv
import matplotlib.pyplot as plt


def main():
    # Command line interface command Ubuntu:
    # python3 create_dict.py "final_msa.aln" "positie_nummer"
    file1 = argv[1]
    pos = int(argv[2]) - 1
    file2 = "dictionary_output_" + file1 + ".txt"
    dict_pos = {}
    seq = ""
    with open(file1, 'r') as file:
        for line in file:
            if not line.startswith(">"):
                seq += line.replace("\n", "")
            else:
                if seq:
                    if seq[pos] not in dict_pos.keys():
                        dict_pos[seq[pos]] = 1
                    else:
                        dict_pos[seq[pos]] += 1
                seq = ""
    print("-" * 79)
    print("Dictionary creation complete of position {}:".format(pos + 1))
    print(dict_pos)
    print("-" * 79)
    plt.pie(dict_pos.values(), labels=dict_pos.keys(), autopct='%1.1f%%')
    plt.title("Test")
    plt.show()


main()
