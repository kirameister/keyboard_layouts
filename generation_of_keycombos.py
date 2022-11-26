#!/usr/bin/python
import argparse
import itertools
import re
import sys

input_chars = '1234567890-qwertyuiop[]asdfghjl;zxcvbnm,./@'
input_chars_set = set(input_chars)
max_combo_len = 4


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def store_lines_to_dict_list(ascii_to_hiragana_table, lines, delimiter):
    for line in lines:
        if(re.search('^###', line)):  # ignore the comment lines
            continue
        line = line.rstrip()
        [input_str, hiragana] = line.split(delimiter)
        if(len(input_str) > max_combo_len):
            eprint(f'Length of input "{input_str}" in the line "{line}" is greater than {max_combo_len}. This line will be ignored.')
            continue
        ascii_to_hiragana_table[len(input_str)-1][input_str] = hiragana
        permutated_combos = list(itertools.permutations(list(input_str)))
        for permued_combo in permutated_combos:
            permued_combo = "".join(permued_combo)
            for i in range(len(ascii_to_hiragana_table)):
                if(permued_combo in ascii_to_hiragana_table[i] and hiragana != ascii_to_hiragana_table[i][permued_combo]):
                    eprint(f'There are multiple lines with the identical input "{permued_combo}". The latter will be taken.')
            ascii_to_hiragana_table[len(permued_combo)-1][permued_combo] = hiragana


def update_table_for_single_strokes(ascii_to_hiragana_table):
    '''
    This function will have a look at the 2-stroke combos,
    and add the relevant single-stroke input to the table
    '''
    for double_stroke_combo in ascii_to_hiragana_table[1].keys():
        permutated_combos = list(itertools.permutations(list(double_stroke_combo)))
        for single_input in permutated_combos[0]:
            if(single_input not in ascii_to_hiragana_table[0]):
                eprint(f'[INFO] A single-char entry for "{single_input}" is added, since it is required for combo.')
                ascii_to_hiragana_table[0][single_input] = single_input


def main(args):
    ascii_to_hiragana_table = list()
    target_table = list()
    output_to_be_in_pending_set = set()

    # first read the txt file containing "\w{2,4} {HIRAGANA}"
    with open(args.input_key_combo_file) as f:
        key_combo_lines = f.readlines()
    # ..and check the max length of key-strokes in the input
    max_input_strokes = len(key_combo_lines[-1].split(' ')[0])
    # initialize the tables..
    for i in range(max_input_strokes):
        ascii_to_hiragana_table.append(dict())
        target_table.append(dict())
    # read the original TSV file, which should contain only 1-stroke inputs
    with open(args.tsv_file) as f:
        tsv_lines = f.readlines()
    # store tsv inputs to dict
    store_lines_to_dict_list(ascii_to_hiragana_table, tsv_lines, '\t')
    # store 2-to-4-combo inputs to respective dicts
    store_lines_to_dict_list(ascii_to_hiragana_table, key_combo_lines, ' ')
    # update the ascii_to_hiragana table s.t. required 1-char input will be present
    update_table_for_single_strokes(ascii_to_hiragana_table)
    # build up the target table bottom-up (naively)..
    invalidated_flag = False
    for i, v in enumerate(ascii_to_hiragana_table):
        if(i == 0):  # goofy implementation..
            continue
        for inp, hiragana in v.items():
            prev_str = inp[0:-1]
            curr_chr = inp[-1]
            if(prev_str in ascii_to_hiragana_table[i-1]):
                target_table[i][ascii_to_hiragana_table[i-1][prev_str] + curr_chr] = hiragana
                output_to_be_in_pending_set.add(ascii_to_hiragana_table[i-1][prev_str])
                if(len(prev_str) == 1 and prev_str not in target_table[0]):
                    # this is required for only listing the required set of chars in the pending set
                    target_table[0][prev_str] = ascii_to_hiragana_table[0][prev_str]
            else:  # there is no match for prev_str, which should actually been defined
                eprint(f'[ERROR] There is no definition for the input "{prev_str}", which is required for "{inp}" => "{hiragana}"')
                invalidated_flag = True
    if(invalidated_flag):
        sys.exit(1)
    # printing the output..
    # first sipmly the original TSV contents
    print('# original TSV file minus the entries in the pending..')
    for k, v in ascii_to_hiragana_table[0].items():
        if(v not in output_to_be_in_pending_set):
            print(f'{k}\t{v}')
    # and then print out the rest..
    print('# set of the entries required for simultaneous key-combos..')
    for i, list_element in enumerate(target_table):
        for k, v in list_element.items():
            if(v in output_to_be_in_pending_set):
                print(f'{k}\t\t{v}')
            else:
                print(f'{k}\t{v}')
    print('# set of the entries for timeout..')
    for v in output_to_be_in_pending_set:
        print(v + '{!}\t' + v)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Permutate 2-to-4-key combos for a given stroke inputs and output with 1-key input')
    parser.add_argument('tsv_file', help='Path to the TSV file where roman table with seeding 1-key inputs are contained')
    parser.add_argument('input_key_combo_file', help='Path to the text file where ASCII-key combos and output Hiragana are split by a space')
    args = parser.parse_args()

    main(args)
