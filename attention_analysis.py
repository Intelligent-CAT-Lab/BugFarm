from transformers import AutoTokenizer, AutoModel
import torch
from utils import visual_atn_matrix, adjust_tokens, visual_matrix, analyze_least_attended_tokens
import matplotlib.pyplot as plt
import numpy as np
import math
import json
import ast
import argparse
import os


def main(args):
    # Init
    model_type = args.model_type
    tokenizer = AutoTokenizer.from_pretrained(f"microsoft/{model_type}-base")
    model = AutoModel.from_pretrained(f"microsoft/{model_type}-base")

    os.system(f'mkdir -p {model_type}_attention_analysis/img')

    project = args.project_name
    lines = []
    with open(f'data/{project}/{project}.jsonl') as fr:
        lines = fr.readlines()
    
    project_least_attended_tokens = []
    excluded = 0
    table_rows = ''
    for l in lines:
        dct = ast.literal_eval(l)

        # Tokenization 
        nl_tokens = tokenizer.tokenize("")

        method = dct['method']
        statements = method.split('\n')
        statements = [x.strip() for x in statements if x.strip() != '']
        code = '\n'.join(statements)

        code_tokens = tokenizer.tokenize(code)

        if len(code_tokens) > 509:
            excluded += 1
            continue

        tokens = [tokenizer.cls_token]+nl_tokens+[tokenizer.sep_token]+code_tokens+[tokenizer.eos_token]

        # Convert tokens to ids
        tokens_ids = tokenizer.convert_tokens_to_ids(tokens)
        decoded_tokens = [tokenizer.decode(id_) for id_ in tokens_ids]

        # Extract the attentions
        attentions = model(torch.tensor(tokens_ids)[None,:], output_attentions=True)['attentions']

        # Post-process attentions
        zeros = np.zeros((len(decoded_tokens), len(decoded_tokens)))
        for i in range(12):
            zeros += visual_atn_matrix(decoded_tokens, attentions, layer_num=i, head_num='average')

        averaged_attentions = zeros / 12

        averaged_attentions, decoded_tokens_types = adjust_tokens(decoded_tokens, dct['tokens'], averaged_attentions)

        decoded_tokens = [x for x,y in decoded_tokens_types]

        plt.figure(figsize=(7,7))
        ax = visual_matrix(averaged_attentions, decoded_tokens)
        plt.savefig('{}_attention_analysis/img/{}_{}_mat.png'.format(model_type, dct['index'], dct['bug_id']), bbox_inches='tight')

        col_averaged = np.average(averaged_attentions, axis=0)

        k = 10
        token_attn = list(zip(decoded_tokens_types, col_averaged))
        token_attn.sort(key = lambda i:i[1])

        least_attended_tokens = token_attn[:math.ceil((k/100) * len(token_attn))]
        project_least_attended_tokens += least_attended_tokens

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

        attended_statements = sorted(record.items(), key=lambda item: item[1][4], reverse=True)

        least_attended_statements = attended_statements[:math.ceil((k/100) * len(attended_statements))]

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
        plt.savefig('{}_attention_analysis/img/{}_{}.png'.format(model_type, dct['index'], dct['bug_id']), bbox_inches='tight')

        img_src = 'img/{}_{}.png'.format(dct['index'], dct['bug_id'])
        atn_mat_img_src = 'img/{}_{}_mat.png'.format(dct['index'], dct['bug_id'])
        index = dct['bug_id'] + '.' + dct['index']
        table_rows += f'\n\t\t\t\t<tr>\n\t\t\t\t\t<td>{index}</td>\n\t\t\t\t\t<td>{token_str}</td>\n\t\t\t\t\t<td><img src={atn_mat_img_src}></td>\n\t\t\t\t\t<td><img src={img_src}></td>\n\t\t\t\t</tr>'
        if index == '1.2': break

    table = f'<html>\n\t<head>\n\t\t<style type="text/css" media="screen">\n\t\t\ttable, th, td {{border: 1px solid black;}}\n\t\t\ttd, th {{word-wrap: break-word}}\n\t\t</style>\n\t</head>\n\t<body>\n\t\t<table>\n\t\t\t<tr>\n\t\t\t\t<th>Index</th>\n\t\t\t\t<th>Statements <br> (red = among least 10% of attended tokens) <br> (blue = among least 10% of attended statements) </th>\n\t\t\t\t<th>Attention Matrix (averaged over all layers and heads)</th>\n\t\t\t\t<th>Statement (unattended / all tokens)</th>\n\t\t\t</tr>{table_rows}\n\t\t</table>\n\t</body>\n</html>'
    with open(f'{model_type}_attention_analysis/{project}_{model_type}.html', 'w') as fw:
        fw.write(table)

    cat_freq = analyze_least_attended_tokens(project_least_attended_tokens)
    with open(f'{model_type}_attention_analysis/freqs_{model_type}.json', 'w') as fp:
        json.dump(cat_freq, fp)

    print('exclusion (length > 512) rate: ', round((excluded / len(lines) * 100), 2))
    print('total methods: ', len(lines))


def parse_args():
    parser = argparse.ArgumentParser("visualize attention weights of a given java project and locate least attended statements")
    parser.add_argument('--project_name', type=str, default='JacksonXml', help='defects4j project name to process and extract methods')
    parser.add_argument('--model_type', type=str, default='codebert', help='model to use in this experiment')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
