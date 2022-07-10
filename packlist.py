import os
import re


def get_notes() -> tuple[list[str], list[str]]:
    """Returns a list of the delivery notes in cwd and a list of WE nots in cwd"""
    path = os.path.dirname(__file__)
    files = os.listdir(path)
    del_notes = [file for file in files if file.startswith(('Del', 'lnb'))]
    we_notes = [file for file in files if file.startswith('kfm')]
    return del_notes, we_notes


def process_delivery_note(filename: str) -> list[str]:
    csv_parts = []
    replaced = False

    # read the raw file data
    with open(filename) as file:
        data = file.read()

    # remove back-ordered parts
    data = data.split('LIST OF BACKORDERS')[0]

    # extract the delivery reference
    note_number = re.search(r'NR. : (\w*)', data).group(1)

    # loop through orders in delivery
    orders = data.split('DELIVERY ACCORDING ORDER NR : ')[1:]
    for order in orders:
        order = order.strip()
        order_number = re.search(r'[A-Z]{1,3}\d{5}[A-Z]?', order).group()
        for order_line in order.split('\n')[1:]:
            # break after the end of the order (blank line)
            if not order_line:
                break
            # skip any line containing 'replaced by'
            elif 'replaced by' in order_line:
                continue
            # if the line contains 'replaces' replace the next line's part number with the current part number
            elif 'replaces' in order_line:
                part_number = re.search(r'((KIT)?\w\d{4}[-BCT]\w{5}([-JN][\dA-Z]{3})?)', order_line).group()
                replaced = True
            else:
                if not replaced:
                    part_number = re.search(r'((KIT)?\w\d{4}[-BCT]\w{5}([-JN][\dA-Z]{3})?)', order_line).group()
                quantity = order_line[-3:]
                csv_parts.append(f'{note_number},{order_number},{part_number},{quantity}\n')

    return csv_parts


def main():
    del_parts = []
    del_notes, we_notes = get_notes()
    for note_filename in del_notes:
        del_parts.extend(process_delivery_note(note_filename))

    with open('output.csv', 'w') as file:
        file.writelines(del_parts)


if __name__ == '__main__':
    main()
