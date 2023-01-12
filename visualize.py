from transformers import AutoTokenizer, AutoModel
import torch
from utils import visual_atn_matrix, adjust_tokens, visual_matrix
import matplotlib.pyplot as plt
import numpy as np
import math
import ast


# Init
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

project = 'JacksonXml'
lines = []
with open(f'data/{project}/{project}.jsonl') as fr:
    lines = fr.readlines()

excluded = 0
index = 0
for z in range(len(lines)):
    dct = ast.literal_eval(lines[z])

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

    averaged_attentions, decoded_tokens = adjust_tokens(decoded_tokens, dct['tokens'], averaged_attentions)

    plt.figure(figsize=(12,7))
    ax = visual_matrix(averaged_attentions, decoded_tokens)
    plt.savefig('img/{}_{}_mat.png'.format(dct['index'], dct['bug_id']), bbox_inches='tight')

    col_averaged = np.average(averaged_attentions, axis=0)

    counter = 0
    record = {}
    statement = ''
    score = []
    statements = []
    for i in range(len(decoded_tokens)):
        if decoded_tokens[i].strip() in ['<s>', '</s>']: continue

        if decoded_tokens[i] == '\n':
            record[counter] = (statement, np.mean(score))
            statements.append(statement)
            counter += 1
            statement, score = '', []
            continue

        statement += decoded_tokens[i] + ' '
        score.append(col_averaged[i])
    
    record[counter] = (statement, np.mean(score))
    statements.append(statement)

    labels = []
    scores = []
    for k in sorted(record):
        labels.append(record[k][0])
        scores.append(record[k][1])

    k = 10
    # least_attended_tokens = get_least_attended_tokens(averaged_attentions, decoded_tokens, k)
    # least_attended_statements = get_least_attended_statements(tokenizer, statements, least_attended_tokens, k)

    token_attn = list(zip(decoded_tokens, col_averaged))
    token_attn.sort(key = lambda i:i[1])

    least_attended_tokens = token_attn[:math.ceil((k/100) * len(token_attn))]

    c = 0
    token_str = f'{c}- '
    for i in range(len(decoded_tokens)):
        if decoded_tokens[i] == '\n':
            c += 1
            token_str += f' <br>{c}- '
            continue
        elif decoded_tokens[i] in list(zip(*least_attended_tokens))[0]:
            token_str += f'<a style="color:red">{decoded_tokens[i]} </a>'
        else:
            token_str += f'{decoded_tokens[i]} '

    fig, ax = plt.subplots()
    y_pos = np.arange(len(labels))

    ax.barh(y_pos, scores, align='center')
    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    ax.set_xlabel('Average Attention of Tokens')
    plt.savefig('img/{}_{}.png'.format(dct['index'], dct['bug_id']), bbox_inches='tight')

    img_src = 'img/{}_{}.png'.format(dct['index'], dct['bug_id'])
    atn_mat_img_src = 'img/{}_{}_mat.png'.format(dct['index'], dct['bug_id'])
    index += 1
    print(f'<tr>\n\t<td>{index}</td>\n\t<td>{token_str}</td>\n\t<td><img src={atn_mat_img_src}></td>\n\t<td><img src={img_src}></td>\n</tr>')
   
print('exclusion (length > 512) rate: ', round((excluded / len(lines) * 100), 2))
print('total methods: ', len(lines))
