import random
class TextGeneratorBase:
    def generate(self):
        return 'ERROR'

from rstr import xeger
class TextFromRegexGenerator(TextGeneratorBase):
    def __init__(self, regex):
        self.pattern = regex
    
    def generate(self):
        return xeger(self.pattern)

import re
class NepaliCurrencyGenerator(TextGeneratorBase):
    def __init__(self):
        self.nepali_numbers = [
            "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ",
            "दश", "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठार", "उन्नाइस",
            "बीस", "एक्काइस", "बाइस", "तेइस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताइस", "अठ्ठाइस", "उनन्तिस",
            "तीस", "एकतीस", "बत्तीस", "तेत्तीस", "चौँतीस", "पैँतीस", "छत्तीस", "सैंतीस", "अठतीस", "उनन्चालीस",
            "चालीस", "एकचालीस", "बयालीस", "त्रियालीस", "चवालीस", "पैंतालीस", "छयालीस", "सतचालीस", "अठचालीस", "उनन्चास",
            "पचास", "एकाउन्न", "बाउन्न", "त्रिपन्न", "चवन्न", "पचपन्न", "छपन्न", "सन्ताउन्न", "अन्ठाउन्न", "उनन्साठी",
            "साठी", "एकसट्ठी", "बयसट्ठी", "त्रिसट्ठी", "चौंसट्ठी", "पैंसट्ठी", "छैंसट्ठी", "सतसट्ठी", "अठसट्ठी",
            "उनन्सत्तरी",
            "सत्तरी", "एकहत्तर", "बहत्तर", "त्रिहत्तर", "चौहत्तर", "पचहत्तर", "छयहत्तर", "सतहत्तर", "अठहत्तर", "उनासी",
            "अस्सी", "एकासी", "बयासी", "त्रियासी", "चौरासी", "पचासी", "छयासी", "सतासी", "अठासी", "उनान्नब्बे",
            "नब्बे", "एकान्नब्बे", "बयान्नब्बे", "त्रियान्नब्बे", "चौरान्नब्बे", "पन्चान्नब्बे", "छयान्नब्बे",
            "सन्तान्नब्बे", "अन्ठान्नब्बे", "उनान्सय", "सय"
        ]

    def random_nepali_number(self):
            return random.choice(self.nepali_numbers)

    def generate_nepali_currency(self):
        parts = []

        # Generate crores part
        if random.choice([True, False]):
            crores = self.random_nepali_number()
            parts.append(f"{crores} करोड")

        # Generate lakhs part
        if random.choice([True, False]):
            lakhs = self.random_nepali_number()
            parts.append(f"{lakhs} लाख")

        # Generate thousands part
        if random.choice([True, False]):
            thousands = self.random_nepali_number()
            parts.append(f"{thousands} हजार")

        # Generate hundreds part
        if random.choice([True, False]):
            hundreds = self.random_nepali_number()
            parts.append(f"{hundreds} सय")

        # Generate final number part
        number = self.random_nepali_number()
        parts.append(number)

        # Combine all parts
        result = ", ".join(parts)
        return result


    def generate(self):
        synthesized_amount = self.generate_nepali_currency()
        # e.g. चौध लाख, उन्नाइस हजार, एघार मात्र/-
        # print(synthesized_amount)
        first_line = []
        second_line = []
        closing_tag = " मात्र/-"
        list_of_words  =  synthesized_amount.split(" ")
        # print(list_of_words)
        # e.g. ['उनन्तिस', 'करोड,', 'पच्चीस', 'लाख,', 'बाह्र', 'हजार,', 'चौबीस', 'मात्र/-']
        if len(list_of_words) <= 7:
            synthesized_amount += closing_tag
        else:
            print("List of words are:", list_of_words)
            # Join words from the list to form the required lines
            first_line = ' '.join(list_of_words[:6])
            second_line = ' '.join(list_of_words[6:])
            print("First Line: ", first_line)
            print("Second Line: ", second_line)
            print("For longer than 6 words: ",first_line, second_line)
            synthesized_amount = first_line +" \n "+ second_line + closing_tag
            print("The synthesized_amount is: ", synthesized_amount)
        return synthesized_amount

class TextFromArrayGenerator(TextGeneratorBase):
    def __init__(self, array):
        self.options = array
    
    def generate(self):
        return random.choice(self.options)


# To return unicode of give integer in component['unicode']
class UnicodeGenerator(TextGeneratorBase):
    def __init__(self, unicode):
        self.options = unicode

    def generate(self):
        # print("The unicode symbol is:", chr(int(self.options[0], 16)))
        return chr(int(self.options[0], 16))

from docsim.utils.lang import EnglishCharacters, LanguageCharacters
class NameGenerator(TextGeneratorBase):
    def __init__(self, lang='en'):
        if lang == 'en':
            self.charset = EnglishCharacters()
            self.title_case = True
        else:
            self.charset = LanguageCharacters(lang)
            self.title_case = False
        
        if hasattr(self.charset, 'letter_combinations'):
            self.random_length_name = self.random_length_name_from_combinations
    
    def generate(self, min_len=5, max_len=5):
        return self.random_name(min_len, max_len)
    
    def random_length_name_from_combinations(self, length=5):
        return ''.join(random.choice(self.charset.letter_combinations) for i in range(length))
    
    def random_length_name(self, length=5):
        return ''.join(random.choice((self.charset.consonants, self.charset.vowels)[i%2]) for i in range(length))

    def random_name(self, min_length=5, max_length=5):
        length = random.randrange(min_length, max_length)
        return self.random_length_name(length)


