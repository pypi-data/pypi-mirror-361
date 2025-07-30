# 🔐 smartpassgen

A simple and lightweight Python library for generating secure passwords of various types.

The library provides a single class with multiple methods to generate different kinds of passwords, including:

- Alphanumeric passwords  
- Strong passwords with symbols  
- PIN codes  
- Custom-length passwords  

Perfect for developers who need quick, flexible, and secure password generation in their applications.

---

## 🔑 Features

- Easy-to-use class-based structure  
- Multiple password generation options  
- Customizable password length and character sets  
- No external dependencies  
- Fast and clean codebase

---

## ✨ Supported Password Types

- **Strong Passwords** (letters + numbers + symbols)  
- **Alphanumeric Passwords**  
- **Custom Charset Passwords**  
- **Letters Only Passwords** (with control over letter casing)  
- **Numbers Only Passwords**  
- **Symbols Only Passwords**  
- **HEX Passwords**  
- **Passphrases** (multi-word phrases)  
- **OTP (One-Time Passwords)**  
- **PIN Codes**  
- **Pattern Lock** (Android-style lock patterns)

---

## 📦 Installation

```bash
pip install smartpassgen
```
---
## 🧠 How to Use
First, import the generator class:

```python
from smartpassgen import PasswordGenerator

generator = PasswordGenerator()
```
⚙️ Class Default Configuration
When you create an instance of PasswordGenerator, you can optionally pass default settings that apply to all password generation methods (unless overridden).

```python
from smartpassgen import PasswordGenerator

generator = PasswordGenerator(
    length=12,
    symbols_ratio=0.2,
    numbers_ratio=0.2,
    use_uppercase=True,
    extra_chars="",
    custom_charset=None,
    random_state=None
)
```
### Parameters

| Parameter        | Type                       | Description                                                                                  |
|------------------|----------------------------|----------------------------------------------------------------------------------------------|
| `length`         | `int`                      | Default password length used by most methods if not explicitly provided. *(Default: 12)*     |
| `symbols_ratio`  | `float`                    | Ratio of symbols in the password (0 to 1). *(Default: 0.2)*                                  |
| `numbers_ratio`  | `float`                    | Ratio of digits in the password (0 to 1). *(Default: 0.2)*                                   |
| `use_uppercase`  | `bool`                     | Whether to include uppercase letters in generated passwords. *(Default: True)*               |
| `extra_chars`    | `str`                      | Additional custom characters to include in all passwords. *(Default: empty)*                 |
| `custom_charset` | `str` or `None`            | A fully custom set of characters to override the built-in ones. *(Default: None)*            |
| `random_state`   | `int` or `random.Random`   | For reproducible results (optional seed or Random instance). *(Default: None)*               |

- ⚠️ You can override these defaults in each method if you want more control per password.

###  Example: Using Default Settings

```python
from smartpassgen import PasswordGenerator
import random

# Create an instance with custom default settings
generator = PasswordGenerator(
    length=16,                # default length = 16
    symbols_ratio=0.3,        # 30% symbols
    numbers_ratio=0.2,        # 20% numbers
    use_uppercase=False,      # no uppercase letters
    extra_chars="*",          # include * in all passwords
    custom_charset=None,      # use default charset (letters + digits + symbols)
    random_state=42           # seed for reproducible output
)

# Generate a strong password using these defaults
password = generator.generate_strong_password()
print("Strong Password:", password)
```

| Setting               | What it does in the example                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `length=16`           | The password will be 16 characters long by default.                     |
| `symbols_ratio=0.3`   | 30% of the password (≈5 chars) will be symbols.                         |
| `numbers_ratio=0.2`   | 20% of the password (≈3 chars) will be digits.                          |
| `use_uppercase=False` | All letters will be lowercase only.                                     |
| `extra_chars="*"`     | The `*` character is allowed and might appear randomly in the password. |
| `random_state=42`     | The output will be the same every time you run the script.              |

###### 📌 Note: You can override any of these per-method like this:

```pyhton
password = generator.generate_strong_password(length=8, use_uppercase=True)
```
---

## 🔐 generate_strong_password()

Generates a strong password using a mix of letters, digits, and symbols — with full control over character ratios and custom additions.

