import os

from approvaltests import verify

from analyze import analyze, analyze_groups, DiffGroup, report_diffs, create_diff, identical


def test_empty_dir(tmpdir):
    analysis = analyze(tmpdir)
    verify(analysis)


def test_only_approved_files(tmpdir):
    approved_file = os.path.join(tmpdir, "a.approved.txt")
    with open(approved_file, "w") as f:
        f.write("foo")
    analysis = analyze(tmpdir)
    verify(analysis)


def test_one_failure(tmpdir):
    test_name = "a"
    write_received_file(tmpdir, test_name, "foo")
    write_approved_file(tmpdir, test_name, "bar")
    analysis = analyze(tmpdir)
    verify(analysis)


def test_two_identical_failures(tmpdir):
    test_name = "a"
    write_received_file(tmpdir, test_name, "foo\n")
    write_approved_file(tmpdir, test_name, "bar\n")
    test_name = "b"
    write_received_file(tmpdir, test_name, "foo\n")
    write_approved_file(tmpdir, test_name, "bar\n")
    analysis = analyze(tmpdir)
    verify(analysis)


def test_missing_approved_file(tmpdir):
    test_name = "a"
    write_received_file(tmpdir, test_name, "foo")
    analysis = analyze(tmpdir)
    verify(analysis)


def write_received_file(tmpdir, test_name, file_contents):
    approval_file_type = "received"
    return write_approval_file(tmpdir, test_name, approval_file_type, file_contents)


def write_approved_file(tmpdir, test_name, file_contents):
    approval_file_type = "approved"
    return write_approval_file(tmpdir, test_name, approval_file_type, file_contents)


def write_approval_file(tmpdir, test_name, approval_file_type, file_contents):
    received_file = os.path.join(tmpdir, test_name + "." + approval_file_type + ".txt")
    with open(received_file, "w") as f:
        f.write(file_contents)
    return received_file


def test_find_diff_single_lines():
    failure = create_diff("foo\n".splitlines(True), "bar\n".splitlines(True))
    verify(failure)


def test_find_diff_multi_lines():
    failure = create_diff("foo\nbar\nbaz\n".splitlines(True), "bar\n".splitlines(True))
    verify(failure)


def test_groups_two_tests_same_diff():
    diff1 = """\
- bar
+ foo
"""
    diffs = {"a": diff1, "b": diff1}
    verify(str(analyze_groups(diffs, identical)))

def test_groups_two_tests_different_diff():
    diff1 = """\
- bar
+ foo
"""
    diff2 = """\
- baz
"""

    diffs = {"a": diff1, "b": diff2}
    verify(str(analyze_groups(diffs, identical)))


def test_groups_larger_number_of_tests():
    diff1 = """\
- bar
+ foo
"""
    diff2 = """\
- baz
"""

    diffs = {"a": diff1, "b": diff2, "c": diff2, "d": diff2, "e": diff1}
    verify(str(analyze_groups(diffs, identical)))


def test_overlapping_diffs():
    diff1 = """\
- bar
+ foo
"""
    diff2 = """\
+ foo
"""

    diffs = {"a": diff1, "b": diff2}
    verify(str(analyze_groups(diffs, identical)))


def test_multiple_overlapping_diffs():
    diff1 = """\
- bar
+ foo
"""
    diff2 = """\
+ foo
"""
    diff3 = """\
- bar
"""
    diffs = {"a": diff1, "b": diff2, "c": diff3}
    verify(str(analyze_groups(diffs, identical)))


def test_report_diffs():
    diff1 = '+ foo\n'
    diff2 = '- bar\n'
    diffs = {diff1: DiffGroup(diff1, ['a', 'b']), diff2: DiffGroup(diff2, ['a', 'c'])}
    verify(report_diffs(diffs))
