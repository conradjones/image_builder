import unittest.mock
from util import util


class CleanupTest(unittest.TestCase):
    def test_cleanup(self):
        i = 0
        with util.cleanup() as the_cleanup:
            the_cleanup.add(lambda: i = 1)




if __name__ == '__main__':
    unittest.main()
