import pytest
from jevoss.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["--help"],
        ["eval", "--help"],
        ["probe", "--help"],
        ["calibrate", "--help"],
        ["compare", "--help"],
        ["ask", "--help"],
    ],
)
def test_help_exits_zero(argv):
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 0
