"""
CIF Parser and Utility Functions

This module provides tools for parsing and manipulating CIF
(Crystallographic Information File) data commonly used in crystallography.

Overview:
    The module includes:
        - A parser for CIF data that can load and process CIF files.
        - Classes for managing CIF data structures like loops and targets.
        - Utility functions for handling CIF data formatting and output.

Features:
    - Parse CIF data from files and strings.
    - Handle loop structures and data values efficiently.
    - Format and export CIF data into compatible outputs.

Credits:
    - Original Python CIF Parser: Based on [CIF Parsers by PDB Japan](https://gitlab.com/pdbjapan/tools/cif-parsers)
    - Modified by: Yinlin Chen, May 2024
    - License: BSD 3-clause
"""


def partition_string(text: str, sep: str) -> tuple:
    """Partitions a string around the first occurrence of a separator.

    Args:
        text (str): The string to partition.
        sep (str): The separator to partition around.

    Returns:
        tuple: A tuple containing the part before the separator, the
            separator itself, and the part after the separator.
    """
    return text.partition(sep)


class Loop:
    """Handles loop structures within CIF files.

    This class manages lists of references and values for loops defined
    in a CIF file, ensuring they are processed correctly.

    Attributes:
        parser_obj: Reference to the parser object handling the loop.
        ref_list (list): List of references in the loop.
        ref_id (int): Index of the current reference.
        names_defined (bool): Indicates whether names have been defined.
    """

    def __init__(self, parser_obj):
        """Initializes the Loop object.

        Args:
            parser_obj: The parser object that manages the CIF data.
        """
        self.parser_obj = parser_obj
        self.ref_list = []
        self.ref_id = -1
        self.names_defined = False

    def add_name(self, name: str):
        """Adds a name to the loop structure.

        Args:
            name (str): The name to add, including the category and key.
        """
        category_name = partition_string(name, ".") if isinstance(name, str) else ("", "", "")
        if category_name[1]:
            if category_name[0] not in self.parser_obj.current_target[-2]:
                self.parser_obj.current_target[-2][category_name[0]] = {}
            if category_name[2] not in self.parser_obj.current_target[-2][category_name[0]]:
                self.parser_obj.current_target[-2][category_name[0]][category_name[2]] = []
                self.ref_list.append(self.parser_obj.current_target[-2][category_name[0]][category_name[2]])
        else:
            if category_name[0] not in self.parser_obj.current_target[-2]:
                self.parser_obj.current_target[-2][category_name[0]] = []
            self.ref_list.append(self.parser_obj.current_target[-2][category_name[0]])
        self.ref_id = (self.ref_id + 1) % len(self.ref_list)

    def push_value(self, value: str):
        """Pushes a value into the loop structure.

        Args:
            value (str): The value to add to the loop.
        """
        if not self.names_defined:
            self.names_defined = True
        target = self.next_target()
        if value == "stop_":
            return self.stop_push()
        target.append(value)

    def next_target(self):
        """Gets the next target in the loop structure.

        Returns:
            Reference to the next list in the loop.
        """
        self.ref_id = (self.ref_id + 1) % len(self.ref_list)
        return self.ref_list[self.ref_id]

    def stop_push(self):
        """Stops adding values into the loop."""
        self.ref_id = -1


def special_split(content: str) -> list:
    """Splits content into tokens, handling quoted strings and comments.

    Args:
        content (str): The content to split.

    Returns:
        list: A list of split tokens with information about quotes.
    """
    output = [["", False]]
    quote = False
    for i, char in enumerate(content):
        is_whitespace = char in " \t"
        if char in "'\"" and (i == 0 or content[i - 1] in " \t" or i == len(content) - 1 or content[i + 1] in " \t"):
            quote = not quote
        elif not quote and is_whitespace and output[-1][0]:
            output.append(["", False])
        elif not quote and char == "#":
            break
        elif not is_whitespace or quote:
            output[-1][0] += char
            output[-1][1] = quote
    if not output[-1][0]:
        output.pop()
    return output


class TargetSetter:
    """Sets target values for the CIF parser.

    This class allows for dynamic assignment of values to keys in
    the CIF data structure.

    Attributes:
        obj: The object being targeted.
        key (str): The key in the object being set.
    """

    def __init__(self, obj, key: str):
        """Initializes the TargetSetter object.

        Args:
            obj: The object to target.
            key (str): The key to set in the object.
        """
        self.obj = obj
        self.key = key

    def set_value(self, value: str):
        """Sets a value for the target.

        Args:
            value (str): The value to set for the key.
        """
        self.obj[self.key] = value


