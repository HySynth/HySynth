from hysynth.pwl.library import find_contiguous_blocks, find_identical_blocks


def test_find_contiguous_blocks():
    """ This tests the find contiguous block function """

    first_seq = [1, 2, 3, 4, 6, 6, 6, 7, 8, 10, 20, 10, 100]
    assert list(find_contiguous_blocks(first_seq)) == [(1, 4), (6, 8)]

    second_seq = [1, 2, 3, 4, 5, 6, 7]
    assert list(find_contiguous_blocks(second_seq)) == [(1, 7)]