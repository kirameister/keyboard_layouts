#!/usr/bin/python
import argparse
import codecs
import itertools
import re
import sys
'''
Usage:
    cat a | xargs -I{} sh -c './permutate_3_key_combos.py ./simultaneous/LAYOUT.tsv {}'
where `a` is in following format:
[a-z]{3,3} HIRAGANA
'''


def main(args):
    input_to_pending_dict = dict()
    input_to_output_dict = dict()
    with open(args.tsv_file) as f:
        lines = f.readlines()
    # first, just read the 1-char input only..
    for line in lines:
        line = line.rstrip()
        if(re.search('{!}', line)):
            continue
        blocks = line.split('\t')
        if(not re.search('^[a-z]$', blocks[0])):
            continue
        if(len(blocks) == 3):  # include pending..
            input_to_pending_dict[blocks[0]] = blocks[2]
        else:  # only the output
            input_to_output_dict[blocks[0]] = blocks[1]
    # ..and check that all the 3 keys are already defined (they need to be..)
    input_chars_list = list(args.input_key_combos)
    for input_char in input_chars_list:
        if(input_char not in input_to_pending_dict):
            print(f'{input_char} is not defined as an independent input or only has the output value to "Output" column. Consider adding an entry to pending. Exiting..')
            sys.exit(1)
    # second, read the TSV for 2-char inputs..
    for line in lines:
        line = line.rstrip()
        if(re.search('{!}', line)):
            continue
        blocks = line.split('\t')
        if(len(list(blocks[0])) != 2):
            continue
        if(len(blocks) == 3):  # include pending..
            input_to_pending_dict[blocks[0]] = blocks[2]
        else:  # only the output
            input_to_output_dict[blocks[0]] = blocks[1]

    # create permutation
    input_permutations = list(itertools.permutations(input_chars_list))
    # start printing permutations..
    permutated_input_output_dict = dict()
    for permutated_input in input_permutations:
        [c1, c2, c3] = list(permutated_input)
        c1 = input_to_pending_dict[c1]
        c1c2 = c1 + c2
        if(c1c2 in input_to_output_dict):
            print(f'"{c1c2}" => {input_to_output_dict[c1c2]} input found with output-only entry. Consider move the output to pending')
            c1c2 = input_to_output_dict[c1c2]
        else:
            c1c2 = input_to_pending_dict[c1c2]
        permutated_input_output_dict[c1c2 + c3] = args.output_hiragana
    for i, o in permutated_input_output_dict.items():
        print(f'{i}\t{o}')
        if(args.update):
            with open(args.tsv_file, 'a') as f:
                print(f'{i}\t{o}', file=f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Permutate 3-key combos for a given stroke inputs and output')
    parser.add_argument('tsv_file', help='TSV file path where existing roman table is contained')
    parser.add_argument('input_key_combos', help='input key-stroke combos (in ASCII), 3 chars are expected and order does not matter')
    parser.add_argument('output_hiragana', help='expected output from the 3-key combos')
    parser.add_argument('-u', '--update', action='store_true', help='update the TSV file by appending the permutated entries')
    args = parser.parse_args()

    main(args)
