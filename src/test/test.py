import ast
import os
import argparse
import logging
import time
from tqdm import tqdm


def main(args):

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_name}-{args.model_size}_selected_bugs.jsonl') as f:
        lines = f.readlines()

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/testing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'testing project={args.project_name} model={args.model_name} size={args.model_size}')

    start_time = time.time()

    project = args.project_name

    os.makedirs(f'test_results/{project}', exist_ok=True)
    os.makedirs(f'temp_project_{project}', exist_ok=True)
    os.system(f'cp -r projects/{project} temp_project_{project}/')

    for l in tqdm(lines):

        dct = ast.literal_eval(l)

        index = dct['index']

        if dct['selected_bugs'] == []:
            continue
        
        # read original file
        file_path = dct['file_path']
        relative_path = '/'.join(file_path.split('/')[1:])
        file_lines = []
        with open(f'temp_project_{project}/{relative_path}', 'r', encoding="ISO-8859-1", errors='ignore') as f:
            file_lines = f.readlines()

        for bug_id in dct['selected_bugs']:
            project = dct['project']

            if os.path.exists(f'test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log'):
                continue

            buggy_method = dct[f'buggy_method{bug_id}']


            file_path = dct['file_path']
            
            file_path = dct['file_path']
            start_line = int(dct['start_line'])
            end_line = int(dct['end_line'])

            buggy_file_lines = file_lines.copy()
            buggy_file_lines[start_line-1:end_line] = buggy_method

            with open(f'temp_project_{project}/{relative_path}', 'w') as f:
                f.writelines(buggy_file_lines)

            os.chdir(f'temp_project_{project}/{project}')
            if project in ['commons-lang', 'joda-time']:
                os.system(f'JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/jre" timeout 300 mvn test -Drat.skip=true -Dmaven.compiler.useIncrementalCompilation=false 2> /dev/null | grep ERROR > ../../test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log')
            else:
                os.system(f'timeout 300 mvn test -Drat.skip=true -Dmaven.compiler.useIncrementalCompilation=false 2> /dev/null | grep ERROR > ../../test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log')

            os.chdir('../../')

            with open(f'temp_project_{project}/{relative_path}', 'w') as f:
                f.writelines(file_lines)

    end_time = time.time()
    time_minutes = round((end_time-start_time)/60,2)
    logging.info(f'testing project={args.project_name} model={args.model_name} size={args.model_size} time={round(end_time-start_time,2)} seconds ({time_minutes} minutes)')

    os.system(f'rm -rf temp_project_{project}')


def parse_args():
    parser = argparse.ArgumentParser("test buggy methods on projects")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to test buggy methods on')
    parser.add_argument('--model_name', type=str, default='codebert', help='model name to test buggy methods on')
    parser.add_argument('--model_size', type=str, default='base', help='model size to test buggy methods on')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
