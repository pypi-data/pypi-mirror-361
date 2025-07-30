# sets/init.py
# -- Import modules from the files --
from _5x8 import _set_5x8 as set_5x8
from _10x14 import _set_10x14 as set_10x14

# -- Define a mapping from set_name string to the actual set dictionary --
_available_sets = {
    "5x8": set_5x8,
    "10x14": set_10x14,
}

# -- Define the get_pattern function. It returns a recursive list of booleans that represent the pattern for a specific character --
def get_pattern(pattern_char: str, set_name: str = "5x8"):
    selected_set = _available_sets.get(set_name)

    if not selected_set:
        print(f"Error: Character set '{set_name}' not found.")
        return None

    string_pattern_list = selected_set.get(pattern_char)

    if not string_pattern_list:
        print(f"Error: Pattern for character '{pattern_char}' not found in set '{set_name}'.")
        return None

    # Convert the string list to a recursive list of booleans
    boolean_pattern = []
    for row_str in string_pattern_list:
        boolean_row = [char == '#' for char in row_str]
        boolean_pattern.append(boolean_row)

    return boolean_pattern

# -- Export function(s) --
__all__ = ["get_pattern"]