import json
import argparse
import ast
import subprocess
import glob


def main(args):

    if args.type == 'closure-mockito':

        json_file = open(f'data/defect/real/test.jsonl', 'wt')

        counter = 0
        instances = []
        for project in ['Closure', 'Mockito']:
            files = subprocess.Popen(["ls"] + glob.glob(f'data/defect/{project}/**/*.txt', recursive=True), stdout=subprocess.PIPE)
            source_paths = [x.decode('ascii').strip() for x in files.stdout.readlines()]

            for source_path in source_paths:
                bug_id = source_path.split('/')[-2].strip()

                with open(source_path, 'r') as f:
                    func = f.read()
                    func = ' '.join(func.split())
                
                if 'fixed' in source_path:
                    instances.append((func, 0))
                else:
                    instances.append((func, 1))
                json_file.flush()
        
        distinct_instances = set(instances)
        for instance in distinct_instances:
            json_file.write(json.dumps({"func": f"{instance[0]}", "target": instance[1], "idx": counter}) + '\n')
            counter += 1

    else:

        projects = ["commons-cli", "commons-codec", "commons-collections", "commons-compress", "commons-csv", "commons-jxpath", "commons-lang", "commons-math", "gson", "jackson-core", "jackson-databind", "jackson-dataformat-xml", "jfreechart", "joda-time", "jsoup"]

        json_file = open(f'data/defect/ours-codebert/{args.model}.jsonl', 'wt')

        counter = 0
        for project in projects:

            with open(f'data/{project}/unique_methods_{args.model}_selected_bugs.jsonl', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    dct = ast.literal_eval(line)
                    func = dct['method']
                    func = ' '.join(func.split())
                    dct['method'] = func
                    json_file.write(json.dumps({"func": f"{dct['method']}", "target": 0, "idx": counter}) + '\n')
                    counter += 1

                    if 'selected_bugs' not in dct:
                        continue

                    for bug_id in dct['selected_bugs']:
                        func = dct[f'buggy_method{bug_id}']
                        func = ' '.join(func.split())
                        dct[f'buggy_method{bug_id}'] = func
                        json_file.write(json.dumps({"func": f"{dct[f'buggy_method{bug_id}']}", "target": 1, "idx": counter}) + '\n')
                        counter += 1

                    json_file.flush()


def parse_args():
    parser = argparse.ArgumentParser("extract chatgpt responses")
    parser.add_argument('--type', type=str, default='test', help='test or train')
    parser.add_argument('--subtype', type=str, default='mubert', help='test or train')
    parser.add_argument('--size', type=str, default='medium', help='small, medium')
    parser.add_argument('--model', type=str, default='codebert-base', help='base')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
