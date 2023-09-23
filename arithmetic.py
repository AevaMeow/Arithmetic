#!/usr/bin/env python3
from collections import Counter

def calculate_probabilities(chars_count, len_text):
    return {ch: count / len_text for ch, count in chars_count.items()}

def arithmetic_encode(source_bytes, bytes_freq):
    # диапазоны
    MAX_VALUE = 4294967295
    THREE_QUARTERS = 3221225472
    ONE_QUARTER = 1073741824
    HALF = 2147483648

    bytes_freq = Counter(source_bytes)
    probabilities = calculate_probabilities(bytes_freq, len(source_bytes))
    cumulative_freq = [0.0]
    for symbol in probabilities.values():
        cumulative_freq.append(cumulative_freq[-1] + symbol)
    cumulative_freq.pop()
    cumulative_freq = {k: v for k, v in zip(probabilities.keys(), cumulative_freq)}
    encoded_numbers = []
    lower_bound, upper_bound = 0, MAX_VALUE
    straddle = 0

    for byte in source_bytes:
        range_width = upper_bound  - lower_bound + 1
        lower_bound += range_width * cumulative_freq[byte]
        upper_bound = lower_bound + range_width * probabilities[byte]
        temporary_numbers = []
        while True:
            if upper_bound < HALF:
                temporary_numbers.append(0)
                temporary_numbers.extend([1]*straddle)
                straddle = 0
            elif lower_bound >= HALF:
                temporary_numbers.append(1)
                temporary_numbers.extend([0]*straddle)
                straddle = 0
                lower_bound -= HALF
                upper_bound -= HALF
            elif lower_bound >= ONE_QUARTER and upper_bound < THREE_QUARTERS:
                straddle += 1
                lower_bound -= ONE_QUARTER
                upper_bound -= ONE_QUARTER
            else:
                break
            if temporary_numbers:
                encoded_numbers.extend(temporary_numbers)
                temporary_numbers = []
            lower_bound *= 2
            upper_bound = 2 * upper_bound + 1

    encoded_numbers.extend([0] + [1]*straddle if lower_bound < ONE_QUARTER else [1] + [0]*straddle)
    return encoded_numbers

def arithmetic_decode():
    print(1)

def decode():
    encoded_file = open('encoded', 'rb')
    encoded_data_bytes = encoded_file.read()

    original_file_length = int.from_bytes(encoded_data_bytes[0:4], 'little')

    unique_byte_count = encoded_data_bytes[4]+1

    header_bytes = encoded_data_bytes[5: 5*unique_byte_count+5]

    byte_frequencies = dict()
    for i in range(unique_byte_count):
        byte_value = header_bytes[i*5]
        frequency = int.from_bytes(header_bytes[i*5+1:i*5+5], 'little')
        byte_frequencies[byte_value] = frequency

    probabilities = calculate_probabilities(byte_frequencies, original_file_length)

    encoded_text_bytes = encoded_data_bytes[5* (encoded_data_bytes[4]+1)+5:]
    padded_encoded_str = ''.join([bin(byte)[2:].rjust(8, '0') for byte in encoded_text_bytes])

    padding_bits_count = int(padded_encoded_str[: 8], 2)
    encoded_sequence = padded_encoded_str[8: -padding_bits_count if padding_bits_count!=0 else None]
    encoded_sequence = [int(bit) for bit in encoded_sequence]
    arithmetic_decode()
    encoded_file.close()

    

def encode():
    source_file = open('source', 'rb')
    input_bytes = source_file.read()
    bytes_freq = dict(Counter(input_bytes))

    encoded_sequence = arithmetic_encode(input_bytes, bytes_freq)
    encoded_sequence_str = ''.join(map(str, encoded_sequence))

    padding_bits_count = 8 - len(encoded_sequence_str) % 8
    encoded_sequence_str += "0"*padding_bits_count

    padding_info_str = "{0:08b}".format(padding_bits_count)
    padded_encoded_str = padding_info_str + encoded_sequence_str

    output_byte_array = bytearray([int(padded_encoded_str[i:i+8], 2) for i in range(0, len(padded_encoded_str), 8)])
    
    encoded_file = open('encoded','wb')
    encoded_file.write(len(input_bytes).to_bytes(4,'little'))
    encoded_file.write((len(bytes_freq.keys())-1).to_bytes(1, 'little'))

    for byte_value, frequency in bytes_freq.items():
        encoded_file.write(byte_value.to_bytes(1, 'little'))
        encoded_file.write(frequency.to_bytes(4, 'little'))

    encoded_file.write(bytes(output_byte_array))
    encoded_file.close()
    source_file.close()

if __name__ == "__main__":
    
    encode()
    decode()