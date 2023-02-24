import javalang
import json
import os
import multiprocessing
import argparse
import sys
import subprocess
import glob
import time
from typing import Set, Tuple
from utils import tokenize
import logging

class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)


def parse_java_func_intervals(content: str) -> Set[Tuple[int, int]]:
    func_intervals = set()
    try:
        for _, node in javalang.parse.parse(content):
            if isinstance(
                node,
                (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration),
            ):
                func_intervals.add(
                    (
                        node.start_position.line,
                        node.end_position.line,
                    )
                )
        return func_intervals
    except javalang.parser.JavaSyntaxError:
        return func_intervals


def process_line(target_line):

        # Java funcname has operator overloading
        # so we use indexing for unique naming

        with counter.val.get_lock() :
            index = counter.val.value
            counter.val.value += 1

        # unsafe !
        data = eval(target_line)

        with open(f'{index}.java', mode='w', encoding="ISO-8859-1", errors='ignore') as fw:
            fw.write(data["code"])

        os.system(f'tokenizer {index}.java > {index}.txt')
        tokens = tokenize(f'{index}.txt')

        instance = {}
        instance['index'] = str(index)
        instance['project'] = data["repo"]
        instance['file_path'] = data["path"]
        instance['method'] = data["code"]
        instance['tokens'] = tokens

        json_file.write(json.dumps(instance) + '\n')
        json_file.flush()
        
        os.remove(f'{index}.txt')
        os.remove(f'{index}.java')


def main(args):

    start = time.time()

    global json_file
    global counter

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'extracting methods from {args.dataset} of CodeSearchNet-java')

    counter = Counter()
    os.makedirs(f'data/{args.dataset}', exist_ok=True)

    def get_file_number(filename) :
        return int("".join([s for s in filename if s.isdigit()]))


    total_methods_from_all_datasets = 0
    for filename in [f for f in os.listdir(args.dir) if f.endswith("jsonl")] :
    
        json_file = open(f"data/{args.dataset}/methods_{get_file_number(filename)}.jsonl", "wt")
        pool = multiprocessing.Pool(args.num_workers)
        json_file.close()

        # Get lines
        with open(os.path.join(args.dir, filename), mode='r', encoding="ISO-8859-1", errors='ignore') as r:
            datalines = r.readlines()

        for i, _ in enumerate(pool.imap_unordered(process_line, datalines), 1) :
            sys.stderr.write('\rpercentage of file completed : {0:%}'.format(i/len(datalines)))

        total_methods_extracted_from_file = counter.val.value
        counter.val.value = 0
        logging.info(f'total time in secs to extract method from {filename}: ' + str(round(time.time() - start, 2)))
        logging.info(f'total methods extracted from {filename} : ' + str(total_methods_extracted_from_file))
        total_methods_from_all_datasets += total_methods_extracted_from_file
        counter.val.value = 0
    
    logging.info(f'Done, total methods extracted from {args.dataset}: ' + str(total_methods_from_all_datasets))


def parse_args():
    parser = argparse.ArgumentParser("extract methods of a given java project")
    parser.add_argument('--dataset', type=str, required=True, help='dataset name (e.g. train, valid, or test')
    parser.add_argument('--dir', type=str, required=True, help='path to directory which contains CodeSearchNet jsonl files')
    parser.add_argument('--log_file', type=str, default='method_extractor.log', help='log file name for method extractor')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
