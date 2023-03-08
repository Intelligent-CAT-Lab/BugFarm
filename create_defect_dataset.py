import json
import argparse
import ast


def main(args):

    if args.type == 'test':
        json_file = open(f'data/defect/{args.size}/test.jsonl', 'wt')

        counter = 0
        with open(f'data/defect/{args.size}/data_refine_{args.size}_test.buggy-fixed.buggy', 'r') as f:
            lines = f.readlines()
            for line in lines:
                json_file.write(json.dumps({"func": f"{line.strip()}", "targe": 0, "idx": counter}) + '\n')
                json_file.flush()
                counter += 1
        
        with open(f'data/defect/{args.size}/data_refine_{args.size}_test.buggy-fixed.fixed', 'r') as f:
            lines = f.readlines()
            for line in lines:
                json_file.write(json.dumps({"func": f"{line.strip()}", "label": 1, "idx": counter}) + '\n')
                json_file.flush()
                counter += 1
        
        json_file.close()

    elif args.type == 'train':

        if args.subtype == 'ours':

            # projects = ["commons-cli", "commons-codec", "commons-collections", "commons-compress", "commons-csv", "commons-jxpath", "commons-lang", "commons-math", "gson", "jackson-core", "jackson-databind", "jackson-dataformat-xml", "jfreechart", "joda-time", "jsoup"]
            projects = ["commons-cli", "commons-codec", "commons-csv", "commons-jxpath", "gson", "jackson-core", "jackson-dataformat-xml", "jfreechart", "jsoup"]

            json_file = open(f'data/defect/ours/train.jsonl', 'wt')

            counter = 0
            for project in projects:

                with open(f'data/{project}/unique_methods_codebert-base_selected_bugs.jsonl', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        dct = ast.literal_eval(line)
                        json_file.write(json.dumps({"func": f"{dct['method']}", "target": 1, "idx": counter}) + '\n')
                        counter += 1

                        for bug_id in dct['selected_bugs']:
                            json_file.write(json.dumps({"func": f"{dct[f'buggy_method{bug_id}']}", "target": 0, "idx": counter}) + '\n')
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
