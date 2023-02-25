import ast
import numpy as np
import seaborn as sns
from ansi.colour import rgb


def color_text(text, rgb_code):
    reset =  '\x1b[0m'
    return rgb.rgb256(*rgb_code) + text + reset

def value2rgb(value):
#     if value < 0:
#         rgb_code = (255/2 + abs(value)/2, abs(value), 255/2 + abs(value)/2)
#     else:
#         rgb_code = (125+value/2, 0, 255/2-value/2)
    if value < 0:
        rgb_code = (255, 255, abs(value))
    else:
        rgb_code = (255, 255-value, 0)
    return rgb_code


def scale(values, input_range, output_range):
    return np.interp(values, input_range, output_range)


def get_legends(value_range, scale_to, step=5):
    min_value, max_value = value_range
    leg_values = np.linspace(min_value, max_value, step)
    scaled_values = scale(leg_values, (min_value, max_value), scale_to)
    
    legends = []
    for leg_value, scaled_value in zip(leg_values, scaled_values):
         legends.append(color_text('{:.2f}'.format(leg_value), value2rgb(scaled_value)))
    return legends


def color_texts(texts, values, use_absolute):
    if use_absolute:
        value_range = (0, 1)
    else:
        value_range = (min(values), max(values))
    scale_to = (-255, 255)
    scaled_values = scale(values, value_range, scale_to)
    result = []
    for text, value in zip(texts, scaled_values):
        rgb = value2rgb(value)
        result.append(color_text(text, rgb))
       
    
    colored = ' '.join(result)
    legends = get_legends(value_range, scale_to)

    colored += ' ({})'.format(' '.join(legends))
        
    if use_absolute:
        colored += ' (min: {:.10f} max: {:.10f})'.format(min(values), max(values))
    
    return colored


def visual_matrix(matrix, labels=None, title=None, **kwargs):

    sns.set(font_scale=0.8)
    ax = sns.heatmap(matrix, xticklabels=labels, yticklabels=labels, cmap='crest', cbar=False, **kwargs)
    if title:
        ax.set(title = title)

    return ax


def get_or_default_config(layer_num, batch_num, head_num, token_num, atn_axis, atns):
    if layer_num is None:
        layer_num = -1  # last layer
    
    batch_size = len(atns[0])
    if batch_size == 1:
        batch_num = 0
    else:
        if batch_num is None:
            raise ValueError('You input an attention with batch size != 1. Please input attentions with batch size 1 or specify the batch_num you want to visualize.')
            
    if head_num is None:
        head_num = 'average'

    if token_num is None:
        token_num = 'average'

    if atn_axis is None:
        atn_axis = 0
        
    return layer_num, batch_num, head_num, token_num, atn_axis


def get_multihead_atn_matrix(atns, layer_num=None, batch_num=None):
    
    
#     layer_num, batch_num = get_or_default_layer_and_batch_num(layer_num, batch_num, atns)
    
    layer = atns[layer_num]

    try:
        multihead_atn_matrix = layer[batch_num].detach().cpu().numpy()  # pytorch
    except TypeError:
        multihead_atn_matrix = layer[batch_num].cpu().numpy()  # pytorch
    except AttributeError:
        multihead_atn_matrix = layer[batch_num]  # tensorflow

    return multihead_atn_matrix


def get_atn_matrix_from_mh_matrix(multihead_atn_matrix, head_num):
    # atn_matrix: (sequence_length, sequence_length)       
    try:
        atn_matrix = multihead_atn_matrix[head_num]
    except (IndexError, TypeError):
        # average over heads        
        atn_matrix = np.mean(multihead_atn_matrix, axis=0)

    return atn_matrix


def merge_atn_matrix(atn_matrix, mean_over_mat_axis):
    atn_matrix_over_axis: list = np.mean(atn_matrix, axis=mean_over_mat_axis)
    return atn_matrix_over_axis


