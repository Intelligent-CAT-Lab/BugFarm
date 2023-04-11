import ast
import os
import argparse
import multiprocessing
import sys
import json


def main(args):
    global success, compile_error, test_error

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_name}_selected_bugs.jsonl') as f:
        lines = f.readlines()

    manager = multiprocessing.Manager()
    success = manager.list()
    compile_error = manager.list()
    test_error = manager.list()

    pool = multiprocessing.Pool(args.num_workers)
    for i, _ in enumerate(pool.imap_unordered(process_instance, lines), 1):
        sys.stderr.write('\rpercentage of source code files completed: {0:%}'.format(i/len(lines)))

    stats = {'success': list(success), 'compile_error': list(compile_error), 'test_error': list(test_error)}

    with open(f'data/{args.project_name}/test_results_{args.model_name}.json', 'w') as f:
        json.dump(stats, f)


def process_instance(l):

    dct = ast.literal_eval(l)

    index = dct['index']

    if dct['selected_bugs'] == []:
        return

    for bug_id in dct['selected_bugs']:
        project = dct['project']
        os.makedirs(f'temp_project_{index}', exist_ok=True)

        os.system(f'cp -r projects/{project} temp_project_{index}/')
                
        buggy_method = dct[f'buggy_method{bug_id}']

        file_path = dct['file_path']
        start_line = int(dct['start_line'])
        end_line = int(dct['end_line'])

        relative_path = file_path.split(f'{project}/')[1]

        file_lines = []
        with open(f'temp_project_{index}/{project}/{relative_path}', 'r') as f:
            file_lines = f.readlines()
        
        file_lines[start_line-1:end_line] = buggy_method

        with open(f'temp_project_{index}/{project}/{relative_path}', 'w') as f:
            f.writelines(file_lines)

        os.chdir(f'temp_project_{index}/{project}')
        if project in ['commons-lang', 'joda-time']:
            os.system(f'JAVA_HOME=`/usr/libexec/java_home -v 1.8` mvn clean compile test -Drat.skip=true --log-file {project}.{index}.{bug_id}.{args.model_name}.build.log')
        else:
            os.system(f'mvn clean compile test -Drat.skip=true --log-file {project}.{index}.{bug_id}.{args.model_name}.build.log')
        
        with open(f'{project}.{index}.{bug_id}.{args.model_name}.build.log', 'r') as f:
            data = f.readlines()

        data = ''.join(data)

        if 'BUILD SUCCESS' in data:
            success.append(f'{index}-{bug_id}')
        elif 'BUILD FAILURE' in data and 'COMPILATION ERROR' in data:
            compile_error.append(f'{index}-{bug_id}')
        elif 'BUILD FAILURE' in data:
            test_error.append(f'{index}-{bug_id}')
        
        os.chdir('../../')
        os.system(f'rm -rf temp_project_{index}/{project}')

    os.rmdir(f'temp_project_{index}')


def parse_args():
    parser = argparse.ArgumentParser("test buggy methods on projects")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to test buggy methods on')
    parser.add_argument('--model_name', type=str, default='codebert-base', help='model name to test buggy methods on')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