#### Parameters
| Parameter       | Type    | Description                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| `length`        | `int`   | Total length of the password. If set to `0`, it will fall back to the class default `length`. |
| `use_uppercase` | `bool`  | Whether to include uppercase letters. Overrides the class default.                            |
| `symbols_ratio` | `float` | Proportion of symbols (0.0 – 1.0) in the password. Overrides the class default.               |
| `numbers_ratio` | `float` | Proportion of digits (0.0 – 1.0) in the password. Overrides the class default.                |
| `extra_chars`   | `str`   | Optional characters to add to the total charset. Combined with letters, digits, and symbols.  |

-  💡 If any of these values are not passed, the method uses the instance defaults set in __init__().


### 🧪 Example 1: Default Usage

``` python 
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_strong_password()
print(password)  # Example: f3&G6s#kP2!e
```

- Uses length=12, 20% symbols, 20% digits, and allows uppercase.


### 🧪 Example 2: Fully Custom Settings

``` python
gen = PasswordGenerator()

password = gen.generate_strong_password(
    length=10,
    use_uppercase=False,
    symbols_ratio=0.1,
    numbers_ratio=0.3,
    extra_chars="*#"
)
print(password)
```

- Length = 10
- No uppercase letters
- ~1 symbol, ~3 digits
- *# can appear in place of symbols

###### ⚠️ Notes:
- The rest of the characters (after symbols + digits) will be filled with lowercase letters.
- If total calculated symbol + digit characters exceeds length, the function will auto-adjust proportions.
- extra_chars will be merged with the symbols pool (not added to all types).

---

## 🔡 generate_alphanumeric_password()

- Generates a password made of letters + digits only (no symbols).
- You can customize the case of letters and optionally control how many digits appear.

#### Parameters
| Parameter                                                              | Type              | Description                                                                            |
| ---------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------- |
| `length`                                                               | `int`             | Total password length. If `0`, falls back to the default set in class (`self.length`). |
| `Case_of_letters`                                                      | `str`             | Letter casing:                                                                         |
|   - `"lower"` → only lowercase                                         |                   |                                                                                        |
|   - `"upper"` → only uppercase                                         |                   |                                                                                        |
|   - `"mixed"` → both lower and upper                                   |                   |                                                                                        |
| `numbers_ratio`                                                        | `float` or `None` | Optional ratio (0.0 – 1.0) of how much of the password should be **digits**.           |
|  If `None`, digits and letters are mixed randomly without fixed ratio. |                   |                                                                                        |

## 🧪 Example 1: Default Mixed Case + Random Ratio

``` python
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_alphanumeric_password(length=10)
print(password)  # e.g., A7k2mD4bQ9
```

## 🧪 Example 2: Lowercase Letters Only + 50% Numbers

``` python
password = gen.generate_alphanumeric_password(length=8, Case_of_letters="lower", numbers_ratio=0.5)
print(password)  # e.g., a4d2f6p9
```
- In this case, half the password will be digits (length * 0.5), rest will be lowercase letters.


###### ⚠️ Notes
- If numbers_ratio is set and exceeds 1.0, it will be clamped internally.
- If Case_of_letters is invalid or excluded, it falls back to "mixed".
- Always generates a random mix (no fixed order) unless you post-process.

---

## 🎯 generate_custom_charset_password()

Generates a password using only the characters you specify.
Useful when you're working with restricted systems or want full control over what appears in the password.

#### Parameters

| Parameter        | Type  | Description                                                                             |
| ---------------- | ----- | --------------------------------------------------------------------------------------- |
| `length`         | `int` | Total password length. If `0`, uses the class default (`self.length`).                  |
| `custom_charset` | `str` | A string of characters to randomly pick from. Must not be `None`. Example: `"abc123!@"` |


## 🧪 Example 1: Basic Usage

``` pyhton 
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_custom_charset_password(length=10, custom_charset="abc123")
print(password)  # e.g., 1ab3c2ba1c
```

###### ⚠️ Notes:
- If custom_charset is None or empty, the method will raise an error.
- Characters in the charset can be repeated in the final password.
- Great for controlled systems like IoT devices, QR encodings, or custom lock formats.

---

## 🔢 generate_only_numbers_password()

