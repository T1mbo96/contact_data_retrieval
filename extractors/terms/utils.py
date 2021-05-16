from typing import List


def contains_complete_content(line: str):
    clean: List[str] = list(filter(None, line.split(' ')))

    return not clean[len(clean) - 1][-1] == ':' or not clean[len(clean) - 1][-1] == ','


def is_standalone(term: str, line: str) -> bool:
    if line.find(term) == 0:
        return True

    if is_number(line[line.index(term) - 1]) or is_valid_special_character_start(
            line[line.index(term) - 1]):
        return True

    if is_number(line[line.index(term) + len(term)]) or is_valid_special_character_end(line[line.index(term) + len(term)]):
        return True

    return False


def is_number(character: str):
    try:
        num = float(character)
        # check for "nan" floats
        return num == num  # or use `math.isnan(num)`
    except ValueError:
        return False


def is_valid_special_character_start(character: str):
    valid_special_characters: str = '-:/\\.'

    return character in valid_special_characters


def is_valid_special_character_end(character: str):
    valid_special_characters: str = '-: /\\.'

    return character in valid_special_characters