def matrix2values(matrix, index='average', axis=0):
    
    if index == 'average':
        result_mat = np.mean(matrix, axis=axis)
    elif isinstance(index, int):
        if axis == 0:
            result_mat = matrix[index]
        elif axis == 1:
            result_mat = matrix.T[index]
        else:
            raise ValueError('matrix to values have a wrong axis (0 or 1): ' + str(axis))
    else:
        raise ValueError('matrix to values have a wrong index ("average" or integers): ' + str(index))
    
    return result_mat
        

def get_atn_values(layer_num, batch_num, head_num, token_num, atn_axis, atns):
    layer_num, batch_num, head_num, token_num, atn_axis = get_or_default_config(layer_num, batch_num, head_num, token_num, atn_axis, atns)
    multihead_atn_matrix = get_multihead_atn_matrix(atns, layer_num=layer_num, batch_num=batch_num)
    atn_matrix = get_atn_matrix_from_mh_matrix(multihead_atn_matrix, head_num=head_num)
    atn_values = matrix2values(atn_matrix, index=token_num, axis=atn_axis)
    
    return atn_values


def get_atn_matrix(layer_num, batch_num, head_num, atns):
    layer_num, batch_num, head_num, *_ = get_or_default_config(layer_num, batch_num, head_num, None, None, atns)

    multihead_atn_matrix = get_multihead_atn_matrix(atns, layer_num=layer_num, batch_num=batch_num)
    atn_matrix = get_atn_matrix_from_mh_matrix(multihead_atn_matrix, head_num=head_num)
    return atn_matrix


def visual_atn(labels, atns, layer_num=None, batch_num=None, head_num=None, token_num=None, atn_axis=None,
               use_absolute=False, output=False, **kwargs):
    atn_values = get_atn_values(layer_num, batch_num, head_num, token_num, atn_axis, atns)
    layer_num, batch_num, head_num, token_num, atn_axis = get_or_default_config(layer_num, batch_num, head_num, token_num, atn_axis, atns)

    assert len(labels) == len(atn_values), 'len(labels): {}, len(merged_atn_values): {}'.format(len(labels), len(atn_values))

    colored = color_texts(labels, atn_values, use_absolute)

    try:
        label = labels[token_num]
    except TypeError:
        label = 'ALL_TOKENS'

    print('(layer) {} (batch) {} (head) {} (token_num) {} (token) {} (axis) {}'.format(layer_num, batch_num, head_num, token_num, label, atn_axis))

    if output:
        return colored, atn_values
    else:
        return colored

    
def visual_atn_matrix(labels, atns, layer_num=None, batch_num=None, head_num=None, token_num=None, output=False):
    
    atn_matrix = get_atn_matrix(layer_num, batch_num, head_num, atns)
    
    layer_num, batch_num, head_num, token_num, _ = get_or_default_config(layer_num, batch_num, head_num, token_num, None, atns)
    
    title = '(layer) {} (batch) {} (head) {}'.format(layer_num, batch_num, head_num)
    
    # if output:
    #     return visual_matrix(atn_matrix, labels, title=title), atn_matrix
    # else:
    #     return visual_matrix(atn_matrix, labels, title=title)
    return atn_matrix


def merge_attentions(indices, attentions):
    row_averaged = np.average(attentions[indices], axis=0).reshape(1, attentions.shape[1])
    row_averaged_attentions = np.vstack((attentions[:indices[0]], row_averaged, attentions[indices[-1]+1:]))
    col_averaged = np.average(row_averaged_attentions[:, indices], axis=1).reshape(row_averaged_attentions.shape[0], 1)
    row_col_averaged_attentions = np.hstack((row_averaged_attentions[:, :indices[0]], col_averaged, row_averaged_attentions[:, indices[-1]+1:]))
    return row_col_averaged_attentions


def clone_attentions(indices, attentions):
    row = attentions[indices[0]].reshape(1, attentions.shape[1])
    row_cloned = np.zeros(row.shape)
    for i in range(len(indices)):
        row_cloned = np.vstack((row_cloned, row))

    row_cloned_attentions = np.vstack((attentions[:indices[0]], row_cloned[1:], attentions[indices[0]+1:]))

    col = row_cloned_attentions[:, indices[0]].reshape(row_cloned_attentions.shape[0], 1)
    col_cloned = np.zeros(col.shape)
    for i in range(len(indices)):
        col_cloned = np.hstack((col_cloned, col))

    row_col_cloned_attentions = np.hstack((row_cloned_attentions[:, :indices[0]], col_cloned[:, 1:], row_cloned_attentions[:, indices[0]+1:]))

    return row_col_cloned_attentions


