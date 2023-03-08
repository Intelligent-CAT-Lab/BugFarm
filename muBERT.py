import json
import javalang
from typing import Set, Tuple
import os
import gzip
from tqdm import tqdm
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


def main():

    os.makedirs('data/muBERT', exist_ok=True)
    json_file = open(f'data/muBERT/bug_dataset.jsonl', 'wt')

    pickle_files = os.listdir('20230102-mberta-mutants')

    for pickle_file in tqdm(pickle_files):

        project = pickle_file.split('.')[0].split('_')[0]
        bug_id = pickle_file.split('.')[0].split('_')[1]

        os.makedirs('./tmp', exist_ok=True)
        os.system(f'defects4j checkout -p {project} -v {bug_id}f -w ./tmp')
        os.system(f'chmod -R 777 tmp')

        df = load_zipped_pickle(f'20230102-mberta-mutants/{pickle_file}')

        print('processing project = {0}, bug_id = {1}'.format(project, bug_id))

        counter = 0
        for index, row in df.iterrows():
            file_path = row['file_path']

            with open('./tmp/' + file_path, 'r') as f:
                original_code = f.read()
            
            code_lines = original_code.split('\n')
            intervals = parse_java_func_intervals(original_code)
            
            for interval in intervals:
                if interval[0] <= row['line'] <= interval[1]:
                    start_line = interval[0]
                    end_line = interval[1]
                    func = '\n'.join(code_lines[start_line-1:end_line])
                    buggy_func = func.replace(row['old_val'], row['pred_token'])
                    json_file.write(json.dumps({"project": project, "bug_id": bug_id, "class_name": row['class_name'], "file_path": row['file_path'], 'method_signature': row['method_signature'], "func": func, "target": 1, "idx": counter}) + '\n')
                    json_file.write(json.dumps({"project": project, "bug_id": bug_id, "class_name": row['class_name'], "file_path": row['file_path'], 'method_signature': row['method_signature'], "func": buggy_func, "target": 0, "idx": counter + 1}) + '\n')
                    json_file.flush()
                    counter += 2
                    break

        os.system('rm -r ./tmp')


if __name__ == '__main__':
    main()
