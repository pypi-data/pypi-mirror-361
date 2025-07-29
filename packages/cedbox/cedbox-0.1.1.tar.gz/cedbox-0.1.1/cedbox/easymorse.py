MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...',
    'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-',
    'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-',
    'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--',
    'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.',
    '0': '-----', ', ': '--..--', '.': '.-.-.-',
    '?': '..--..', '/': '-..-.', '-': '-....-',
    '(': '-.--.', ')': '-.--.-', ':': '---...',
}


class EasyMorse:
    """Class for creating and managing Morse code time units."""

    def __init__(self, text, morse_dict=None, prefix:bool|str=False):
        """
        Initialize the MorseCodeTimes class.

        Args:

        """
        morse_dict = morse_dict if morse_dict is not None else MORSE_CODE_DICT
        morse_dict.update({' ': '_____'})
        self.morse_dict = morse_dict
        self.times_dict = self._create_times_dict()

        if isinstance(prefix, bool):
            self.prefix = "._._._-___._._._-___._._._-___-_._._._._-_____" if prefix else "" #VVV- as prefix
        elif isinstance(prefix, str):
            self.prefix = prefix

        self.raw_text = text
        self.text_to_morse = None
        self.morse_code = None
        self.morse_code_times = None
        self.morse_message = None
        self.morse_seq = None
        self.set_text(text)


    def _create_times_dict(self):
        """
        Convert Morse code dictionary to time units dictionary.

        Returns:
            dict: Dictionary mapping characters to tuples of time units.
        """
        times_dict = {
            char: tuple(1 if c == '.' else 3 for c in code) 
            for char, code in self.morse_dict.items()
        }
        times_dict.update({' ': (-5,)})
        return times_dict


    def set_text(self, raw_text: str):

        self.raw_text = raw_text

        self.text_to_morse = [char for char in self.raw_text.upper() if char in self.morse_dict]

        morse_code = ['_'.join(self.morse_dict[char]) for char in self.text_to_morse]

        self.morse_code = '___'.join(morse_code).replace('_______________', '_____')

        self.morse_message = self.prefix + self.morse_code if self.prefix else self.morse_code

        self.morse_seq = [{'.': 1, '-': 3, '_': -3}[char] for char in self.morse_message]

if __name__ == "__main__":
    morse = EasyMorse('KM km')
    print(morse.morse_seq)