class CIFParser:
    """Parses CIF files and manages CIF data.

    This class provides methods for reading CIF files, processing
    their content, and managing the data structure.

    Attributes:
        data (dict): Parsed CIF data stored as a dictionary.
        current_target (list): Tracks the current target in the data.
        loop_pointer (Loop): Pointer to the current loop being parsed.
    """

    def __init__(self):
        """Initializes the CIFParser object."""
        self.data = {}
        self.current_target = None
        self.loop_pointer = None

    def parse_string(self, contents: str):
        """Parses CIF data from a string.

        Args:
            contents (str): String containing CIF data.
        """
        multi_line_mode = False
        buffer = []
        for line in contents.splitlines():
            prefix = line[:1]
            line = line.strip()
            if prefix == ";":
                multi_line_mode = not multi_line_mode
                line = line[1:].strip()
                if not multi_line_mode:
                    self.set_data_value("\n".join(buffer))
                    buffer = []
            if multi_line_mode:
                buffer.append(line)
            else:
                self.process_content(special_split(line))

    def parse(self, file_obj: str):
        """Parses CIF data from a file.

        Args:
            file_obj (str): Path to the CIF file.
        """
        try:
            with open(file_obj, 'r') as file:
                self.parse_string(file.read())
        except IOError:
            print("Error opening or reading the file.")

    def process_content(self, content: list):
        """Processes content split into tokens.

        Args:
            content (list): List of tokens extracted from the CIF data.
        """
        for c, quoted in content:
            if c.startswith("data_") and not quoted:
                self.loop_pointer = None
                self.select_data(c)
            elif c.startswith("save_") and not quoted:
                self.loop_pointer = None
                if c[5:]:
                    self.select_frame(c)
                else:
                    self.end_frame()
            elif c == "loop_" and not quoted:
                self.loop_pointer = Loop(self)
            elif c.startswith("_") and not quoted:
                self.set_data_name(c[1:])
            else:
                self.set_data_value(c)

    def set_data_name(self, name: str):
        """Sets the current data name for parsing.

        Args:
            name (str): The name of the data to set.
        """
        if self.loop_pointer and not self.loop_pointer.names_defined:
            self.loop_pointer.add_name(name)
        else:
            name_parts = partition_string(name, ".")
            self.current_target.pop()
            if name_parts[1]:
                if name_parts[0] not in self.current_target[-1]:
                    self.current_target[-1][name_parts[0]] = {}
                self.current_target[-1][name_parts[0]][name_parts[2]] = ""
                self.current_target.append(TargetSetter(self.current_target[-1][name_parts[0]], name_parts[2]))
            else:
                self.current_target[-1][name_parts[0]] = ""
                self.current_target.append(TargetSetter(self.current_target[-1], name_parts[0]))

    def set_data_value(self, value: str):
        """Sets the current data value for parsing.

        Args:
            value (str): The value to set for the current data name.
        """
        if self.loop_pointer:
            self.loop_pointer.push_value(value)
        else:
            self.current_target[-1].set_value(value)

    def select_global(self):
        """Selects the global data target."""
        self.current_target = [self.data, self.data, None]

    def select_data(self, name: str):
        """Selects a specific data target.

        Args:
            name (str): The name of the data target to select.
        """
        if name not in self.data:
            self.data[name] = {}
        self.current_target = [self.data, self.data[name], None]

    def select_frame(self, name: str = ""):
        """Selects a specific frame target.

        Args:
            name (str, optional): The name of the frame to select. Defaults to "".
        """
        if name not in self.current_target[1]:
            self.current_target[1][name] = {}
        self.current_target = [self.current_target[0], self.current_target[1], self.current_target[1][name]]

    def end_frame(self):
        """Ends the current frame target."""
        self.current_target = self.current_target[:3]


def load_cif(cif_file: str) -> dict:
    """Loads CIF data from a file.

    Args:
        cif_file (str): Path to the CIF file.

    Returns:
        dict: Parsed CIF data as a dictionary.
    """
    parser = CIFParser()
    parser.parse(cif_file)
    return parser.data


def hint_to_str(key: str, value: str, length: int = 35) -> str:
    """Converts a key-value pair into a formatted CIF string.

    Args:
        key (str): The CIF data key.
        value (str): The corresponding value.
        length (int, optional): Minimum width for the key column. Defaults to 35.

    Returns:
        str: Formatted CIF string.
    """
    if not isinstance(value, str):
        value = str(value)
    if not value:
        value = "?"
    if "\n" in value:
        return f"_{key}\n;\n{value}\n;\n"
    elif " " in value:
        return f"_{key:<{length}}\'{value}\'\n"
    else:
        return f"_{key:<{length}} {value}\n"


def print_pcf(pcf_path: str, pcf_data: dict, short_name: str) -> None:
    """Writes PCF data to a file.

    Args:
        pcf_path (str): Path to the output PCF file.
        pcf_data (dict): Dictionary containing PCF data.
        short_name (str): Data block name for the PCF file.
    """
    with open(pcf_path, "w") as file:
        file.write(f"data_{short_name}\n")
        for key, value in pcf_data.items():
            file.write(hint_to_str(key, value))