Generates a password made up of digits only (0–9).
Simple and clean for use cases like PINs, numeric tokens, or systems that disallow letters and symbols.

#### Parameters

| Parameter | Type  | Description                                                                            |
| --------- | ----- | -------------------------------------------------------------------------------------- |
| `length`  | `int` | Total length of the password. If `0`, falls back to the class default (`self.length`). |


## 🧪 Example: 8-digit Numeric Password

``` python
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_only_numbers_password(length=8)
print(password)  # e.g., 40958372
```

###### ⚠️ Notes:
- Only characters used: 0123456789
- Length must be positive. If not provided, class default (e.g., 12) is used.
- No letter or symbol will be included.

---

## 🔠 generate_only_letters_password()

- Generates a password using only letters (a–z, A–Z).
- Generates a password made of letters only, with optional control over letter casing (lower, upper, or mixed).
Ideal if you need a password without numbers or symbols, for example for testing purposes or if your system prevents special characters.



#### Parameters

| Parameter                             | Type  | Description                                                                               |
| ------------------------------------- | ----- | ----------------------------------------------------------------------------------------- |
| `length`                              | `int` | Total length of the password. If `0`, it falls back to the class default (`self.length`). |
| `Case_of_letters`                     | `str` | Case of letters to use:                                                                   |
|   - `"lower"` → lowercase only (a–z)  |       |                                                                                           |
|   - `"upper"` → uppercase only (A–Z)  |       |                                                                                           |
|   - `"mixed"` → mix of both (default) |       |                                                                                           |


## 🧪 Example 1: Mixed Case Letters

``` pyhton
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_only_letters_password(length=10)
print(password)  # e.g., AbcdEfGhIj
```

## 🧪 Example 2: Lowercase Only

``` python
password = gen.generate_only_letters_password(length=8, Case_of_letters="lower")
print(password)  # e.g., xhdswjqe
```



###### ⚠️ Notes:
- The method avoids digits and symbols entirely.
- If Case_of_letters is invalid, it defaults to "mixed" automatically.
- Great for systems that only allow alphabetic input or where simplicity is required.

---

## 🔣 generate_only_symbols_password()

- Generates a password made entirely of symbols, with no letters or numbers.
- Useful for testing, special systems, or generating high-entropy random tokens.

#### Parameters

| Parameter | Type  | Description                                                                            |
| --------- | ----- | -------------------------------------------------------------------------------------- |
| `length`  | `int` | Total password length. If set to `0`, falls back to the class default (`self.length`). |


``` pyhton
from smartpassgen import PasswordGenerator

gen = PasswordGenerator()
password = gen.generate_only_symbols_password(length=6)
print(password)  # e.g., @^*!&$
```

###### ⚠️ Notes:
- Symbols are selected from a default symbol set:
!@#$%^&*()-_=+[]{}|;:,.<>?/
- Output contains only symbols, no digits or letters.
- If no length is specified, the default from the class will be used.

---

## 🔐 generate_otp_password()

- Generates a One-Time Password (OTP) with full control over its components — letters, numbers, symbols, and casing.
- Suitable for authentication systems or temporary codes.


#### Parameters

| Parameter         | Type              | Description                                                                           |
| ----------------- | ----------------- | ------------------------------------------------------------------------------------- |
| `length`          | `int`             | Total OTP length. If `0`, uses class default (`self.length`).                         |
| `include_numbers` | `bool`            | Whether to include digits (0–9). Default is `True`.                                   |
| `include_letters` | `bool`            | Whether to include alphabetic characters. Default is `True`.                          |
| `include_symbols` | `bool`            | Whether to include symbols. Default is `False`.                                       |
| `letter_case`     | `str`             | Case of letters to include: `"lower"`, `"upper"`, or `"mixed"`. Default is `"mixed"`. |
| `numbers_ratio`   | `float` or `None` | Ratio of digits in the OTP (0.0–1.0). Optional.                                       |
| `symbols_ratio`   | `float` or `None` | Ratio of symbols in the OTP. Optional.                                                |


## 🧪 Example 1: Default OTP (letters + digits)

``` pyhton
gen = PasswordGenerator()
otp = gen.generate_otp_password(length=6)
print(otp)  # e.g., A7f3K2
```

## 🧪 Example 2: Digits Only OTP

