import unittest
from tree2cmd.cli import convert_tree_to_commands
import sys
sys.path.insert(0, ".")

class TestTreeToCommands(unittest.TestCase):

    def test_basic_tree(self):
        with open('sample.txt', 'r') as f:
            tree = f.read()
        expected = [
            'mkdir -p "Project/"',
            'mkdir -p "Project/src/"',
            'touch "Project/src/main.py"',
            'touch "Project/README.md"'
        ]
        output = convert_tree_to_commands(tree, dry_run=True, verbose=False)
        self.assertEqual(output, expected)

    def test_no_crash_on_empty(self):
        output = convert_tree_to_commands("", dry_run=True)
        self.assertEqual(output, [])

if __name__ == "__main__":
    unittest.main
