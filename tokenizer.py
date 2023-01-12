import ast

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

        tokens.append(token)

    return tokens
