import argparse
import os

from src.processors import Processor
from src.errors import ConstructorError

if __name__ == "__main__":
    current_path = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to a file or a directory to rename", type=str)
    parser.add_argument("-pt", "--path_translator", help="path to an user's translator", type=str)
    parser.add_argument("-l", "--layer", help="Set layer to process in depth", type=int)
    parser.add_argument("-ed", "--exclude_dirs",
                        help="write 'yes' or 'y' if you want to exclude directories from processing. "
                             "Else write 'no' or 'n'",
                        type=str)
    parser.add_argument("-ef", "--exclude_files",
                        help="write 'yes' or 'y' if you want to exclude files from processing. "
                             "Else write 'no' or 'n'", type=str)
    args = parser.parse_args()

    ex_dirs = False
    if args.exclude_dirs == "yes":
        ex_dirs = True

    ex_files = False
    if args.exclude_files == "yes":
        ex_files = True

    try:
        proc = Processor(
            args.path,
            None,
            args.path_translator,
            args.layer,
            ex_dirs,
            ex_files
        )
        proc.run()
    except ConstructorError as e:
        e.print_message()
