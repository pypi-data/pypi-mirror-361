import random
import importlib.resources


class PasswordGenerator:
    """
    PasswordGenerator is a flexible utility class for generating various types of secure passwords
    and passphrases with customizable parameters.

    🔧 Core Features:
    ----------------
    - Generate strong passwords using letters, digits, and symbols with customizable ratios.
    - Generate passwords with only letters, numbers, or symbols.
    - Support for custom character sets or casing (upper/lower/mixed).
    - Generate alphanumeric or hexadecimal passwords.
    - Generate secure one-time passwords (OTP) with optional symbol and letter case control.
    - Generate numeric PIN codes.
    - Generate human-readable passphrases from a wordlist.

    📌 Methods Overview:
    --------------------
    - generate_strong_password(): Create a complex password using ratios for symbols and numbers.
    - generate_only_numbers_password(): Password with digits only.
    - generate_only_letters_password(): Password with letters only (mixed/upper/lower).
    - generate_only_symbols_password(): Password with symbols only.
    - generate_alphanumeric_password(): Letters and digits, with optional case control.
    - generate_hex_password(): Password in hexadecimal format (lower/upper).
    - generate_custom_charset_password(): Create password using user-defined character set.
    - generate_otp_password(): One-time password with optional components (letters, numbers, symbols).
    - generate_passphrase(): Generate readable passphrase from a curated wordlist.
    - generat_Pin(): Generate simple numeric PIN of a specified length.
    - resolve_length(): Choose a length between min and max (used for randomness bounds).

    ⚙️ Configuration Parameters:
    ----------------------------
    - length (int): Default length used in all generation methods (overridable per call).
    - symbols_ratio (float): Ratio of symbols to use in `generate_strong_password()`.
    - numbers_ratio (float): Ratio of numbers to use in `generate_strong_password()`.
    - use_uppercase (bool): Whether to include uppercase letters.
    - extra_chars (str): Additional characters to include in the character pool.
    - custom_charset (str): Optional full override for character pool.
    - random_state (int/None): Seed for reproducible output (for testing or debugging).

    🧠 Example Usage:
    -----------------
    >>> gen = PasswordGenerator(length=16)
    >>> gen.generate_strong_password()
    'A7f@wL#9!x8GmQ$d'

    >>> gen.generate_passphrase(count_words=6)
    'rocket table dragon glass tiger nest'

    This class is suitable for applications that need secure password generation, customizable
    entropy levels, or even human-readable key phrases for security tokens and user onboarding.

    """
    SYMBOLS = '!@#$%^&*()-_=+[]{}|;:,.<>?/'  # مجموعة الرموز   
    def __init__(self, length=12, symbols_ratio=0.2, numbers_ratio=0.2,
                    use_uppercase=True, extra_chars="", custom_charset=None, random_state=None):
        self.length = length
        self.symbols_ratio = symbols_ratio
        self.numbers_ratio = numbers_ratio
        self.use_uppercase = use_uppercase
        self.extra_chars = extra_chars
        self.custom_charset = custom_charset
        self.random = random.Random(random_state)  # لضبط العشوائية

    def _build_letter_charset(self, case):
        """Builds a character set based on the specified letter case."""
        if case == 'upper':
            return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        elif case == 'lower':
            return 'abcdefghijklmnopqrstuvwxyz'
        elif case == 'mixed':
            return 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        else:
            raise ValueError("Invalid letter_case option.")

        
    def _resolve_length_chack(self, length):
        """Checks and resolves the length parameter."""
        if length < 1:
            raise ValueError("Length must be at least 1.")
        return length or self.length

    def resolve_length(self, main_length=1, max_length=None):
        """Resolves the length based on main_length and max_length."""
        if max_length is None:
            raise ValueError("You must provide max_length (required).")
        if max_length < 1:
            raise ValueError("Maximum length must be a positive integer.")
        if main_length < 0:
            raise ValueError("Main length must be a non-negative integer.")
        if main_length > max_length:
            max_length, main_length = main_length, max_length
            print("\033[91mWarning: Main length is greater than maximum length. Swapping values.\033[0m")
        if main_length > 0:
            return self.random.randint(main_length, max_length)
        else:
            return self.random.randint(1, max_length)

    # Generate a random pin password based on the specified parameters
    def generat_Pin(self, pin_length=4):
        """Generates a random PIN of specified length."""
        if pin_length < 1:
            raise ValueError("PIN length must be at least 1.")
        return ''.join(self.random.choices('0123456789', k=pin_length))
    
    # Generate a strong password based on the specified parameters
    def generate_strong_password(self , extra_chars="" , symbols_ratio=0, numbers_ratio=0 , length=0):
        """Generates a strong password based on the specified parameters."""
        self.extra_chars = extra_chars if extra_chars else self.extra_chars
        self.symbols_ratio = symbols_ratio if symbols_ratio else self.symbols_ratio
        self.numbers_ratio = numbers_ratio if numbers_ratio else self.numbers_ratio
        length = self._resolve_length_chack(length)
        if self.custom_charset:
            charset = self.custom_charset
        else:
            charset = 'abcdefghijklmnopqrstuvwxyz'
            if self.use_uppercase:
                charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if self.extra_chars:
                charset += self.extra_chars
            if self.symbols_ratio > 0:
                charset += self.SYMBOLS
            if self.numbers_ratio > 0:
                charset += '0123456789'
        password_length = round(length * (1 - self.symbols_ratio - self.numbers_ratio))
        symbols_length = round(length * self.symbols_ratio)
        numbers_length = round(length * self.numbers_ratio)
        password_chars = (
            self.random.choices(charset, k=password_length) +
            self.random.choices(self.SYMBOLS, k=symbols_length) +
            self.random.choices('0123456789', k=numbers_length)
        )
        self.random.shuffle(password_chars)
        return ''.join(password_chars)



    def generate_alphanumeric_password(self, length=0, Case_of_letters='mixed', numbers_ratio=None):
        """Generates an alphanumeric password of specified length with optional number ratio."""
        length = self._resolve_length_chack(length)
        letters_charset = self._build_letter_charset(Case_of_letters)
        numbers_charset = '0123456789'

        if numbers_ratio is not None:
            numbers_length = round(length * numbers_ratio)
            letters_length = length - numbers_length

            if letters_length < 0:
                raise ValueError("numbers_ratio too high. It exceeds total length.")

            password_chars = (
                self.random.choices(letters_charset, k=letters_length) +
                self.random.choices(numbers_charset, k=numbers_length)
            )
        else:
            combined_charset = letters_charset + numbers_charset
            password_chars = self.random.choices(combined_charset, k=length)

        self.random.shuffle(password_chars)
        return ''.join(password_chars)


    def generate_only_numbers_password(self, length=0):
        """Generates a numeric password of specified length."""
        length = self._resolve_length_chack(length)
        return ''.join(self.random.choices('0123456789', k=length))

    def generate_only_letters_password(self, length=0, Case_of_letters='mixed'):
        """Generates a letter-only password of specified length."""
        length = self._resolve_length_chack(length)
        charset = self._build_letter_charset(Case_of_letters)
        return ''.join(self.random.choices(charset, k=length))

    def generate_only_symbols_password(self, length=0):
        """Generates a symbol-only password of specified length."""
        length = self._resolve_length_chack(length)
        return ''.join(self.random.choices(self.SYMBOLS, k=length))
    
    
    def generate_custom_charset_password(self, length=0, custom_charset=None):
        """Generates a password using a custom character set."""
        if custom_charset is None:
            raise ValueError("Custom charset must be provided.")
        if len(custom_charset) < 1:
            raise ValueError("Custom charset must contain at least one character.")
        length = self._resolve_length_chack(length)
        return ''.join(self.random.choices(custom_charset, k=length))
    
    def generate_hex_password(self, length=0, hex_upper=False):
        """Generates a hexadecimal password of specified length."""
        length = self._resolve_length_chack(length)
        hex_chars = '0123456789abcdef'
        if hex_upper:
            hex_chars = hex_chars.upper()
        return ''.join(self.random.choices(hex_chars, k=length))
    
    def generate_otp_password(self, length=0, include_numbers=True,
                                include_letters=True, include_symbols=False, 
                                letter_case='mixed',
                                numbers_ratio=None, symbols_ratio=None):
        """Generates a one-time password (OTP) of specified length with optional ratios."""

        length = self._resolve_length_chack(length)
        total_length = length

        charset_letters = self._build_letter_charset(letter_case) if include_letters else ''
        charset_numbers = '0123456789' if include_numbers else ''
        charset_symbols = self.SYMBOLS if include_symbols else ''

        # النسب
        numbers_len = round(total_length * numbers_ratio) if numbers_ratio else 0
        symbols_len = round(total_length * symbols_ratio) if symbols_ratio else 0
        letters_len = total_length - numbers_len - symbols_len

        if letters_len < 0:
            raise ValueError("Sum of ratios is greater than 1. Please adjust the ratios.")

        password_chars = []
        if letters_len < 0:
            if not charset_letters:
                raise ValueError("No letter charset selected but letters are required by ratio.")
            password_chars += self.random.choices(charset_letters, k=letters_len)
        if numbers_len > 0:
            if not charset_numbers:
                raise ValueError("No number charset selected but numbers are required by ratio.")
            password_chars += self.random.choices(charset_numbers, k=numbers_len)
        if symbols_len > 0:
            if not charset_symbols:
                raise ValueError("No symbol charset selected but symbols are required by ratio.")
            password_chars += self.random.choices(charset_symbols, k=symbols_len)

        if not password_chars:
            # fallback إذا مفيش ratios متوفرة
            combined_charset = charset_letters + charset_numbers + charset_symbols
            if not combined_charset:
                raise ValueError("OTP character set is empty. Please select at least one type.")
            password_chars = self.random.choices(combined_charset, k=total_length)

        self.random.shuffle(password_chars)
        return ''.join(password_chars)
    
    def generate_valid_pattern_lock(self, length=4):
        if not (3 <= length <= 9):
            raise ValueError("Pattern length must be between 3 and 9.")
        # خريطة نقاط العبور المطلوبة بين رقمين
        skips = {
            (1, 3): 2, (3, 1): 2,
            (1, 7): 4, (7, 1): 4,
            (3, 9): 6, (9, 3): 6,
            (7, 9): 8, (9, 7): 8,
            (1, 9): 5, (9, 1): 5,
            (2, 8): 5, (8, 2): 5,
            (3, 7): 5, (7, 3): 5,
            (4, 6): 5, (6, 4): 5,
        }

        pattern = []
        used = set()

        current = self.random.choice(range(1, 10))
        pattern.append(current)
        used.add(current)

        while len(pattern) < length:
            candidates = []
            for candidate in range(1, 10):
                if candidate in used:
                    continue
                skip = skips.get((current, candidate))
                if skip is None or skip in used:
                    candidates.append(candidate)

            if not candidates:
                break  # مفيش اختيارات صحيحة، هنوقف

            current = self.random.choice(candidates)
            pattern.append(current)
            used.add(current)

        if len(pattern) < length:
            raise ValueError("Couldn't generate valid pattern with given length.")
        return pattern

    def generate_passphrase(self ,count_words = 4 , join_words = True , separator = '  '):
        """Generates a passphrase with a specified number of words."""
        with importlib.resources.files("smartpassgen").joinpath("words_list.txt").open("r", encoding="utf-8") as file:
            words = file.read().splitlines()
        if count_words < 1:
            raise ValueError("Count must be at least 1.")
        selected = random.choices(words, k=count_words)
        return separator.join(selected) if join_words else selected


