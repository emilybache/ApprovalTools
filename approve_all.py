#!/usr/bin/env python3

import os
import re
import shutil
import argparse


def approve_all(directory, verbose=True, verify=False):
    approved_token = ".verified" if verify else ".approved"
    regex = re.compile(r"(.*)\.received(\..*)")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            matches = re.findall(regex, filename)
            if matches:
                test_name = matches[0][0]
                file_extension_including_dot = matches[0][1]

                new_filename = test_name + approved_token + file_extension_including_dot
                received_file = str(os.path.join(root, filename))
                approved_file = str(os.path.join(root, new_filename))
                shutil.copyfile(received_file,
                                approved_file)
                if verbose:
                    print(f"approving {test_name}")


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory to approve files in")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress all output messages")
    parser.add_argument("-v", "--verify", action="store_true", help="Use Verify format for approved files, ie .verified instead of .approved")

    args = parser.parse_args()
    directory = args.directory or os.getcwd()
    verbose = not args.quiet

    if not os.path.exists(directory):
        print(f"directory not found {directory}")
        sys.exit(-1)

    if verbose:
        print(f"approving all received files in folder {directory}")
    approve_all(directory, verbose, args.verify)
