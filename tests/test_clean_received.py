from approvaltests import verify
import os

from clean_received import *


def test_empty_dir(tmpdir):
    clean_received(tmpdir)
    verify(str(os.listdir(tmpdir)))


def test_simple_received_file(tmpdir):
    received_file = os.path.join(tmpdir, "a.received.txt")
    with open(received_file, "w") as f:
        f.write("foo")
    clean_received(tmpdir)
    verify(str(os.listdir(tmpdir)))


def test_mix_of_files(tmpdir):
    received_file = os.path.join(tmpdir, "a.received.txt")
    with open(received_file, "w") as f:
        f.write("foo")
    approved_file = os.path.join(tmpdir, "a.approved.txt")
    with open(approved_file, "w") as f:
        f.write("bar")
    clean_received(tmpdir)
    verify(str(os.listdir(tmpdir)))