``` pyhton
otp = gen.generate_otp_password(length=6, include_letters=False, include_symbols=False)
print(otp)  # e.g., 738194
```

## 🧪 Example 3: OTP With Symbols and Custom Ratios

``` pyhton
otp = gen.generate_otp_password(length=8, include_symbols=True, symbols_ratio=0.25, numbers_ratio=0.5)
print(otp)  # e.g., 48f#K7m!
```
###### ⚠️ Notes

- If all include flags (letters, numbers, symbols) are False, the function raises an error.
- Ratios (numbers_ratio, symbols_ratio) are optional. If not set, characters are distributed randomly.
- The OTP is randomized every call — even with the same settings.

---

## 🧠 generate_passphrase()

Generates a passphrase made of multiple random words.
Great for human-readable passwords or memory-friendly secure phrases.

#### Parameters

| Parameter     | Type   | Description                                                                                                 |
| ------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| `count_words` | `int`  | Number of words to include in the passphrase. Default is `4`.                                               |
| `join_words`  | `bool` | If `True`, returns the words as a single string (joined). If `False`, returns a list.                       |
| `separator`   | `str`  | Used to join words when `join_words=True`. Default is double space (`"  "`). Ignored if `join_words=False`. |

## 🧪 Example 1: Joined Passphrase


``` pyhton
gen = PasswordGenerator()
phrase = gen.generate_passphrase(count_words=4, join_words=True, separator="-")
print(phrase)  # e.g., bright-mouse-lake-train
```

## 🧪 Example 2: Passphrase as List


``` pyhton
words = gen.generate_passphrase(count_words=3, join_words=False)
print(words)  # e.g., ['apple', 'storm', 'circle']
```

###### ⚠️ Notes
- The word list must be available (e.g., words_list.txt) for this function to work.
- You can adjust count_words to increase or decrease passphrase complexity.
- separator gives you full control over the format (e.g., space, hyphen, underscore, etc.).

---

## 🧪 generate_hex_password()

Generates a random hexadecimal string using characters from 0–9 and a–f (or A–F if uppercase is enabled).
Useful for generating random hashes, IDs, tokens, or even color codes.

#### Parameters
| Parameter   | Type   | Description                                                                     |
| ----------- | ------ | ------------------------------------------------------------------------------- |
| `length`    | `int`  | Total length of the hex string. If `0`, uses the class default (`self.length`). |
| `hex_upper` | `bool` | If `True`, the hex characters will be uppercase (`A–F`). Default is `False`.    |

## 🧪 Example 1: Default Lowercase Hex


``` python 
gen = PasswordGenerator()
hex_code = gen.generate_hex_password(length=8)
print(hex_code)  # e.g., a1f3c8b9
```

## 🧪 Example 2: Uppercase Hex

``` python 
hex_code = gen.generate_hex_password(length=6, hex_upper=True)
print(hex_code)  # e.g., 4D9FAE
```

## 🧪 Use Case Example: Random Color Code

``` pyhton
color = "#" + gen.generate_hex_password(length=6)
print(color)  # e.g., #3fa92c
```

- The output is not cryptographically secure but sufficient for general use.
- If you need even-length hex strings (e.g. for byte representations), set length accordingly.
- Does not include any non-hex characters — strictly 0–9 and a–f or A–F.

---

🔓 generate_valid_pattern_lock()
Generates a valid Android-style pattern lock consisting of a sequence of numbers from a 3×3 grid (1–9).
The generated pattern respects real-world gesture rules — no skipping over dots unless intermediate ones are already used.

#### Parameters

| Parameter | Type  | Description                                                                   |
| --------- | ----- | ----------------------------------------------------------------------------- |
| `length`  | `int` | Number of points in the pattern. Must be between `3` and `9`. Default is `4`. |

📱 How It Works

The pattern is based on a 3×3 grid, where:

```
1 2 3
4 5 6
7 8 9
```

- Movement rules follow the logic of actual Android pattern locks:
- You can’t jump over a point unless it was already used.
For example: going from 1 to 3 directly will skip 2, so it's invalid unless 2 was already included.
- The result is always a valid gesture path.

🧪 Example

``` pyhton
gen = PasswordGenerator()
pattern = gen.generate_valid_pattern_lock(length=5)
print(pattern)  # e.g., [1, 2, 5, 8, 9]
```

