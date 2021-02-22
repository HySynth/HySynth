import pytest
from hysynth.pwl.library import contract_path


def test_contract_path():
    """ Test the contracting function """

    seq1 = "AAAAAAAAAAAAAAAAAAAAAAAA"
    assert contract_path(seq1) == list("A")

    seq2 = "AAAAAAAAAAAAABBBBBBBBBB"
    assert contract_path(seq2) == list("AB")

    seq3 = "AAABBBBBAAAAAAAACCCABC"
    assert contract_path(seq3) == list("ABACABC")

    seq4 = ["A", "A", "B", "B"]
    assert contract_path(seq4) == list("AB")


def test_contract_path_single_item():
    seq5 = ["A"]
    assert contract_path(seq5) == list("A")


def test_contract_path_empty_error():
    seq6 = []
    with pytest.raises(ValueError) as excinfo:
        assert contract_path(seq6) == list()

    assert 'Empty iterable!' in str(excinfo.value)