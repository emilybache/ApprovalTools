import argparse
import os
import re
import io
import difflib
from pprint import pprint


class TestFailure:
    def __init__(self, received_text, approved_text):
        self.received_text = received_text
        self.approved_text = approved_text
        self.diff = None

    def find_diff(self):
        if not self.diff:
            self.diff = find_diff(self.received_text, self.approved_text)
        return self.diff


def find_diff(received_text, approved_text):
    differ = difflib.Differ()
    return "\n".join(
            differ.compare(
                approved_text.splitlines(),
                received_text.splitlines()
            )
        )


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


def analyze_diffs(failures):
    diffs = {}
    for test_name, failure in failures.items():
        diff = failure.find_diff()
        diffs[test_name] = diff

    groups = analyze_groups(diffs)
    return groups


def analyze_groups(diffs):
    groups = {}
    for test_name1, diff1 in diffs.items():
        for test_name2, diff2 in diffs.items():
            if test_name1 == test_name2:
                continue
            # the diffs must be identical, not merely overlapping. This gives the test operator the best information
            if diff1 == diff2:
                groups[diff1] = DiffGroup(diff1, [test_name1, test_name2])

    return groups


def report_diffs(diff_groups):
    result = ""
    result += "Failures can be grouped.\n"
    group_count = 0
    for group_name, group in diff_groups.items():
        result += f"Group #{group_count+1}:\n"
        result += "\n".join(sorted(group.test_names))
        result += f"\nAll share this diff:\n"
        result += group.diff
        result += "\n"
        group_count += 1

    return result


def report_failures(failures):
    result = "Failed tests:\n"
    for test_name, failure in failures.items():
        result += f"{test_name}\n"

    groups = analyze_diffs(failures)
    if groups:
        result += report_diffs(groups)

    result += "\n-----------------\n"
    result += f"Total test failure count: {len(failures)}"
    return result


def analyze(directory):
    regex = re.compile(r"(.*)\.received(\..*)")
    failures = {}
    for root, dirs, files in os.walk(directory):
        for received_filename in files:
            matches = re.findall(regex, received_filename)
            if matches:
                test_name = matches[0][0]

                received_file = str(os.path.join(root, received_filename))
                with open(received_file, encoding="utf-8") as f:
                    received_text = f.read()

                approved_filename = test_name + ".approved" + matches[0][1]
                approved_file = str(os.path.join(root, approved_filename))
                if os.path.exists(approved_file):
                    with open(approved_file, encoding="utf-8") as f:
                        approved_text = f.read()
                else:
                    approved_text = ""
                failures[test_name] = TestFailure(received_text, approved_text)

    if not failures:
        return f"No failing tests found."
    else:
        return report_failures(failures)


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory where the test results are (it will also search subdirectories)")

    args = parser.parse_args()
    directory = args.directory or os.getcwd()

    if not os.path.exists(directory):
        print(f"directory not found {directory}")
        sys.exit(-1)

    print(f"analyzing test results found in folder {directory}")
    analyze(directory)
