import javalang
import json
import os
from multiprocessing import Pool
import argparse
import sys
from typing import Set, Tuple
from utils import tokenize
import ast


def parse_java_func_intervals(content: str) -> Set[Tuple[int, int]]:
    func_intervals = set()
    for _, node in javalang.parse.parse(content):
        if isinstance(
            node,
            (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration),
        ):
            func_intervals.add(
                (
                    node.start_position.line,
                    node.end_position.line + 1,
                )
            )
    return func_intervals


def get_class_paths(project, bug_id, modified_classes):
    full_path = []
    for class_name in modified_classes:
        java_file_name = class_name.split(".")[-1] + ".java"
        class_fixed_pwd = "./projects/" + project + "/" + bug_id

        os.system("find " + class_fixed_pwd + " -name " + "'" + java_file_name + "'" + " > " + f"{project}{bug_id}{class_name}.txt")

        with open(f"{project}{bug_id}{class_name}.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
            found_paths = f.readlines()
            if len(found_paths) == 0:
                os.system(f"rm {project}{bug_id}{class_name}.txt")
                continue

            substring = class_name.replace('.', '/')
            class_fixed_location = ''
            for path in found_paths:
                if substring in path:
                    class_fixed_location = path
                    break

            class_fixed_location = class_fixed_location.strip()
            class_fixed_location = class_fixed_location.replace("$", "\$")
            full_path.append(class_fixed_location)

        os.system(f"rm {project}{bug_id}{class_name}.txt")
    
    return full_path


def get_bug_ids(project_name):
    command = 'defects4j query -p ' + project_name + f' -q bug.id > {project_name}_bug_ids.txt'
    os.system(command)

    bug_ids = []
    with open(f'{project_name}_bug_ids.txt') as fr:
        for line in fr.readlines():
            bug_ids.append(line.strip())

    os.system(f'rm {project_name}_bug_ids.txt')
    return bug_ids


def get_file_paths(project_name, bug_id):
    modified_classes = []
    with open(f'{project_name}_{bug_id}_relevant_classes.txt') as f:
        modified_classes = f.readlines()
        modified_classes = list(map(lambda x: x.strip(), modified_classes))
        
    os.system(f'rm {project_name}_{bug_id}_relevant_classes.txt')

    return get_class_paths(project_name, bug_id, modified_classes)


def process_bug(bug_id):
    os.system(f'mkdir -p projects/{project}/{bug_id}')
    os.system(f'defects4j checkout -p {project} -v {bug_id}f -w projects/{project}/{bug_id}')
    os.system(f'defects4j export -p classes.relevant -w projects/{project}/{bug_id} > {project}_{bug_id}_relevant_classes.txt')
    os.system(f'chmod -R 777 projects/{project}/{bug_id}')

    file_paths = get_file_paths(project, bug_id)

    index = 0
    for target_file in file_paths:

        if not os.path.exists(target_file): continue

        with open(target_file, mode='r', encoding="ISO-8859-1", errors='ignore') as r:
            codelines = r.readlines()
            code_text = ''.join(codelines)

        intervals = parse_java_func_intervals(code_text)

        for start, end in intervals:
            method_text =  ''.join(codelines[start-1:end])

            if method_text.strip() == "": continue

            with open(f'{project}.{bug_id}.{index}.java', mode='w', encoding="ISO-8859-1", errors='ignore') as fw:
                fw.write(method_text)

            os.system(f'tokenizer {project}.{bug_id}.{index}.java > {project}.{bug_id}.{index}.txt')
            tokens = tokenize(f'{project}.{bug_id}.{index}.txt')

            dataset = {}
            dataset['index'] = str(index)
            dataset['project'] = project
            dataset['bug_id'] = bug_id
            dataset['file_path'] = target_file
            dataset['start_line'] = str(start)
            dataset['end_line'] = str(end)
            dataset['method'] = method_text
            dataset['tokens'] = tokens

            json_file.write(json.dumps(dataset) + '\n')
            json_file.flush()
            
            os.remove(f'{project}.{bug_id}.{index}.txt')
            os.remove(f'{project}.{bug_id}.{index}.java')

            index += 1

    os.system(f'rm -r projects/{project}/{bug_id}')


def main(args):
    global project
    global json_file
    project = args.project_name

    os.system(f'mkdir -p data/{project}')
    json_file = open(f"data/{project}/methods.jsonl", "wt")

    # export project bug ids
    bug_ids = get_bug_ids(project)

    # multiprocessing for faster processing
    pool = Pool(os.cpu_count())
    for i, _ in enumerate(pool.imap_unordered(process_bug, bug_ids), 1):
        sys.stderr.write('\rpercentage of files completed: {0:%}'.format(i/len(bug_ids)))
    
    # handle duplicates
    lines = []
    with open(f'data/{project}/methods.jsonl') as fr:
        lines = fr.readlines()

    json_file = open(f"data/{project}/methods.jsonl", "wt")
    unique_methods = []
    unique_method_tokens = []

    for l in lines:
        dct = ast.literal_eval(l)

        if dct['method'].strip() not in unique_methods:
            unique_methods.append(dct['method'].strip())
            unique_method_tokens.append(dct['tokens'])
        
        dct['foreign_key'] = str(unique_methods.index(dct['method'].strip()))

        json_file.write(json.dumps(dct) + '\n')
        json_file.flush()

    assert len(unique_methods) == len(unique_method_tokens)

    with open(f'data/{project}/unique_methods.jsonl', 'w') as fw:
        for i in range(len(unique_methods)):
            fw.write(json.dumps({'index': str(i), 'method': unique_methods[i], 'tokens': unique_method_tokens[i]}) + '\n')
            fw.flush()


def parse_args():
    parser = argparse.ArgumentParser("extract methods of a given java project")
    parser.add_argument('--project_name', type=str, default='JacksonXml', help='defects4j project name to process and extract methods')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
