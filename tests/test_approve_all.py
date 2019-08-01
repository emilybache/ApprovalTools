import os

from approvaltests import verify
from approve_all import *


def test_empty_dir(tmpdir):
    approve_all(tmpdir)
    verify(os.listdir(tmpdir))


def test_nothing_to_approve(tmpdir):
    approved_file = os.path.join(tmpdir, "a.approved.txt")
    with open(approved_file, "w") as f:
        f.write("foo")
    approve_all(tmpdir)
    verify(str(os.listdir(tmpdir)))


def test_approve_one_file(tmpdir):
    received_file = os.path.join(tmpdir, "a.received.txt")
    with open(received_file, "w") as f:
        f.write("foo")
    approve_all(tmpdir)

    all_files = os.listdir(tmpdir)
    verify(str(all_files))


def test_approve_one_file_with_distractions(tmpdir):
    received_file = os.path.join(tmpdir, "a.received.txt")
    with open(received_file, "w") as f:
        f.write("foo")
    other_file = os.path.join(tmpdir, "bar.xxx.txt")
    with open(other_file, "w") as f:
        f.write("bar")

    approve_all(tmpdir)

    all_files = os.listdir(tmpdir)
    verify(str(all_files))
