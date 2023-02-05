from augmentation.refactoring_methods import *
from augmentation.generate_refactoring import generate_adversarial
import argparse
import ast
import multiprocessing
import os
from utils import tokenize
import json
import sys
import time
import logging


class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)


def process_method(l):
    dct = ast.literal_eval(l)
    method = dct['method']
    index = dct['index']

    json_file.write(json.dumps(dct) + '\n')
    json_file.flush()

    K = 1
    for transformation in refactors_list:
        code = f'public class DummyClass {{\n\t{method}\n}}'
        new_code = generate_adversarial(K, code, transformation)

        if new_code is not '':

            new_code = '\n'.join(new_code.split('\n')[1:-1])
            code = '\n'.join(code.split('\n')[1:-1])

            if new_code == code: continue

            with open(f'{args.project_name}.{transformation.__name__}.{index}.java', mode='w', encoding="ISO-8859-1", errors='ignore') as fw:
                fw.write(new_code)

            os.system(f'tokenizer {args.project_name}.{transformation.__name__}.{index}.java > {args.project_name}.{transformation.__name__}.{index}.txt')
            tokens = tokenize(f'{args.project_name}.{transformation.__name__}.{index}.txt')

            dataset = {'index': f'{index}-{transformation.__name__}', 'method': new_code, 'tokens': tokens}

            json_file.write(json.dumps(dataset) + '\n')
            json_file.flush()

            os.remove(f'{args.project_name}.{transformation.__name__}.{index}.txt')
            os.remove(f'{args.project_name}.{transformation.__name__}.{index}.java')

            with counter.val.get_lock():
                counter.val.value += 1


def main(args):
    global json_file
    global refactors_list
    global counter

    start = time.time()

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'applying transformations on {args.project_name}')

    counter = Counter()

    refactors_list = [  rename_argument, return_optimal, add_arguments, rename_api,
                        rename_local_variable, add_local_variable, rename_method_name, 
                        enhance_for_loop, enhance_filed, enhance_if, add_print]

    lines = []
    with open(f'data/{args.project_name}/unique_methods.jsonl') as fr:
        lines = fr.readlines()

    json_file = open(f"data/{args.project_name}/unique_methods_w_transformations.jsonl", "wt")

    pool = multiprocessing.Pool(os.cpu_count())

    for i, _ in enumerate(pool.imap_unordered(process_method, lines), 1):
        sys.stderr.write('\rpercentage of methods augmented: {0:%}'.format(i/len(lines)))

    logging.info(f'total time in secs for {args.project_name}: ' + str(round(time.time() - start, 2)))
    logging.info(f'total number of transformations for {args.project_name}: ' + str(counter.val.value))


def parse_args():
    parser = argparse.ArgumentParser("augment methods of a project in a semantically preserving manner")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to augment')
    parser.add_argument('--log_file', type=str, default='method_augmentor.log', help='log file name')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
