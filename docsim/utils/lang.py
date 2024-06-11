import unicodedata as ud
import random
import string

# ISO Language code to script name
ISO639_TO_SCRIPT = {
    'ta': 'tamil',
    'ml': 'malayalam',
    'te': 'telugu',
    'kn': 'kannada',
    'hi': 'devanagari',
    'ne': 'devanagari'
}

MAX_RANGE = 1114112
MAX_DEVANAGARI =43264
MIN_DEVANAGARI = 2304
ALLOWED_CATEGORIES = ['L', 'M', 'N', 'P']
DISALLOWED_CHARACTERS = ['ऀ', 'ऌ', 'ऍ', 'ऎ','ऄ','ऑ', 'ऒ','ऩ',
                         'ऱ', 'ळ', 'ऴ', 'ऺ', 'ऻ', '़', 'ऽ',
                         'ॅ', 'ॆ', 'े', 'ै', 'ॎ', 'ॏ',
                         '॑', '॒', '॓', '॔', 'ॕ', 'ॖ', 'ॗ',
                         'क़', 'ख़', 'ग़', 'ज़', 'ड़', 'ढ़', 'फ़',
                         'य़', 'ॠ', 'ॡ', 'ॢ', 'ॣ','ृ',
                         'ॱ', 'ॲ', 'ॳ', 'ॴ', 'ॵ', 'ॶ', 'ॷ',
                         'ॸ', 'ॹ', 'ॺ', 'ॻ', 'ॼ', 'ॽ', 'ॾ', 'ॿ',
                         'ꣲ', 'ꣳ', 'ꣴ', 'ꣵ','ॉ', 'ॊ',
                         'ꣶ', 'ꣷ', 'ꣻ', 'ꣽ', 'ꣾ', 'ꣿ', 'ॄ']
# ALLOWED_CATEGORIES = ['L', 'M', 'N', 'P', 'S', 'Z', 'C']
def get_characters(script_name, only_prefix_match=False, skip_punctuations=False, skip_numbers=False, verbose=True):
    characters = {}
    unicode_list = []
    unicode = []
    counter = 0
    categories = []
    script_name = script_name.upper()
    for i in range(MIN_DEVANAGARI, MAX_DEVANAGARI):
        try:
            name = ud.name(chr(i))
        except ValueError:
            continue
        if only_prefix_match:
            if not name.startswith(script_name):
                continue
        elif script_name not in name:
            continue
        if script_name in name:
            unicode.append(i)
            unicode_list.append(name)
            counter += 1

        # Got a character of that script
        cat = ud.category(chr(i))
        categories.append(cat)
        if skip_numbers and cat[0] == 'N':
            continue
        if skip_punctuations and cat[0] == 'P':
            continue

        if cat[0] not in ALLOWED_CATEGORIES:
            if verbose:
                print('SKIPPED:', chr(i), name, cat)
        else:
            characters[chr(i)] = (name, cat)
    # print("The correct unicodes are: ", unicode_list)
    # print("The number of characters: ", counter)
    # print("The range of devanagari unicodes are:", unicode)
    # print("The categories are:", categories)
    # print(characters.keys())
    filtered_dict = filter_characters(characters)
    return filtered_dict

def filter_characters(characters):
    keys_to_remove = [key for key in characters if key in DISALLOWED_CHARACTERS]
    for item in keys_to_remove:
        del characters[item]
    return characters

def get_vowels(characters):
    vowels = []
    for c, (name, category) in characters.items():
        if 'VOWEL' in name or 'VIRAMA' in name:
            vowels.append(c)
    return vowels

def get_consonants(characters):
    consonants = []
    for c, (name, category) in characters.items():
        if 'LETTER' in name:
            consonants.append(c)
    return consonants

class EnglishCharacters:
    def __init__(self, skip_punctuations=True, skip_numbers=True):
        self.lang_code = 'en'
        self.characters = string.ascii_uppercase
        if not skip_punctuations:
            self.characters += string.punctuation
        if not skip_numbers:
            self.characters += string.digits

        self.vowels = 'AEIOU'
        self.consonants = 'BCDFGHJKLMNPQRSTVWXYZ'

class LanguageCharacters:
    def __init__(self, lang_code, only_prefix_match=True, skip_punctuations=True, skip_numbers=True,
                 verbose=False):

        if lang_code not in ISO639_TO_SCRIPT:
            exit('Lang code %s not found' % lang_code)

        self.lang_code = lang_code
        self.script = ISO639_TO_SCRIPT[lang_code]
        self.characters = get_characters(self.script, only_prefix_match, skip_punctuations, skip_numbers, verbose)
        self.vowels = get_vowels(self.characters)
        self.consonants = get_consonants(self.characters)
        self.import_letter_combinations()

        if verbose: self.print_details()

    def import_letter_combinations(self):
        if self.lang_code == 'ta':
            import tamil
            self.letter_combinations = tamil.utf8.tamil247

        return

    def print_details(self):
        print('LANGUAGE CODE:', self.lang_code)
        print('SCRIPT NAME:', self.script)
        print('CHARACTERS:'); print(self.characters)
        print('VOWELS:'); print(self.vowels)
        print('CONSONANTS:'); print(self.consonants)
        return


if __name__ == '__main__':
    c = LanguageCharacters('ne', only_prefix_match=True, skip_punctuations=True, skip_numbers=True, verbose=True)
