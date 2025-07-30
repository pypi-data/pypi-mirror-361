from barnone import ColoredProgressBar

COLOR_CODE = "\033[38;2;"
COLOR_RESET = "\033[0m"


def test_colored_pb_is_pb_instance():
    pb = ColoredProgressBar(total=10)
    assert isinstance(pb, ColoredProgressBar)


def test_cpb_passes_args_to_pb():
    pb = ColoredProgressBar(10, prefix="Test", suffix="Done")
    assert pb.total == 10
    assert pb.prefix == "Test"
    assert pb.suffix == "Done"


def test_cpb_bar_has_color(capsys):
    pb = ColoredProgressBar(total=10)
    pb.update(1)

    output, _ = capsys.readouterr()
    last_line = output.splitlines()[-1]
    split = last_line.split("]")[0]
    assert COLOR_CODE in split
    assert COLOR_RESET in split


def test_cpb_percentage_has_color(capsys):
    pb = ColoredProgressBar(total=10)
    pb.update(1)

    output, _ = capsys.readouterr()
    last_line = output.splitlines()[-1]
    split = last_line.split("]")[1]

    assert COLOR_CODE in split
    assert COLOR_RESET in split


def test_cpb_prefix_has_no_color(capsys):
    pb = ColoredProgressBar(total=10, prefix="Test")
    pb.update(1)

    output, _ = capsys.readouterr()
    last_line = output.splitlines()[-1]
    split = last_line.split("[")[0]

    assert COLOR_CODE not in split
    assert COLOR_RESET not in split


def test_cpb_eta_has_no_color(capsys):
    pb = ColoredProgressBar(total=10, prefix="Test")
    pb.update(1)

    output, _ = capsys.readouterr()
    last_line = output.splitlines()[-1]
    split = last_line.split("/")[1]

    assert COLOR_CODE not in split
    assert COLOR_RESET not in split
