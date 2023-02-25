import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
import ast
import json
import os
import math
from utils import visual_matrix, analyze_least_attended_tokens
import sys
import argparse
import time
import logging
from json import JSONEncoder


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def main(args):

    start = time.time()

    global table_rows
    global project_least_attended_tokens
    global json_file

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'visualizing {args.project_name} using {args.model_type}-{args.model_size}')

    os.system(f'mkdir -p visualizations/{args.model_type}_{args.model_size}_{args.project_name}_attention_analysis/img')

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_attnw.jsonl') as fr:
        lines = fr.readlines()

    json_file = open(f"data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_las_lat.jsonl", "wt")

    table_rows = open('table_rows.txt', 'w')
    project_least_attended_tokens = open('least_attended_tokens.txt', 'w')
    pool = multiprocessing.Pool(args.num_workers)
    for i, _ in enumerate(pool.imap_unordered(process_instance, lines), 1):
        sys.stderr.write('\rpercentage of methods visualized: {0:%}'.format(i/len(lines)))

    with open('table_rows.txt') as fr:
        content = fr.read()

    table = f'<html>\n\t<head>\n\t\t<style type="text/css" media="screen">\n\t\t\ttable, th, td {{border: 1px solid black;}}\n\t\t\ttd, th {{word-wrap: break-word}}\n\t\t</style>\n\t</head>\n\t<body>\n\t\t<table>\n\t\t\t<tr>\n\t\t\t\t<th>Index</th>\n\t\t\t\t<th>Statements <br> (red = among least 10% of attended tokens) <br> (blue = among least 10% of attended statements) </th>\n\t\t\t\t<th>Attention Matrix (averaged over all layers and heads)</th>\n\t\t\t\t<th>Statement (unattended / all tokens)</th>\n\t\t\t</tr>{content}\n\t\t</table>\n\t</body>\n</html>'
    with open(f'visualizations/{args.model_type}_{args.model_size}_{args.project_name}_attention_analysis/{args.project_name}_{args.model_type}.html', 'w') as fw:
        fw.write(table)
    
    with open('least_attended_tokens.txt') as fr:
        project_least_attended_tokens = fr.readlines()
    
    res = [ast.literal_eval(x) for x in project_least_attended_tokens]
    cat_freq = analyze_least_attended_tokens(res)
    with open(f'visualizations/{args.model_type}_{args.model_size}_{args.project_name}_attention_analysis/freqs.json', 'w') as fp:
        json.dump(cat_freq, fp)

    os.remove('table_rows.txt')
    os.remove('least_attended_tokens.txt')

    logging.info(f'total time in secs for visualizing {args.project_name} using {args.model_type}: ' + str(round(time.time() - start, 2)))