### 💡 Use Cases
- Simulate Android lock patterns for UI or logic testing
- Generate pattern-based access codes
- Game mechanics or puzzle systems
- Study gesture security or build training datasets

###### ⚠️ Notes
- The minimum allowed length is 3.
- The maximum is 9 (uses all dots on the grid).
- The output is a list of digits (1–9) representing the gesture order.

---

## 📏 resolve_length()

Returns a random integer length between a minimum (main_length) and a maximum (max_length).
Used to dynamically define the password length in other functions when you want randomization within safe bounds.

| Parameter     | Type  | Description                                    |
| ------------- | ----- | ---------------------------------------------- |
| `main_length` | `int` | The minimum value (inclusive). Default is `1`. |
| `max_length`  | `int` | The maximum value (inclusive). **Required**.   |

🔍 Behavior & Validation
- If main_length >= max_length, the function raises an error or warning.
- Ensures the random length is always within the expected range.
- Helps avoid hardcoding lengths when testing or generating variable-size passwords.

``` python 
gen = PasswordGenerator()
length = gen.resolve_length(main_length=8, max_length=16)
print(length)  # e.g., 12 (randomly chosen between 8 and 16)
``` 

## 🔁 Using resolve_length() with the Class or Any Method
You can use resolve_length() to dynamically generate a random length within a safe range — then use that length with any password generation method that accepts a length parameter.

## 🧪 Example


``` pyhton
from smartpassgen import PasswordGenerator

# Create an instance
gen = PasswordGenerator()

# Dynamically decide the length (e.g., between 8 and 32)
length = gen.resolve_length(main_length=8, max_length=32)

# Use it with any generator method
strong_pass = gen.generate_strong_password(length=length)
hex_code   = gen.generate_hex_password(length=length)
pin_code   = gen.generate_only_numbers_password(length=length)

print("Strong Password:", strong_pass)
print("HEX Code:", hex_code)
print("PIN:", pin_code)
```

#### 🔧 Why Use It?
- Removes the need to hardcode lengths
- Ensures flexibility and randomness in testing or production
- Helps avoid invalid lengths or manual adjustments


###### ⚠️ Notes
- You must provide a max_length.
- Always ensure main_length < max_length to avoid runtime issues.
- Great for making password generation more dynamic and flexible.



----

## 🧪 Quick Full Example

Below is a complete test that demonstrates all the features of `smartpassgen` in one go:

```python
import random
from smartpassgen import PasswordGenerator

Password_generator = PasswordGenerator()

# Generate a dynamic length for flexibility
length = Password_generator.resolve_length(main_length=8, max_length=32)
pin = Password_generator.generat_Pin(6)
password = Password_generator.generate_strong_password(length=length)
generate_custom_charset_password = Password_generator.generate_custom_charset_password(length=length, custom_charset="abcd1234")

print(f"\nGenerated Length: {length}\n")

# Main Password Types
print(f"Generated Strong Password: {password}")
print(f"Generated Alphanumeric Password: {Password_generator.generate_alphanumeric_password(length=length, Case_of_letters='mixed')}")
print(f"Generated Custom Charset Password: {generate_custom_charset_password}\n")

# Individual Character Types
print(f"Generated Only Letters Password: {Password_generator.generate_only_letters_password(length=length, Case_of_letters='mixed')}")
print(f"Generated Only Numbers Password: {Password_generator.generate_only_numbers_password(length=length)}")
print(f"Generated Only Symbols Password: {Password_generator.generate_only_symbols_password(length=length)}\n")

# PIN and OTP
print(f"Generated PIN: {pin}")
print(f"Generated OTP Password: {Password_generator.generate_otp_password(length=8, include_numbers=True, include_letters=False, include_symbols=False, letter_case='mixed')}\n")

# Other Generators
print(f"Generated Passphrase: {Password_generator.generate_passphrase(join_words=False, count_words=length, separator='  ')}")
print(f"Generated Hex Password: {Password_generator.generate_hex_password(length=8, hex_upper=True)}")
print(f"Generated Pattern Lock: {Password_generator.generate_valid_pattern_lock(length=random.randint(3, 9))}\n")
```

