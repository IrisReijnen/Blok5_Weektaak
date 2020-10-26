# Michelle Memelink
# Iris Reijnen
# B. van Velzen
# 13-10-2020
# ---------------------------------
# CLI = Command Line Interface
# ---------------------------------
# Pipeline loop
# Takes a fasta file with sequences and filters through them with
# tools like muscle, HMMbuild and HMMsearch.
# Loops with a newly created fasta file by HMMsearch until there's not
# a lot of sequences left to add.
# ---------------------------------
# To start the program, enter this command on the CLI.
# Replace single quotes with own input.
# python3 'pipeline_file.py' 'DeltaBLAST_file.fasta' 'path/to/seq_db'
import os
import subprocess
from sys import argv


def muscle(input_fasta, output_msa):
    """Run muscle via the CLI
    arguments:
    input_fasta - str - fasta voor msa
    output_msa -str- naam output met msa
    """
    print("--- STARTING MSA ---")
    cmd_msa = "muscle -in {} -out {}".format(input_fasta, output_msa)
    subprocess.check_call(cmd_msa, shell=True)
    return


def hmmbuild(output_hmmbuild, output_msa):
    """Run HMMbuild via the CLI
    Arguments:
    output_hmmbuild - str - HMMbuild output
    output_msa - str - name output of MSA
    """
    print("--- STARTING HMMBUILD ---")
    cmd_hmmbuild = "hmmbuild  {}  {}".format(output_hmmbuild, output_msa)
    subprocess.check_call(cmd_hmmbuild, shell=True)
    return


def hmmsearch(output_hmmbuild, seq_db, output_hmmsearch_raw,
              output_hmmsearch_fasta):
    """Run HMMsearch via the CLI
    Converts the HMMsearch output to fastaa with esl-reformat.
    Arguments:
    output_hmmbuild - str - output file of HMMbuild
    seq_db - str - path to sequence database file used
    output_hmmsearch_raw - str - name of HMMsearch file created
    output_hmmsearch_fasta - str - name of HMMsearch fasta created
    """
    print("--- STARTING HMMSEARCH ---")

    cmd_hmmsearch = "hmmsearch -A {} -E 1.0e-26 {} {} ".format(output_hmmsearch_raw,
                                                    output_hmmbuild,
                                                    seq_db)
    subprocess.check_call(cmd_hmmsearch, shell=True)

    cmd_hmmsearch_omzetten_fasta = "./esl-reformat fasta {} > {} ".format(
        output_hmmsearch_raw, output_hmmsearch_fasta)
    subprocess.check_call(cmd_hmmsearch_omzetten_fasta, shell=True)
    return


def test_double_accessions(hmm_fasta, result_fasta):
    """Adds new sequences to file, filters duplicates out.
    :param result_fasta: Het oude bestand
    :param hmm_fasta: Het bestand met nieuwe en misschien dubbele sequenties
    :returns amount_added: amount of sequences added.
    """
    print("--- WRITING TO FILE ---")

    hmm_headers_seqs = {}
    seq = ""
    with open(hmm_fasta, 'r') as hmm_file:
        for line in hmm_file:
            if not line.startswith(">"):
                seq += line
            else:
                if seq:
                    hmm_headers_seqs[header] = seq
                header = line
                seq = ""
        hmm_headers_seqs[header] = seq

    list_old_accs = []
    with open(result_fasta, 'r') as result_file:
        # Get accession codes of deltablast
        for line in result_file:
            if line.startswith(">"):
                list_old_accs.append(line.split(":")[0].replace(">", ""))

    amount_added = 0
    with open(result_fasta, 'a') as result_file:
        # Check if HMM accession codes are in DeltaBLAST,
        # if not add to new file.
        for hmm_header in hmm_headers_seqs.keys():
            hmm_accession = hmm_header.split("/")[0].replace(">", "")
            if hmm_accession not in list_old_accs:
                amount_added += 1
                result_file.write(hmm_header.replace("/", ":"))
                result_file.write(hmm_headers_seqs[hmm_header])

    return amount_added


def loop_necessary(amount_added, result_fasta, input_fasta, seq_db):
    """Check if looping is necessary by
    observing amount of sequences added.
    Arguments:
    amount_added - int - counts the amount of sequences added to file
    results_fasta - str - name of loop fasta file
    input_fasta - str - name of starting fasta file
    seq_db - str - path to database fasta file
    """
    print("--- CHECKING IF LOOPING IS NECESSARY ---")
    if amount_added >= 5:
        print("More than 5 sequences added, looping.")
        loop(result_fasta, input_fasta, seq_db)
    else:
        print("Not more than 5 sequences added, finishing up with an MSA.")
        muscle(result_fasta, "final_msa.aln")


def loop(result_fasta, input_fasta, seq_db):
    """Loops the pipeline.
    Asks if a new loop is necessary.
    Arguments:
    results_fasta - str - name of loop fasta file
    input_fasta - str - name of starting fasta file
    seq_db - str - path to database fasta file
    """
    print("--- LOOPING ---")

    output_msa = "msa_output.aln"
    output_hmmbuild = "hmmbuild_profile.hmm"
    output_hmmsearch_raw = "hmmsearch_raw"
    output_hmmsearch_fasta = "hmmsearch.fasta"

    muscle(input_fasta, output_msa)
    hmmbuild(output_hmmbuild, output_msa)
    hmmsearch(output_hmmbuild, seq_db, output_hmmsearch_raw,
              output_hmmsearch_fasta)
    amount_added = test_double_accessions(output_hmmsearch_fasta, result_fasta)

    loop_necessary(amount_added, result_fasta, input_fasta, seq_db)


def main():
    # CLI:
    # python3 "sequentie_aligned_refseq.txt"(=1) "path/to/refseqdb"(=2)
    result_fasta = "result.fasta"
    try:
        input_fasta = argv[1]
        seq_db = argv[2]
    except IndexError:
        print("Insufficient arguments added, stopping program")
        exit()

    if os.path.isfile(result_fasta):
        os.remove(result_fasta)
    os.mknod(result_fasta)
    with open(input_fasta, 'r') as input_file:
        with open(result_fasta, 'w') as output_file:
            for line in input_file:
                output_file.write(line)

    loop(result_fasta, input_fasta, seq_db)


main()
