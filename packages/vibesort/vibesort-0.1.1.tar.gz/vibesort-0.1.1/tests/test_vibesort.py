from vibesort import vibesort
from dotenv import load_dotenv

load_dotenv()


def test_vibesort():
    assert vibesort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
    assert vibesort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert vibesort([1, 3, 2, 5, 4]) == [1, 2, 3, 4, 5]


def test_long_array():
    assert vibesort([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert vibesort([10, 9, 8, 7, 6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert vibesort([1, 3, 2, 5, 4, 7, 6, 9, 8, 10]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
