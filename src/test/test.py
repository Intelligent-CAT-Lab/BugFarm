import ast
import os
import argparse


def main(args):
    global test_results

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_name}_selected_bugs.jsonl') as f:
        lines = f.readlines()

    test_results = open(f'data/{args.project_name}/test_results_{args.model_name}.txt', 'a')

    os.makedirs(f'test_results/{args.project_name}', exist_ok=True)

    for l in lines:

        dct = ast.literal_eval(l)

        index = dct['index']

        if dct['selected_bugs'] == []:
            continue

        for bug_id in dct['selected_bugs']:
            project = dct['project']

            os.makedirs(f'temp_project', exist_ok=True)

            if os.path.exists(f'test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}.build.log'):
                continue

            if not os.path.exists(f'temp_project/{project}'):
                os.system(f'cp -r projects/{project} temp_project/{project}')

            buggy_method = dct[f'buggy_method{bug_id}']

            file_path = dct['file_path']
            start_line = int(dct['start_line'])
            end_line = int(dct['end_line'])

            relative_path = file_path.split(f'{project}/')[1]

            file_lines = []
            with open(f'temp_project/{project}/{relative_path}', 'r') as f:
                file_lines = f.readlines()
            
            file_lines[start_line-1:end_line] = buggy_method

            with open(f'temp_project/{project}/{relative_path}', 'w') as f:
                f.writelines(file_lines)

            os.chdir(f'temp_project/{project}')
            if project in ['commons-lang', 'joda-time']:
                os.system(f'timeout 3600 JAVA_HOME=`/usr/libexec/java_home -v 1.8` mvn test -Drat.skip=true | grep ERROR > ../../test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}.build.log')
            else:
                os.system(f'timeout 3600 mvn test -Drat.skip=true | grep ERROR > ../../test_results/{project}/{project}.{index}.{bug_id}.{args.model_name}.build.log')

            os.chdir('../../')

            file_lines = []
            with open(file_path, 'r') as f:
                file_lines = f.readlines()
            
            with open(f'temp_project/{project}/{relative_path}', 'w') as f:
                f.writelines(file_lines)

    os.system(f'rm -rf temp_project')


def parse_args():
    parser = argparse.ArgumentParser("test buggy methods on projects")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to test buggy methods on')
    parser.add_argument('--model_name', type=str, default='codebert-base', help='model name to test buggy methods on')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
