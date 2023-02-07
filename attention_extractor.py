from transformers import AutoTokenizer, AutoModel, T5EncoderModel, RobertaTokenizer, CodeGenModel
import torch
from utils import visual_atn_matrix, adjust_tokens
import multiprocessing
import numpy as np
from json import JSONEncoder
import json
import ast
import argparse
import time
import os
import logging
import sys


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def process_instance(l):
    dct = ast.literal_eval(l)

    # Tokenization 
    nl_tokens = tokenizer.tokenize("")

    method = dct['method']
    statements = method.split('\n')
    statements = [x.strip() for x in statements if x.strip() != '']
    code = '\n'.join(statements)

    code_tokens = tokenizer.tokenize(code)

    if len(code_tokens) > 509:
        return

    if args.model_type == 'codegen':
        tokens = [tokenizer.bos_token]+nl_tokens+[tokenizer.bos_token]+code_tokens+[tokenizer.eos_token]
    else:
        tokens = [tokenizer.cls_token]+nl_tokens+[tokenizer.sep_token]+code_tokens+[tokenizer.eos_token]

    # Convert tokens to ids
    tokens_ids = tokenizer.convert_tokens_to_ids(tokens)
    decoded_tokens = [tokenizer.decode(id_) for id_ in tokens_ids]

    # Extract the attentions
    attentions = model(torch.tensor(tokens_ids)[None,:], output_attentions=True)['attentions']

    # Post-process attentions
    if args.average_layers:
        zeros = np.zeros((len(decoded_tokens), len(decoded_tokens)))
        for i in range(args.num_layers):
            zeros += visual_atn_matrix(decoded_tokens, attentions, layer_num=i, head_num='average')
        
        model_attentions = zeros / args.num_layers
    else:
        model_attentions = visual_atn_matrix(decoded_tokens, attentions, layer_num=args.layer_num, head_num='average')

    try:
        model_attentions, decoded_token_types = adjust_tokens(decoded_tokens, dct['tokens'], model_attentions)
    except Exception:
        return

    dct['model_attentions'] = model_attentions
    dct['decoded_token_types'] = decoded_token_types

    json_file.write(json.dumps(dct, cls=NumpyArrayEncoder) + '\n')
    json_file.flush()


def main(args):
    global tokenizer
    global model
    global json_file

    start = time.time()

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'extracting method attentions from {args.project_name} using {args.model_type}')

    if args.model_type == 'codet5':
        tokenizer = RobertaTokenizer.from_pretrained(f"salesforce/{args.model_type}-base")
        model = T5EncoderModel.from_pretrained(f"salesforce/{args.model_type}-base")
    elif args.model_type == 'codebert':
        tokenizer = AutoTokenizer.from_pretrained(f"microsoft/{args.model_type}-base")
        model = AutoModel.from_pretrained(f"microsoft/{args.model_type}-base")
    elif args.model_type == 'codegen':
        model = CodeGenModel.from_pretrained(f"salesforce/{args.model_type}-350M-mono")
        tokenizer = AutoTokenizer.from_pretrained(f"salesforce/{args.model_type}-350M-mono")

    lines = []
    with open(f'data/{args.project_name}/unique_methods.jsonl') as fr:
        lines = fr.readlines()
    
    json_file = open(f"data/{args.project_name}/unique_methods_{args.model_type}_attnw.jsonl", "wt")

    pool = multiprocessing.Pool(args.num_workers)
    for i, _ in enumerate(pool.imap_unordered(process_instance, lines), 1):
        sys.stderr.write('\rpercentage of method attentions extracted: {0:%}'.format(i/len(lines)))

    logging.info(f'total time in secs for {args.project_name} using {args.model_type}: ' + str(round(time.time() - start, 2)))


def parse_args():
    parser = argparse.ArgumentParser("extract attention weights of a project using a given model")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to process and extract methods')
    parser.add_argument('--model_type', type=str, default='codebert', help='LLM to use in this experiment')
    parser.add_argument('--average_layers', type=lambda x: (str(x).lower() == 'true'), default=True, help='average attention scores of all layers in the model')
    parser.add_argument('--layer_num', type=int, default=0, help='layer number when average_layers=False')
    parser.add_argument('--num_layers', type=int, default=12, help='number of layers in the model')
    parser.add_argument('--log_file', type=str, default='attention_extractor.log', help='log file name')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
