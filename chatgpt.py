import json
import ast
import time
from tqdm import tqdm
from revChatGPT.V1 import Chatbot

config = {}
with open('configs/chatgpt_configs.json', 'r') as f:
    config = json.load(f)

chatbot = Chatbot(config=config)

project = 'commons-cli'
model_type = 'codebert'
model_size = 'base'

lines = []
with open(f'data/{project}/unique_methods_{model_type}-{model_size}_las_lat.jsonl', 'r') as f:
    lines = f.readlines()

json_file = open(f'data/{project}/unique_methods_{model_type}-{model_size}_chatgpt.jsonl', 'a')

# calculate number of lines in json_file
num_lines = 0
with open(f'data/{project}/unique_methods_{model_type}-{model_size}_chatgpt.jsonl', 'r') as f:
    num_lines = len(f.readlines())

lines = lines[num_lines:]

for l in tqdm(lines):
    
    start_time = time.time()

    dct = ast.literal_eval(l)

    method = dct['method'].strip().split('\n')

    least_attended_statement_indices = dct['least_attended_statements']

    index_code = []
    counter = 0
    for i in range(len(method)):
        stripped_statement = method[i].strip()
        if stripped_statement == '':
            continue
        index_code.append(f'{counter}- {method[i].strip()}')
        counter += 1

    change_statements = []
    for i in least_attended_statement_indices:
        change_statements.append("\"" + index_code[i] + "\"")

    change_statements_str = ''
    if len(change_statements) > 1:
        change_statements_str = 'statements ' + ' and '.join(change_statements)
    else:
        change_statements_str = 'statement ' + ' and '.join(change_statements)

    prompt =  """Observe the following java method where each statement has a specific ID starting from 0. Can you produce 3 different buggy versions of this method by changing {} only? Do not change other statements in the given java code.\n\nYou have to write each buggy method again. Do not write anything else in your response. Make sure your generated buggy java code is compilable and does not have syntax errors and compile-time errors. Do not use a variable which does not exist in the scope of the given method. You should put <start1> <start2> <start3> and <end1> <end2> <end3> in the beginning and end of each buggy method so I could parse your response later.\n\n{}""".format(change_statements_str, '\n'.join(index_code))

    response = ""
    for data in chatbot.ask(prompt):
        response = data["message"]

    dct['chatgpt_response'] = response
    dct['duration'] = time.time() - start_time

    json_file.write(json.dumps(dct) + '\n')
    json_file.flush()
