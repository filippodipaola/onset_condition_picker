import csv
from os import listdir
from os.path import isfile, join
import argparse

VERBOSE = True

def list_StopTask_csv_files(directory):
    """
    Method to get all csv files contains stop tasks from selected directory
    :param directory: path to the directory containing csv files.
    :return: a list of all csv files containing stop task.
    """
    stoptask_csv = []
    for f in listdir(directory):
        if isfile(join(directory, f)) and f.endswith(".csv") and "StopTask" in f:
            stoptask_csv.append(join(directory, f))

    return stoptask_csv

def check_for_failed_stop(a_csv_row):
    """
    Change this function if failed_stop criteria changes.
    :param a_csv_row:
    :return: Boolean
    """
    return a_csv_row['StopSignal'] == "Yes" and a_csv_row['IsCorrect'] == "No"

def check_for_successful_stop(a_csv_row):
    """
    Change this function if successful_stop criteria changes.
    :param a_csv_row:
    :return: Boolean
    """
    return a_csv_row['StopSignal'] == "Yes" and a_csv_row['IsCorrect'] == "Yes"

def check_for_go_correct(a_csv_row):
    """
    Change this function if go_correct criteria changes.
    :param a_csv_row:
    :return: Boolean
    """
    return a_csv_row['StopSignal'] == "No" and a_csv_row['IsCorrect'] == "Yes"


def process_csv_file(csv_r, output_filename_format):
    """
    Processes a csv file reader using the above functions.
    The method looks on each row of the csv file and checks
    if the above function conditions are met, then outputs
    the time at start of trail values into a txt file.
    :param csv_r: csv dictreader object
    :param output_filename_format:  the formattable filename of the output
    :return: None
    """

    global VERBOSE
    go_correct_times = []
    successful_stop_times = []
    failed_stop_times = []

    for line in csv_r:
        time_at_start = line['TimeAtStartOfTrial']
        if check_for_failed_stop(line):
            failed_stop_times.append(time_at_start)

        elif check_for_successful_stop(line):
            successful_stop_times.append(time_at_start)

        elif check_for_go_correct(line):
            go_correct_times.append(time_at_start)

    with open(output_filename_format.replace('!', "failed_stop"), "w") as out_f:
        print(f"Outputting file: {out_f.name}") if VERBOSE else None
        out_f.write("\n".join(failed_stop_times))

    with open(output_filename_format.replace('!', "successful_stop"), "w") as out_f:
        print(f"Outputting file: {out_f.name}") if VERBOSE else None
        out_f.write("\n".join(successful_stop_times))

    with open(output_filename_format.replace('!', "go_correct"), "w") as out_f:
        print(f"Outputting file: {out_f.name}") if VERBOSE else None
        out_f.write("\n".join(go_correct_times))



def get_filename_prefix(file_name, out_dir=None):
    """
    Generates a formattable output file name used to generate
    the three output files. Handles RTAD where the participant
    name is fucked up.
    :param file_name: the filename of the current csv file being processed
    :param out_dir: Optional, used when arguments specify output directory
    :return: A formattable output file string
    """
    if "/" in file_name:
        file_name = file_name.split("/")[-1]

    if "\\" in file_name:
        file_name = file_name.split("\\")[-1]

    spl_file_name = file_name.split("_")
    stoptask_index = spl_file_name.index("StopTask")
    participant = spl_file_name[stoptask_index + 1]
    if file_name.startswith("RTAD"):
        participant = f"RTAD{participant}"
    visit_letter = spl_file_name[stoptask_index+2][0]
    visit = "pre" if visit_letter in ['A', 'B'] else "post"
    if out_dir:
        return join(out_dir, f"{participant}_!_{visit}.txt")
    return f"{participant}_!_{visit}.txt"


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Pick onset data from csv files.")
    parser.add_argument("-d", "--directory", help="The directory containing the stop tasks.")
    parser.add_argument("-o", "--output_dir",
                        help="The directory (MUST EXIST) to output the task times.")
    parser.add_argument("-s", "--silent", action='store_const', const=True,
                        help="Add this argument if you want the script to"
                             " NOT output what it's doing")
    args = parser.parse_args()
    csv_files = list_StopTask_csv_files(args.directory)
    out_dir = None
    if args.output_dir:
        out_dir = args.output_dir

    if args.silent:
        VERBOSE = False

    for csvf in csv_files:
        print(f"Processing file: {csvf}") if VERBOSE else None
        output_filename_format = get_filename_prefix(csvf, out_dir)
        with open(csvf, "r") as open_csvf:
            csv_r = csv.DictReader(open_csvf)
            process_csv_file(csv_r, output_filename_format)