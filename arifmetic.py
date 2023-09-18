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

def decode():
    encoded_file = open('encoded', 'rb')
    encoded_data_bytes = encoded_file.read()
    # print(encoded_data_bytes)
    original_file_length = int.from_bytes(encoded_data_bytes[0:4], 'little')
    unique_byte_count = encoded_data_bytes[4]+1
    print(original_file_length, unique_byte_count)
    header_bytes = encoded_data_bytes[5: 5*unique_byte_count+5]
    byte_frequencies = dict()
    for i in range(unique_byte_count):
        byte_value = header_bytes[i*5]
        frequency = int.from_bytes(header_bytes[i*5+1:i*5+5], 'little')
        byte_frequencies[byte_value] = frequency
    probabilities = calculate_probabilities(byte_frequencies, original_file_length)
    print(probabilities)


if __name__ == "__main__":
    source_file = open('source', 'rb')
    input_bytes = source_file.read()
    bytes_freq = dict(Counter(input_bytes))
    # print(bytes_freq)
    encoded_sequence = arithmetic_encode(input_bytes, bytes_freq)
    # print(encoded_sequence)
    encoded_sequence_str = ''.join(map(str, encoded_sequence))

    padding_bits_count = 8 - len(encoded_sequence_str) % 8
    encoded_sequence_str += "0"*padding_bits_count
    
    print(len(input_bytes), (len(bytes_freq.keys())-1))
    encoded_file = open('encoded','wb')
    encoded_file.write(len(input_bytes).to_bytes(4,'little'))
    encoded_file.write((len(bytes_freq.keys())-1).to_bytes(1, 'little'))
    for byte_value, frequency in bytes_freq.items():
        encoded_file.write(byte_value.to_bytes(1, 'little'))
        encoded_file.write(frequency.to_bytes(4, 'little'))
    encoded_file.close()
    source_file.close()

    decode()