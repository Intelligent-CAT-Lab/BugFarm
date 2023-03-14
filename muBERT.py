import json
import javalang
from typing import Set, Tuple
import os
import gzip
import multiprocessing
import sys
import pickle5 as p


def load_zipped_pickle(filename):
    print('loading cached data from = {0}'.format(filename))
    with gzip.open(filename, 'rb') as f:
        loaded_object = p.load(f)
        return loaded_object


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


def process_project(project):

    bug_id = '1'
    
    json_file = open(f'data/muBERT/bug_dataset_{project}_{bug_id}.jsonl', 'wt')

    os.makedirs(project, exist_ok=True)
    os.system(f'defects4j checkout -p {project} -v {bug_id}f -w ./{project}')
    os.system(f'chmod -R 777 {project}')

    df = load_zipped_pickle(f'20230102-mberta-mutants/{project}_{bug_id}.pickle')

    print('processing project = {0}, bug_id = {1}'.format(project, bug_id))

    total_mutants = {}

    counter = 0
    for index, row in df.iterrows():
        file_path = row['file_path']
        method_sig = row['method_signature']

        total_mutants.setdefault(file_path + method_sig, 0)

        with open(f'./{project}/' + file_path, 'r') as f:
            original_code = f.read()
        
        code_lines = original_code.split('\n')
        intervals = parse_java_func_intervals(original_code)
        
        for interval in intervals:
            if interval[0] <= row['line'] <= interval[1] and total_mutants[file_path + method_sig] <= 3:
                start_line = interval[0]
                end_line = interval[1]
                func = '\n'.join(code_lines[start_line-1:end_line])
                buggy_func = func.replace(row['old_val'], row['pred_token'])
                json_file.write(json.dumps({"project": project, "bug_id": bug_id, "class_name": row['class_name'], "file_path": file_path, 'method_signature': method_sig, "func": func, "target": 0, "idx": counter}) + '\n')
                json_file.write(json.dumps({"project": project, "bug_id": bug_id, "class_name": row['class_name'], "file_path": file_path, 'method_signature': method_sig, "func": buggy_func, "target": 1, "idx": counter + 1}) + '\n')
                json_file.flush()
                counter += 2
                total_mutants[file_path + method_sig] += 1
                break

    os.system(f'rm -r ./{project}')


def main():
    os.makedirs('data/muBERT', exist_ok=True)

    projects = ['Chart', 'Cli', 'Codec', 'Collections', 'Compress', 'Csv', 'Gson', 'JacksonCore', 'JacksonDatabind', 'JacksonXml', 'Jsoup', 'JxPath', 'Lang', 'Math', 'Time']

    pool = multiprocessing.Pool(8)

    for i, _ in enumerate(pool.imap_unordered(process_project, projects), 1):
        sys.stderr.write('\rpercentage of projects completed: {0:%}'.format(i/len(projects)))
        

if __name__ == '__main__':
    main()