def process_instance(input):
    dct = ast.literal_eval(input)
    model_attentions = dct['model_attentions']
    decoded_token_types = dct['tokens']
    decoded_tokens = [x for x,y in decoded_token_types]

    plt.figure(figsize=(7,7))
    ax = visual_matrix(model_attentions, decoded_tokens)
    plt.savefig('visualizations/{}_{}_{}_attention_analysis/img/{}_mat.png'.format(args.model_type, args.model_size, args.project_name, dct['index']), bbox_inches='tight')
    plt.close()

    col_averaged = np.average(model_attentions, axis=0)

    k = args.threshold
    token_attn = list(zip(decoded_token_types, col_averaged))
    token_attn.sort(key = lambda i:i[1])

    least_attended_tokens = token_attn[:math.ceil((k/100) * len(token_attn))]
    for item in least_attended_tokens:
        project_least_attended_tokens.write(str(item) + '\n')
        project_least_attended_tokens.flush()

    counter = 0
    record = {}
    statement = ''
    score = []
    for i in range(len(decoded_tokens)):
        if decoded_tokens[i].strip() in ['<s>', '</s>']: continue

        if decoded_tokens[i] == '\n':
            record[counter] = [statement, np.sum(score), len(score)]
            counter += 1
            statement, score = '', []
            continue

        statement += decoded_tokens[i] + ' '

        if decoded_tokens[i] in list(zip(*list(zip(*least_attended_tokens))[0]))[0]:
            score.append(1)
        else:
            score.append(0)
    
    record[counter] = [statement, np.sum(score), len(score)]

    unnormalized_lengths = []
    for i in sorted(record):
        unnormalized_lengths.append(record[i][2])
    
    unnormalized_lengths = np.array(unnormalized_lengths) / np.linalg.norm(unnormalized_lengths)
    for i in sorted(record):
        record[i].append(unnormalized_lengths[i])
        record[i].append(record[i][1] / record[i][3])

    attended_statements = sorted(record.items(), key=lambda item: item[1][4])

    res = []
    for pair in attended_statements:
        if pair[0] == 0:
            res.append(pair)
        elif pair[1][0].strip().startswith('//'):
            res.append(pair)
        else:
            res.insert(0, pair)

    least_attended_statements = res[:math.ceil((k/100) * len(res))]

    labels = []
    unattended_tokens = []
    all_tokens = []
    scores = []
    for k in sorted(record):
        labels.append(record[k][0])
        unattended_tokens.append(record[k][1])
        all_tokens.append(record[k][2])
        scores.append(record[k][4])

    c = 0
    token_str = f'{c}- '
    is_set = False
    for i in range(len(decoded_tokens)):
        if c in list(zip(*least_attended_statements))[0] and not is_set:
            token_str += '<a style="color:blue">[least attended statement] </a>'
            is_set = True

        if decoded_tokens[i] == '\n':
            c += 1
            token_str += f' <br>{c}- '
            is_set = False
            continue

        elif decoded_tokens[i] in list(zip(*list(zip(*least_attended_tokens))[0]))[0]:
            token_str += f'<a style="color:red">{decoded_tokens[i]} </a>'

        else:
            token_str += f'{decoded_tokens[i]} '

    fig, ax = plt.subplots()
    ax2 = plt.twiny()
    y_pos = np.arange(len(labels))

    ax.barh(y_pos, unattended_tokens, align='edge', color='blue', height=0.4, label='unattended tokens')
    ax.barh(y_pos, all_tokens, align='edge', color='red', height=-0.4, label='all tokens')
    ax2.barh(y_pos, scores, align='center', height=0.27, color='green', label='ratio')
    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    ax.set_xlabel('# tokens')
    ax2.set_xlabel('ratio (unattended / normalized_length)')
    ax2.grid(False)
    ax2.legend(loc=3)
    ax.legend(loc=4)
    plt.savefig('visualizations/{}_{}_{}_attention_analysis/img/{}.png'.format(args.model_type, args.model_size, args.project_name, dct['index']), bbox_inches='tight')
    plt.close()

    img_src = 'img/{}.png'.format(dct['index'])
    atn_mat_img_src = 'img/{}_mat.png'.format(dct['index'])
    index = dct['index']
    table_rows.write(f'\n\t\t\t\t<tr>\n\t\t\t\t\t<td>{index}</td>\n\t\t\t\t\t<td>{token_str}</td>\n\t\t\t\t\t<td><img src={atn_mat_img_src}></td>\n\t\t\t\t\t<td><img src={img_src}></td>\n\t\t\t\t</tr>')

    dct['least_attended_tokens'] = [x[0][0] for x in least_attended_tokens]
    dct['least_attended_statements'] = [x[0] for x in least_attended_statements]

    json_file.write(json.dumps(dct, cls=NumpyArrayEncoder) + '\n')
    json_file.flush()


def parse_args():
    parser = argparse.ArgumentParser("visualize attention weights of a given java project and locate least attended statements")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to visualize its attentions')
    parser.add_argument('--model_type', type=str, default='codebert', help='model to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='model size to use in this experiment')
    parser.add_argument('--log_file', type=str, default='visualize_attention.log', help='log file name')
    parser.add_argument('--threshold', type=int, default=10, help='threshold for least attended tokens and statements')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
