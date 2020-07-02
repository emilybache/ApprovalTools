#!/usr/bin/env python3

import argparse
import os
import re


def clean_received(directory, verbose=True):
    regex = re.compile(r"(.*)\.received(\..*)")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            matches = re.findall(regex, filename)
            if matches:
                test_name = matches[0][0]
                file_extension_including_dot = matches[0][1]

                received_file = str(os.path.join(root, filename))
                os.remove(received_file)
                if verbose:
                    print(f"removed {test_name}.received{file_extension_including_dot}")


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory to clean files in")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress all output messages")

    args = parser.parse_args()
    directory = args.directory or os.getcwd()
    verbose = not args.quiet

    if not os.path.exists(directory):
        print(f"directory not found {directory}")
        sys.exit(-1)

    if verbose:
        print(f"cleaning received files in folder {directory}")
    clean_received(directory, verbose)
