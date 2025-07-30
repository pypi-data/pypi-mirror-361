import unittest
from listdupes.main import ListDupes, cond_hash
from pathlib import Path

here = Path(__file__).parent

class TestCondHash(unittest.TestCase):
    def test_hash_file(self):
        file = here / "data/hello.txt"
        self.assertEqual(cond_hash(file), (str(file),"181210f8f9c779c26da1d9b2075bde0127302ee0e3fca38c9a83f5b1dd8e5d3b"))

    def test_hash_directory(self):
        file = here / "data"
        self.assertIsNone(cond_hash(file))


class TestListDupes(unittest.TestCase):
    def test_correct_number_of_files(self):
        ld = ListDupes()
        for _ in ld.find_duplicates(here / "data"):
            pass
        self.assertEqual(ld.scanned, 4)

    def test_correct_number_of_dupes(self):
        ld = ListDupes()
        for _ in ld.find_duplicates(here / "data"):
            pass
        self.assertEqual(ld.found, 2)
    

if __name__ == "__main__":
    unittest.main()
    print(f"running in {here.absolute()}")
