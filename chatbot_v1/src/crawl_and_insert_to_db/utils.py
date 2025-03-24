import re

# Hàm chuyển các số la mã thành số thập phân
def convert_roman_to_num(roman_num):
    roman_num = roman_num.upper()
    roman_to_num = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    num = 0
    for i in range(len(roman_num)):
        romain_char = roman_num[i]
        if romain_char not in roman_to_num.keys():
            num += alphabet.index(romain_char) + 1
            continue
        if i > 0 and roman_to_num[romain_char] > roman_to_num[roman_num[i - 1]]:
            num += roman_to_num[romain_char] - 2 * roman_to_num[roman_num[i - 1]]
        else:
            num += roman_to_num[romain_char]
    return num

# Hàm trích xuất mapc từ mục liên quan
def extract_input(input_string):
    pattern = r"\((.*?)\)"
    match = re.search(pattern, input_string)

    if match:
        return match.group(1)
    else:
        return None