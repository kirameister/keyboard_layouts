#!/usr/bin/python
import argparse
import itertools
import sys

input_chars = '1234567890-qwertyuiop[]asdfghjl;zxcvbnm,./'
input_chars_set = set(input_chars)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main(args):
    strokes_to_hiragana_dict_in_list = list()
    target_table = list()

    # first read the txt file containing "\w{2,4} {HIRAGANA}"
    with open(args.input_key_combo_file) as f:
        key_combo_lines = f.readlines()
    # ..and check the max length of key-strokes in the input
    max_input_strokes = len(key_combo_lines[-1].split(' ')[0])
    # initialize the tables..
    for i in range(max_input_strokes):
        strokes_to_hiragana_dict_in_list.append(dict())
        target_table.append(dict())
    # read the original TSV file, which should contain only 1-stroke inputs
    with open(args.tsv_file) as f:
        tsv_lines = f.readlines()
    # store tsv inputs to dict
    for line in tsv_lines:
        line = line.rstrip()
        [c, hiragana] = line.split('\t')
        strokes_to_hiragana_dict_in_list[0][c] = hiragana
    # store 2-to-4-combo inputs to respective dicts
    for line in key_combo_lines:
        line = line.rstrip()
        [input_strokes, hiragana] = line.split(' ')
        if(len(input_strokes) < 2 or 4 < len(input_strokes)):
            eprint(f'Length of input "{input_strokes}" in the line "{line}" is outside of expected range from 2 to 4. This line will be ignored.')
            continue
        cs_permed = list(itertools.permutations(list(input_strokes)))
        for cs in cs_permed:
            cs = "".join(cs)
            for i in range(max_input_strokes):
                if(cs in strokes_to_hiragana_dict_in_list[i]):
                    eprint(f'There are multiple lines with the identical input "{cs}". The latter will be taken.')
            strokes_to_hiragana_dict_in_list[len(cs)-1][cs] = hiragana
    # call the recursive function for each of the
    print(strokes_to_hiragana_dict_in_list)
    # build up the target table bottom-up (naively)..
    for i,v in enumerate(strokes_to_hiragana_dict_in_list):
        if(i == 0): # goofy implementation..
            continue
        for inp, hiragana in v.items():
            prev_str = inp[0:-1]
            curr_chr = inp[-1]
            if(prev_str in strokes_to_hiragana_dict_in_list[i-1]):
                target_table[i][strokes_to_hiragana_dict_in_list[i-1][prev_str] + curr_chr] = hiragana
    print(target_table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Permutate 2-to-4-key combos for a given stroke inputs and output with 1-key input')
    parser.add_argument('tsv_file', help='Path to the TSV file where roman table with seeding 1-key inputs are contained')
    parser.add_argument('input_key_combo_file', help='Path to the text file where ASCII-key combos and output Hiragana are split by a space')
    parser.add_argument('-u', '--update', action='store_true', help='update the TSV file by appending the permutated entries')
    args = parser.parse_args()

    main(args)
