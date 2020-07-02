#!/usr/bin/env python3

import argparse
import os
import re
import difflib


class DiffGroup:
    def __init__(self, diff, test_names=None):
        self.diff = diff
        if test_names:
            self.test_names = set(test_names)
        else:
            self.test_names = set()

    def add_test(self, test_name):
        self.test_names.add(test_name)

    def __repr__(self):
        return repr(sorted(self.test_names))


def analyze_groups(diffs):
    groups = {}
    for test_name1, diff1 in diffs.items():
        for test_name2, diff2 in diffs.items():
            if test_name1 == test_name2:
                continue
            # the diffs must be identical, not merely overlapping. This gives the test operator the best information
            if diff1 == diff2:
                if diff1 not in groups.keys():
                    groups[diff1] = DiffGroup(diff1)
                groups[diff1].add_test(test_name1)
                groups[diff1].add_test(test_name2)

    return groups


def report_diffs(diff_groups):
    result = ""
    result += "Failures can be grouped. All tests in this list have exactly the same diff:\n"
    group_count = 0
    for group_name, group in diff_groups.items():
        result += f"Group #{group_count+1}:\n"
        result += "\n".join(sorted(group.test_names))
        result += f"\nAll share this diff:\n"
        result += group.diff
        result += "\n"
        group_count += 1

    return result


def report_failures(failures, groups):
    result = "Failed tests:\n"
    for test_name, _ in failures.items():
        result += f"{test_name}\n"

    if groups:
        result += "\n-----------------\n"
        result += report_diffs(groups)

    result += "\n-----------------\n"
    result += f"Total test failure count: {len(failures)}"
    return result


def analyze(folder):
    regex = re.compile(r"(.*)\.received(\..*)")
    failures = {}
    for root, dirs, files in os.walk(folder):
        for received_filename in files:
            matches = re.findall(regex, received_filename)
            if matches:
                test_name = matches[0][0]
                file_extension_including_dot = matches[0][1]

                received_file = str(os.path.join(root, received_filename))
                with open(received_file, encoding="utf-8") as f:
                    received_text = f.readlines()

                approved_filename = test_name + ".approved" + file_extension_including_dot
                approved_file = str(os.path.join(root, approved_filename))
                if os.path.exists(approved_file):
                    with open(approved_file, encoding="utf-8") as f:
                        approved_text = f.readlines()
                else:
                    approved_text = ""
                failures[test_name] = create_diff(received_text, approved_text)

    if not failures:
        return f"No failing tests found."
    else:
        failure_groups = analyze_groups(failures)
        return report_failures(failures, failure_groups)


def create_diff(received_text, approved_text):
    differ = difflib.Differ()
    diff = "".join(differ.compare(approved_text, received_text))
    return diff


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("directory",
                        help="the directory where the test results are (it will also search subdirectories)",
                        default=os.getcwd())

    args = parser.parse_args()
    directory = args.directory or os.getcwd()

    if not os.path.exists(directory):
        print(f"directory not found {directory}")
        sys.exit(-1)

    print(f"analyzing test results found in folder {directory}")
    print(analyze(directory))
