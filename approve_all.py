import os
import re
import shutil


def approve_all(directory):
    regex = re.compile("(.*\.)received(\..*)")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            matches = re.findall(regex, filename)
            if matches:
                new_filename = matches[0][0] + "approved" + matches[0][1]
                shutil.copyfile(str(os.path.join(root, filename)),
                                str(os.path.join(root, new_filename)))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.getcwd()
    approve_all(directory)
