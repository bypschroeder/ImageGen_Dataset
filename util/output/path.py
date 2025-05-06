import os
import re


def get_next_index(output_dir):
    files = [f for f in os.listdir(output_dir) if re.match(r"\d{3}", f)]

    if files:
        numbers = [int(re.search(r"\d{3}", f).group()) for f in files]
        next_index = max(numbers) + 1
    else:
        next_index = 0

    return f"{next_index:03}"
