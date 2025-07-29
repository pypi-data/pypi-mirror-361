import unittest
from unittest.mock import patch
import pytest
from cedbox.easymorse import EasyMorse, MORSE_CODE_DICT


class TestEasyMorse(unittest.TestCase):
    """Tests for EasyMorse class"""

    def test_char_to_seq_letter(self):
        """Test char_to_seq with a letter"""
        result = EasyMorse.char_to_seq('A')
        self.assertEqual(result, [1, -3, 3])

    def test_char_to_seq_number(self):
        """Test char_to_seq with a number"""
        result = EasyMorse.char_to_seq('1')
        self.assertEqual(result, [1, -3, 3, -3, 3, -3, 3, -3, 3])

    def test_char_to_seq_symbol(self):
        """Test char_to_seq with a symbol"""
        result = EasyMorse.char_to_seq('?')
        self.assertEqual(result, [1, -3, 1, -3, 3, -3, 3, -3, 1, -3, 1])

    def test_char_to_seq_lowercase(self):
        """Test char_to_seq with a lowercase letter (should be converted to uppercase)"""
        result = EasyMorse.char_to_seq('k')
        self.assertEqual(result, [3, -3, 1, -3, 3])

    def test_char_to_seq_not_in_dict(self):
        """Test char_to_seq with a character not in the dictionary"""
        result = EasyMorse.char_to_seq('@')
        self.assertEqual(result, [])

    def test_char_to_seq_custom_dict(self):
        """Test char_to_seq with a custom dictionary"""
        custom_dict = {'X': '....'}  # X as four dots
        result = EasyMorse.char_to_seq('X', custom_dict)
        self.assertEqual(result, [1, -3, 1, -3, 1, -3, 1])

    def test_init_default(self):
        """Test initialization with default parameters"""
        morse = EasyMorse("TEST")
        self.assertEqual(morse.raw_text, "TEST")
        self.assertEqual(morse.prefix, "")
        self.assertIn('A', morse.morse_dict)
        self.assertIn(' ', morse.morse_dict)

    def test_init_with_prefix_true(self):
        """Test initialization with prefix=True"""
        morse = EasyMorse("TEST", prefix=True)
        self.assertTrue(morse.prefix.startswith("._._._-___"))
        self.assertEqual(morse.raw_text, "TEST")

    def test_init_with_custom_prefix(self):
        """Test initialization with custom prefix"""
        custom_prefix = ".-.-."
        morse = EasyMorse("TEST", prefix=custom_prefix)
        self.assertEqual(morse.prefix, custom_prefix)

    def test_init_with_custom_dict(self):
        """Test initialization with custom dictionary"""
        custom_dict = {'A': '.-', 'B': '-...'}
        morse = EasyMorse("AB", morse_dict=custom_dict)
        self.assertEqual(morse.morse_dict['A'], '.-')
        self.assertEqual(morse.morse_dict['B'], '-...')
        self.assertIn(' ', morse.morse_dict)  # Space should be added

    def test_create_times_dict(self):
        """Test _create_times_dict method"""
        morse = EasyMorse("TEST")
        times_dict = morse._create_times_dict()
        self.assertEqual(times_dict['A'], (1, 3))
        self.assertEqual(times_dict['T'], (3,))
        self.assertEqual(times_dict[' '], (-5,))

    def test_set_text_simple(self):
        """Test set_text method with a simple string"""
        morse = EasyMorse("")
        morse.set_text("SOS")
        self.assertEqual(morse.raw_text, "SOS")
        self.assertEqual(morse.text_to_morse, ['S', 'O', 'S'])
        # Check morse_code format
        self.assertIn('._._._', morse.morse_code)  # S is ._._._
        self.assertIn('-_-_-', morse.morse_code)  # O is -_-_-

    def test_set_text_with_spaces(self):
        """Test set_text method with spaces"""
        morse = EasyMorse("")
        morse.set_text("A B")
        self.assertEqual(morse.raw_text, "A B")
        self.assertEqual(morse.text_to_morse, ['A', ' ', 'B'])
        # Check morse_code format
        self.assertIn('._-', morse.morse_code)  # A is ._-
        self.assertIn('-_._._', morse.morse_code)  # B is -_._._
        self.assertIn('_____', morse.morse_code)  # Space representation

    def test_set_text_with_invalid_chars(self):
        """Test set_text method with characters not in the dictionary"""
        morse = EasyMorse("")
        morse.set_text("A@B")
        self.assertEqual(morse.raw_text, "A@B")
        self.assertEqual(morse.text_to_morse, ['A', 'B'])  # @ should be filtered out

    def test_morse_seq_generation(self):
        """Test morse_seq generation"""
        morse = EasyMorse("A")
        # Check that morse_seq is correctly generated
        self.assertEqual(morse.morse_seq, [1, -3, 3])  # A is ._-

    def test_morse_seq_with_prefix(self):
        """Test morse_seq generation with prefix"""
        morse = EasyMorse("A", prefix=True)
        # Prefix should be included in morse_seq
        self.assertTrue(len(morse.morse_seq) > 2)  # More than just [1, 3] for 'A'

    def test_full_message_conversion(self):
        """Test full message conversion process"""
        morse = EasyMorse("SOS")
        expected_seq = []
        # S: ...
        expected_seq.extend([1, -3, 1, -3, 1])
        # Inter-character space
        expected_seq.extend([-3, -3, -3])
        # O: ---
        expected_seq.extend([3, -3, 3, -3, 3])
        # Inter-character space
        expected_seq.extend([-3, -3, -3])
        # S: ...
        expected_seq.extend([1, -3, 1, -3, 1])

        # Compare with actual sequence
        self.assertEqual(morse.morse_seq, expected_seq)


if __name__ == '__main__':
    unittest.main()
