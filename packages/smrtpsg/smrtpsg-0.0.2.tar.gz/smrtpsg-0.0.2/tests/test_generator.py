import random

from smartpassgen import PasswordGenerator   # 👈 استورد من generator.py مباشرة

Password_generator = PasswordGenerator() 
pin = Password_generator.generat_Pin(6)
length = Password_generator.resolve_length(main_length=8,max_length=32)
password = Password_generator.generate_strong_password(length=length)
generate_custom_charset_password = Password_generator.generate_custom_charset_password(length=length, custom_charset="abcd1234")
print(f"\nGenerated Length: {length}\n")

# الأهم
print(f"Generated Strong Password: {password}")
print(f"Generated Alphanumeric Password: {Password_generator.generate_alphanumeric_password(length=length, Case_of_letters='mixed')}")
print(f"Generated Custom Charset Password: {generate_custom_charset_password}\n")

# حروف وأرقام منفصلة
print(f"Generated Only Letters Password: {Password_generator.generate_only_letters_password(length=length, Case_of_letters='mixed')}")
print(f"Generated Only Numbers Password: {Password_generator.generate_only_numbers_password(length=length)}")
print(f"Generated Only Symbols Password: {Password_generator.generate_only_symbols_password(length=length)}\n")

# PIN و OTP
print(f"Generated PIN: {pin}")
print(f"Generated OTP Password: {Password_generator.generate_otp_password(length=8, include_numbers=True, include_letters=False, include_symbols=False, letter_case='mixed')}\n")

# كلمات طويلة وأساليب أخرى
print(f"Generated Passphrase: {Password_generator.generate_passphrase(join_words=False, count_words=length, separator='  ')}")
print(f"Generated Hex Password: {Password_generator.generate_hex_password(length=8, hex_upper=True)}")
print(f"Generated Pattern Lock: {Password_generator.generate_valid_pattern_lock(length=random.randint(3, 9))}\n")

