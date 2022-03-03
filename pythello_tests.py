import unittest
import pythello

class PythelloTests(unittest.TestCase):

    def setUp(self):
        self.game = pythello.ReversAI(8, 8)
        self.instance = self.game.newPos()

    def test_board_sizes(self):


if __name__ == '__main__':
    unittest.main()