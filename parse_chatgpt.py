import ast
import javalang
import json
import argparse
import os
from tqdm import tqdm
from utils import tokenize


def is_equal(method1, method2):
    method1 = method1.split('\n')
    method2 = method2.split('\n')

    method1_stmts = []
    for i in range(len(method1)):
        if method1[i].strip().startswith('//'):
            continue
        if method1[i].strip().startswith('/*'):
            continue
        method1_stmts.append(method1[i].strip())
    
    method2_stmts = []
    for i in range(len(method2)):
        if method2[i].strip().startswith('//'):
            continue
        if method2[i].strip().startswith('/*'):
            continue
        method2_stmts.append(method2[i].strip())

    for i in range(len(method1_stmts)):
        if method1_stmts[i] != method2_stmts[i]:
            return False
    
    return True


def remove_stmt_ids(method):
    if not method.strip().startswith('0-'):
        return method
    
    method = method.split('\n')
    new_method = []
    counter = 0
    for i in range(len(method)):
        if method[i].strip() == '':
            continue

        if method[i].strip().startswith(f'{counter}- '):
            new_method.append(method[i].strip()[len(f'{counter}- '):])
            counter += 1

    return '\n'.join(new_method)


def main(args):
    project = args.project_name
    model_type = args.model_type
    model_size = args.model_size

    filename = f'data/{project}/unique_methods_{model_type}-{model_size}_chatgpt.jsonl'

    json_file = open(f'data/{project}/unique_methods_{model_type}-{model_size}_Nbugs.jsonl', 'w')

    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    total_time = 0
    total_unsuccessful = 0
    total_unchanged = 0
    total_non_parseable = 0

    for line in tqdm(lines):

        dct = ast.literal_eval(line)

        total_time += dct['duration']
        index = dct['index']
        response = dct['chatgpt_response']
        method = dct['method']

        if '<start1>' not in response and '<end1>' not in response or '</start1>' in response and '</end1>' in response:
            
            if '```' in response:
                response = response[:response.find('```')] + '<start1>' + response[response.find('```')+3:response.find('```', response.find('```')+3)] + '<end1>' + response[response.find('```', response.find('```')+3)+3:]
            elif '</start1>' in response:
                response = response[:response.find('<start1>')] + '<start1>' + response[response.find('<start1>')+len('<start1>'):response.find('</start1>')] + '<end1>' + response[response.find('</start1>')+len('</start1>'):]
            else:
                total_unsuccessful += 1
                continue

        if '<start2>' not in response and '<end2>' not in response or '</start2>' in response and '</end2>' in response:
            
            if '```' in response:
                response = response[:response.find('```')] + '<start2>' + response[response.find('```')+3:response.find('```', response.find('```')+3)] + '<end2>' + response[response.find('```', response.find('```')+3)+3:]
            elif '</start2>' in response:
                response = response[:response.find('<start2>')] + '<start2>' + response[response.find('<start2>')+len('<start2>'):response.find('</start2>')] + '<end2>' + response[response.find('</start2>')+len('</start2>'):]
            else:
                total_unsuccessful += 1
                continue

        if '<start3>' not in response and '<end3>' not in response or '</start3>' in response and '</end3>' in response:
                
            if '```' in response:
                response = response[:response.find('```')] + '<start3>' + response[response.find('```')+3:response.find('```', response.find('```')+3)] + '<end3>' + response[response.find('```', response.find('```')+3)+3:]
            elif '</start3>' in response:
                response = response[:response.find('<start3>')] + '<start3>' + response[response.find('<start3>')+len('<start3>'):response.find('</start3>')] + '<end3>' + response[response.find('</start3>')+len('</start3>'):]
            else:
                total_unsuccessful += 1
                continue

        buggy_method1 = response[response.find("<start1>")+len("<start1>"):response.find("<end1>")]

        buggy_method2 = response[response.find("<start2>")+len("<start2>"):response.find("<end2>")]

        buggy_method3 = response[response.find("<start3>")+len("<start3>"):response.find("<end3>")]

        buggy_method1 = remove_stmt_ids(buggy_method1)
        buggy_method2 = remove_stmt_ids(buggy_method2)
        buggy_method3 = remove_stmt_ids(buggy_method3)

        if is_equal(buggy_method1, method):
            total_unchanged += 1
            continue

        if is_equal(buggy_method2, method):
            total_unchanged += 1
            continue
        
        if is_equal(buggy_method3, method):
            total_unchanged += 1
            continue

        try:
            javalang.parse.parse('class Dummy {' + buggy_method1 + '}')
        except:
            total_non_parseable += 1
            continue
        
        try:
            javalang.parse.parse('class Dummy {' + buggy_method2 + '}')
        except:
            total_non_parseable += 1
            continue

        try:
            javalang.parse.parse('class Dummy {' + buggy_method3 + '}')
        except:
            total_non_parseable += 1
            continue

        for i, method_text in enumerate([buggy_method1, buggy_method2, buggy_method3]):
            with open(f'{index}.java', mode='w', encoding="ISO-8859-1", errors='ignore') as fw:
                fw.write(method_text)

            os.system(f'tokenizer {index}.java > {index}.txt')
            tokens = tokenize(f'{index}.txt')

            dct['buggy_method_' + str(i) + '_tokens'] = tokens

            os.system(f'rm {index}.java')
            os.system(f'rm {index}.txt')

        # save generated methods which are sound and correct
        dct['buggy_method1'] = buggy_method1
        dct['buggy_method2'] = buggy_method2
        dct['buggy_method3'] = buggy_method3

        json_file.write(json.dumps(dct) + '\n')
        json_file.flush()


    print('project_name', project)
    print('total_time', total_time)
    print('total_unsuccessful', total_unsuccessful)
    print('total_unchanged', total_unchanged)
    print('total_non_parseable', total_non_parseable)


def parse_args():
    parser = argparse.ArgumentParser("extract chatgpt responses")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to process and extract methods')
    parser.add_argument('--model_type', type=str, default='codebert', help='LLM to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='model size to use in this experiment')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
