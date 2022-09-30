#!/usr/bin/env python3

import argparse
import os
import re
import difflib


class DiffGroup:
    def __init__(self, group_type, diff, test_names=None):
        self.group_type = group_type
        self.diff = diff
        if test_names:
            self.test_names = set(test_names)
        else:
            self.test_names = set()

    def add_test(self, test_name):
        self.test_names.add(test_name)

    def __repr__(self):
        return repr(sorted(self.test_names))


def report_diffs(diff_groups):
    result = ""
    group_count = 0
    for group_name, group in diff_groups.items():
        result += f"Group #{group_count + 1} ({len(group.test_names)} tests):\n"
        result += "\n".join(sorted(group.test_names))
        result += f"\n{group.group_type}:\n"
        result += f"{group.diff}"
        result += "\n"
        group_count += 1

    return result


def report_failures(failures, identical_groups, similar_groups):
    result = "Failed tests:\n"
    for test_name, _ in failures.items():
        result += f"{test_name}\n"

    if identical_groups:
        result += "\n-----------------\n"
        result += "Failures can be grouped. All tests in this list have exactly the same diff:\n"
        result += report_diffs(identical_groups)
    if similar_groups:
        result += "\n-----------------\n"
        result += "Additionally, tests in this list have similarities in their diffs\n"
        result += report_diffs(similar_groups)

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
                if test_name.endswith("DotNet6_0"):
                    test_name = test_name.replace(".DotNet6_0", "")
                file_extension_including_dot = matches[0][1]

                received_file = str(os.path.join(root, received_filename))
                received_text = read_lines_from_file(received_file)

                approved_filename = test_name + ".approved" + file_extension_including_dot
                verified_filename = test_name + ".verified" + file_extension_including_dot
                approved_file = str(os.path.join(root, approved_filename))
                verified_file = str(os.path.join(root, verified_filename))
                if os.path.exists(approved_file):
                    approved_text = read_lines_from_file(approved_file)
                elif os.path.exists(verified_file):
                    approved_text = read_lines_from_file(verified_file)
                else:
                    approved_text = ""
                failures[test_name] = reduce_diff(create_diff(received_text, approved_text))

    if not failures:
        return f"No failing tests found."
    else:
        identical_failure_groups = analyze_groups(failures, identical)
        similar_failure_groups = analyze_groups(failures, similar)
        return report_failures(failures, identical_failure_groups, similar_failure_groups)


def analyze_groups(diffs, comparison_function):
    groups = {}
    for test_name1, diff1 in diffs.items():
        for test_name2, diff2 in diffs.items():
            if test_name1 == test_name2:
                continue
            group_type, diff = comparison_function(diff1, diff2)
            if group_type is not None:
                group_name = f"{group_type}{diff}"
                if group_name not in groups.keys():
                    groups[group_name] = DiffGroup(group_type, diff)
                groups[group_name].add_test(test_name1)
                groups[group_name].add_test(test_name2)

    return groups


def read_lines_from_file(received_file):
    with open(received_file, encoding="utf-8") as f:
        received_text = f.readlines()
        if received_text and not received_text[-1].endswith('\n'):
            received_text[-1] = received_text[-1] + '\n'
    return received_text


def identical(diff1, diff2):
    if diff1 == diff2:
        return "They share this diff", diff1
    return None, None


def similar(diff1, diff2):
    diff_type, diff = identical(diff1, diff2)
    if diff_type is not None:
        return None, None

    if added_lines(diff1) == added_lines(diff2):
        return "They have added lines", added_lines(diff1)
    if removed_lines(diff1) == removed_lines(diff2):
        return "They have removed lines", removed_lines(diff1)

    if diff1 in diff2:
        return "There are similar lines", diff1
    return None, None


def added_lines(diff):
    added = lines_with_prefix(diff, "+ ")
    return added


def removed_lines(diff):
    removed = lines_with_prefix(diff, "- ")
    return removed


def lines_with_prefix(diff, prefix):
    added = filter(lambda line: line[:2] == prefix, diff.splitlines())
    return list(map(lambda line: line + "\n", added))


def create_diff(received_text, approved_text):
    differ = difflib.Differ()
    diff = "".join(differ.compare(approved_text, received_text))
    return diff


def reduce_diff(diff):
    """remove the lines added for context and just keep the lines that show the actual differences """
    new_diff = ""
    for line in diff.splitlines():
        if line[:2] in ["  ", "? "]:
            continue
        new_diff += line + "\n"
    return new_diff


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
