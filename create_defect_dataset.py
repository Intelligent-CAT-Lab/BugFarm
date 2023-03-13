import json
import argparse
import ast


def main(args):

    projects = ["commons-cli", "commons-codec", "commons-collections", "commons-compress", "commons-csv", "commons-jxpath", "commons-lang", "commons-math", "gson", "jackson-core", "jackson-databind", "jackson-dataformat-xml", "jfreechart", "joda-time", "jsoup"]

    json_file = open(f'data/defect/ours/big_train.jsonl', 'wt')

    counter = 0
    for project in projects:

        with open(f'data/{project}/unique_methods_codebert-base_selected_bugs.jsonl', 'r') as f:
            lines = f.readlines()
            for line in lines:
                dct = ast.literal_eval(line)
                json_file.write(json.dumps({"func": f"{dct['method']}", "target": 0, "idx": counter}) + '\n')
                counter += 1

                if 'selected_bugs' not in dct:
                    continue

                for bug_id in dct['selected_bugs']:
                    json_file.write(json.dumps({"func": f"{dct[f'buggy_method{bug_id}']}", "target": 1, "idx": counter}) + '\n')
                    counter += 1

                json_file.flush()


def parse_args():
    parser = argparse.ArgumentParser("extract chatgpt responses")
    parser.add_argument('--type', type=str, default='test', help='test or train')
    parser.add_argument('--subtype', type=str, default='mubert', help='test or train')
    parser.add_argument('--size', type=str, default='medium', help='small, medium')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
