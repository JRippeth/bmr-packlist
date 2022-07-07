import os
import re


def get_notes() -> tuple[list[str], list[str]]:
    """Returns a list of the delivery notes in cwd and a list of WE nots in cwd"""
    path = os.path.dirname(__file__)
    files = os.listdir(path)
    del_notes = [file for file in files if file.startswith(('Del', 'lnb'))]
    we_notes = [file for file in files if file.startswith('kfm')]
    return del_notes, we_notes


def process_del_note(filename: str) -> list[str]:
    """Returns a list of parts contained within the del note in the format:
    '{note_number}, {order_number}, {part_number}, {quantity}'"""
    note_pattern = re.compile(r'NR. : (\w*)')
    order_pattern = re.compile(r'\d\(([A-Z]{1,3}\d{5}[A-Z]?)')
    replacement_pattern_1 = re.compile(r'(\w{5}[-BCT]\w{5}([-JN][\dA-Z]{3})? replaces :)')
    replacement_pattern_2 = re.compile(r'(\w{5}[-BCT]\w{5}([-JN][\dA-Z]{3})? is replaced by :)')
    part_pattern = re.compile(r'(\w\d{4}[-BCT]\w{5}([-JN][\dA-Z]{3})?).*\s(\d{1,3})\n')

    parts = []
    note_number = ''
    order_number = ''

    # read the contents of the file
    with open(filename) as file:
        lines = file.readlines()

    # loop over the contents of the file
    for line in lines:
        # extract the note number
        if match := note_pattern.findall(line):
            note_number = match[0]
        # extract replaces line
        elif match := replacement_pattern_1.findall(line):
            parts.append(f',,{match[0][0]}\n')
        # extract replaced by line
        elif match := replacement_pattern_2.findall(line):
            parts.append(f',,{match[0][0]}\n')
        # extract order number
        elif match := order_pattern.findall(line):
            order_number = match[0]
        # extract part number and quantity
        elif match := part_pattern.findall(line):
            part_number, _, quantity = match[0]
            parts.append(f'{note_number}, {order_number}, {part_number}, {quantity}\n')

    return parts


def main():
    del_parts = []
    del_notes, we_notes = get_notes()
    for note_filename in del_notes:
        del_parts.extend(process_del_note(note_filename))

    with open('output.csv', 'w') as file:
        file.writelines(del_parts)


if __name__ == '__main__':
    main()
