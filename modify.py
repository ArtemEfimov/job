"""Merge data

Run this script from terminal.

You must located in App directory.

command: python3 modify.py --percent 10 -p increase         to merge price and stock and increase price on 10 percent (that can be any digit)

command: python3 modify.py --percent 10 -p reduce           to merge price and stock reduce price on 10 percent (that can be any digit)

command: python3 modify.py                                  to merge price and stock

Note:
    it merges price and stock only if same items in different files.

"""


import argparse
from glob import glob
import json
import os
import sys


parser = argparse.ArgumentParser()

parser.add_argument('--percent', type=int)
parser.add_argument('-p', '--action', help="type  'increase', 'reduce'. Attention: case-sensitive")
args = parser.parse_args()

def get_avg(*items):
    return round(sum(items) / len(items), 3)

def get_avg_price(*items, percent):
    if args.action == 'increase':
        tmp = round(sum(items) / len(items), 3)
        val = tmp / 100 * percent
        tmp += val
        return round(tmp, 3)
    elif args.action == 'reduce':
        tmp = round(sum(items) / len(items), 3)
        val = tmp / 100 * percent
        tmp -= val
        return round(tmp, 3)
    else:
        return round(sum(items) / len(items), 3)


def get_merge_stock(*args) -> str:
    """ Merge values"""
    return str(sum(args))


def create_list(filenames: str, components: list, directory: str) -> list:
    """Create items list which will use to make merge.json"""
    for file in filenames:
        if not os.stat(os.path.join(sys.path[0] + f'/{directory}/', file)) == 0:
            with open(file) as f:
                tmp = json.load(f)
                components.extend(tmp)
    return components


def get_json_files(path: str, backup_path: str) -> list:
    """ Get json files from /output directory"""
    components = []
    # check files in the 'output' directory
    # if not empty dump to data
    filenames = glob(path)
    if filenames:
        directory = '/output/'
        create_list(filenames, components, directory)
    # use backup directory if output directory is empty
    else:
        filenames = glob(backup_path)
        directory = '/backup/'
        create_list(filenames, components, directory)
    return components


def merge(components: list, items: dict):
    """ Create .json with custom 'price' values and merge 'stock' values"""
    for prod in components:
        if prod['name'] not in items:
            items[prod['name']] = []
        items[prod['name']].append(prod)
    for key, val in items.items():
        price = [(float(p['price'])) for p in val]
        stock = [int(s['stock']) for s in val]
        av_price = get_avg_price(*price, percent=args.percent)
        mg_stock = get_merge_stock(*stock)
        items[key][0]['price'] = av_price
        items[key][0]['stock'] = mg_stock
        items[key][0].pop('name', None)
        items[key] = items[key][0]
    with open('modified_values3.json', 'w') as f:
        json.dump(items, f)


def main():
    """Main function"""
    items = {}
    path = os.path.join(sys.path[0] + '/output/', '*.json')
    backup_path = os.path.join(sys.path[0] + '/backup/', '*.json')
    components = get_json_files(path, backup_path)
    merge(components, items)


if __name__ == '__main__':
    main()
