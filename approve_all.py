#!/usr/bin/env python3

import os
import re
import shutil
import argparse


def approve_all(directory, verbose=True):
    regex = re.compile("(.*\.)received(\..*)")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            matches = re.findall(regex, filename)
            if matches:
                new_filename = matches[0][0] + "approved" + matches[0][1]
                received_file = str(os.path.join(root, filename))
                approved_file = str(os.path.join(root, new_filename))
                shutil.copyfile(received_file,
                                approved_file)
                if verbose:
                    print(f"approving {matches[0][0]}")


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory to approve files in")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress all output messages")

    args = parser.parse_args()
    directory = args.directory or os.getcwd()
    verbose = not args.quiet

    if not os.path.exists(directory):
        print(f"directory not found {directory}")
        sys.exit(-1)

    if verbose:
        print(f"approving all received files in folder {directory}")
    approve_all(directory, verbose)