def is_substring(s1, s2):
    if s2 in s1:
        return True
    return False


def split(s1, s2):
    to_split = [''] * 2
    to_split[0] = s2
    to_split[1] = s1[len(s2):len(s1)]
    return to_split


def adjust_tokens(bpe_tokens, java_tokens_types, attentions):

    # clean the tokens
    bpe_tokens = [x.replace(' ', '') if x != '\n' else x for x in bpe_tokens]
    java_tokens = [x.replace(' ', '') if x != '\n' else x for x,y in java_tokens_types]

    code_index = 0
    bpe_index = 0
    merge_indices = []
    split_indices = []

    while code_index < len(java_tokens):

        if bpe_tokens[bpe_index] in ['<s>', '</s>', '\n']:
            bpe_index += 1
            continue

        if java_tokens[code_index] == bpe_tokens[bpe_index]:
            code_index += 1
            bpe_index += 1

            if split_indices != []:
                attentions = clone_attentions([split_indices[0]] * (len(split_indices) + 1), attentions)
            
            if merge_indices != []:
                attentions = merge_attentions(merge_indices, attentions)

            merge_indices = []
            split_indices = []

        
        else:
            if is_substring(java_tokens[code_index], bpe_tokens[bpe_index]):
                merged_string = bpe_tokens.pop(bpe_index) + bpe_tokens.pop(bpe_index)
                bpe_tokens.insert(bpe_index, merged_string)
                
                if merge_indices == []:
                    merge_indices.append(bpe_index)
                    merge_indices.append(bpe_index + 1)
                else:
                    merge_indices.append(merge_indices[-1] + 1)
            
            else:
                if is_substring(bpe_tokens[bpe_index], java_tokens[code_index]):
                    to_split = bpe_tokens.pop(bpe_index)
                    splitted_token = split(to_split, java_tokens[code_index])
                    bpe_tokens.insert(bpe_index, splitted_token[1])
                    bpe_tokens.insert(bpe_index, splitted_token[0])
                    split_indices.append(bpe_index)

                    bpe_index += 1
                    code_index += 1
                
                else:
                    print('exceptional case')
                    raise Exception

    # testing if the new matrix dimension is correct after reducing and expanding it
    decoded_tokens = []
    for i in range(len(bpe_tokens[2:-1])):
        if bpe_tokens[i+2] == '\n':
            java_tokens_types.insert(i, ['\n', ['linebreak.java']])
        decoded_tokens.append((bpe_tokens[i+2], java_tokens_types[i][1]))

    assert len(bpe_tokens) == attentions.shape[0]
    return attentions[2:-1, 2:-1], decoded_tokens


def analyze_least_attended_tokens(project_lat):
    categories = {}

    for x, y in project_lat:
        cat = '.'.join(x[1][-1].split('.')[:-1])
        categories.setdefault(cat, 0)
        categories[cat] += 1
    
    return categories


def tokenize(fname):
    lines = []
    with open(fname) as f:
        lines = f.readlines()

    key = ''
    value = ''
    pairs = []
    for line in lines:
        if ':' in line:
            key = ':'.join(line.split(':')[3:]).strip()

        elif line.strip().startswith('[') and line.strip().endswith(']'):
            value = line.strip()[1:-1]
            pairs.append((key, ast.literal_eval('[' + value + ']')))
            key, value = '', ''

        elif line.startswith('  '):
            value += line

        elif line.strip() == ']':
            pairs.append((key, ast.literal_eval('[' + value + ']')))
            key, value = '', ''

    tokens = []
    for token, scope in pairs:
        if token == '': continue
        # if 'punctuation.definition.comment.java' in scope or 'comment.block.javadoc.java' in scope or 'comment.line.double-slash.java' in scope: continue

        tokens.append((token, scope))

    return tokens