class AccountNameGenerator(TextGeneratorBase):
    def __init__(self, lang='en'):
        if lang == 'en':
            self.charset = EnglishCharacters()
            self.title_case = True
        else:
            self.charset = LanguageCharacters(lang)
            self.title_case = False

        if hasattr(self.charset, 'letter_combinations'):
            self.random_length_name = self.random_length_name_from_combinations

    def generate(self, min_len=5, max_len=5):
        return self.random_name(min_len, max_len)

    def random_length_name_from_combinations(self, length=5):
        return ' '.join(random.choice(self.charset.letter_combinations) for i in range(length))

    def random_length_name(self, length=5):
        return ' '.join(random.choice((self.charset.consonants, self.charset.vowels)[i % 2]) for i in range(length))

    def random_name(self, min_length=5, max_length=5):
        length = random.randrange(min_length, max_length)
        return self.random_length_name(length)


class FullNameGenerator(NameGenerator):
    
    def generate(self):
        return self.random_fullname()
    
    def random_fullname(self):
        first_name = self.random_name(5, 7)
        
        initial = random.choice(self.charset.consonants) + '.'
        if random.random() < 0.25:
            # Two initials
            initial += ' ' + random.choice(self.charset.consonants) + '.'
            if random.random() < 0.4:
                # Three initials
                initial += ' ' + random.choice(self.charset.consonants) + '.'
        
        middle_name = self.random_name(4, 7)
        last_name = self.random_name(6, 8)
        
        # Either add middle name or initial
        if random.random() > 0.5:
            if random.random() > 0.5:
                # Add initial in middle
                name = first_name + ' ' + initial
            else:
                # Add initial at the beginning
                name = initial + ' ' + first_name
            
        else:
            name = first_name + ' ' + middle_name
        
        # Add last name for majority
        if random.random() > 0.15:
            name += ' ' + last_name
        
        return name.title() if self.title_case else name


class AccNameGenerator(AccountNameGenerator):
    def generate(self):
        return self.random_fullname()

    def random_fullname(self):
        first_name = self.random_name(5, 7)

        middle_name = self.random_name(4, 7)
        last_name = self.random_name(6, 8)

        # Add last name for majority
        if random.random() > 0.45:
            if len(first_name) < 8:
                middle_name = " "*random.randint(20,25)
            else:
                middle_name = " "* random.randint(14,17)
        else:
            if len(first_name) < 8:
                first_name += " "*random.randint(15,20)
        name = f"{first_name}{' '*7}{middle_name}{' '*7}{last_name}"

        return name.title() if self.title_case else name

class MultilineFullNameGenerator(FullNameGenerator):
    
    def generate(self):
        full_name = self.random_fullname()
        if random.random() > 0.3:
            return full_name
        else:
            return full_name + '\n' + self.random_name(6, 8)

class ChildNameFromParentGenerator(MultilineFullNameGenerator):
    def __init__(self, lang, src_component):
        super().__init__(lang)
        self.src_component = src_component
    
    def generate(self):
        child_name = self.src_component['generator'].generate()
        if random.random() > 0.2:
            return child_name
        
        parent = self.src_component['last_generated'].replace('\n', ' ')
        first_name = child_name.split()[0]
        if len(first_name) < 3:
            first_name = ' '.join(child_name.split()[:2])
            if len(first_name) < 5:
                first_name = ' '.join(child_name.split()[:3])
        
        if random.random() > 0.3:
            name = first_name + ' ' + parent
        else:
            # Remove parent's first name
            family_name = parent.replace(parent.split()[0], '')
            name = first_name + family_name
        
        parts = name.split()
        if len(parts) > 3:
            # Break into 2 lines if long
            name = ' '.join(parts[:3]) + '\n' + ' '.join(parts[3:])
        
        return name

class ReferentialTextGenerator(TextGeneratorBase):
    def __init__(self, src_component):
        self.src_component = src_component # Reference to the component from which we have to xlit
        
    def generate(self):
        return self.src_component['last_generated']

from docsim.utils.transliterator import Transliterator
class ReferentialTextTransliterator(ReferentialTextGenerator):
    def __init__(self, src_lang, dest_lang, src_component):
        super().__init__(src_component)
        self.transliterator = Transliterator(src_lang, dest_lang)
        
    def generate(self):
        return self.transliterator.transliterate(super().generate())

class TextPostProcessor():
    def __init__(self, upper_case=False, lower_case=False,
                 multiline=True):
        self.upper_case = upper_case
        self.lower_case = lower_case
        self.multiline = multiline
        
    def process(self, text):
        if self.upper_case:
            text = text.upper()
        elif self.lower_case:
            text = text.lower()
        
        if not self.multiline:
            text = text.split('\n')[0]
        return text

from faker import Faker
class AddressGenerator():
    LANG2CODE = {
        'en' : 'en-US',
        'hi': 'hi_IN'
    }
    def __init__(self, language='en', type="full"):
        lang_code = AddressGenerator.LANG2CODE[language]
        self.faker = Faker(lang_code)
        self.type = type
    def generate(self):
        if self.type == "full":
            return self.faker.address()
        if self.type == "street_address":
            return self.faker.street_address()
        elif self.type == "city":
            return self.faker.city()
        elif self.type == "country":
            return self.faker.country()
        elif self.type == "postcode":
            return self.faker.postcode()
        else:
            raise NotImplementedError
            