# Example usage:

# Password_generator = PasswordGenerator() 
# pin = Password_generator.generat_Pin(6)
# length = Password_generator.resolve_length(main_length=8,max_length=32)
# pssword = Password_generator.generate_strong_password(length=length)
# generate_custom_charset_password = Password_generator.generate_custom_charset_password(length=length, custom_charset="abcd1234")
# print(f"Generated Custom Charset Password: {generate_custom_charset_password}")
# print(f"Generated Only Letters Password: {Password_generator.generate_only_letters_password(length=length, Case_of_letters='mixed')}")
# print(f"Generated Only Numbers Password: {Password_generator.generate_only_numbers_password(length=length)}")
# print(f"Generated Only Symbols Password: {Password_generator.generate_only_symbols_password(length=length)}")
# print(f"Generated Length: {length}")
# print(f"Generated PIN: {pin}")
# print(f"Generated Password: {pssword}")
# print(f"Generated Alphanumeric Password: {Password_generator.generate_alphanumeric_password(length=length, Case_of_letters='mixed')}")
# print(f"Generated Hex Password: {Password_generator.generate_hex_password(length=8, hex_upper=True)}")
# print(f"Generated OTP Password: {Password_generator.generate_otp_password(length=8, include_numbers=True, include_letters=False, include_symbols=False, letter_case='mixed')}")
# print(f"Generated Pattern Lock: {Password_generator.generate_valid_pattern_lock(length=random.randint(3, 9))}")
# print(f"Generated Passphrase: {Password_generator.generate_passphrase(join_words= False , count_words = length, separator = '  ')}")
