import json
from scipy import stats
import argparse


def get_spearman_corr(pair, dct):
    item1, item2 = pair
    freq_item1 = dct[item1]
    freq_item2 = dct[item2]

    a = [freq_item1[k] for k in sorted(freq_item1)]
    b = [freq_item2[k] for k in sorted(freq_item2)]

    res = stats.spearmanr(a, b)
    print('{}-{}: {}'.format(item1, item2, round(res.correlation, 2)))


def main(args):

    models = ['codebert-base', 'codet5-small', 'codet5-base', 'codet5-large', 'plbart-base', 'plbart-large']
    projects = ["commons-cli", "commons-codec", "commons-collections", "commons-compress", "commons-csv", "commons-jxpath", "commons-lang", "commons-math", "gson", "jackson-core", "jackson-databind", "jackson-dataformat-xml", "jfreechart", "joda-time", "jsoup"]

    if args.type == 'cross-model':
        iter1 = models
        iter2 = [projects[projects.index(args.project)]]

    elif args.type == 'cross-project':
        iter1 = projects
        iter2 = [models[models.index(args.model)]]

    entries = {}
    for i in iter1:
        
        entries.setdefault(i, {x:0 for x in ["comment", "constant", "entity", "keyword", "linebreak", "meta", "punctuation", "source", "storage", "string", "variable"]})

        for j in iter2:
            
            if args.type == 'cross-model':
                prefix = f'{i}_{j}'
            elif args.type == 'cross-project':
                prefix = f'{j}_{i}'
            
            with open(f'visualizations/{prefix}_True_0_attention_analysis/freqs.json') as fr:
                data = json.load(fr)

                for k in data:
                    key = k.split('.')[0]
                    entries[i].setdefault(key, 0)
                    entries[i][key] += data[k]

    combs = [(a, b) for idx, a in enumerate(iter1) for b in iter1[idx + 1:]]

    for pair in combs:
        get_spearman_corr(pair, entries)


def parse_args():
    parser = argparse.ArgumentParser("calculate cross-project and cross-model spearman correlations")
    parser.add_argument('--type', type=str, default='cross-project', help='cross-project or cross-model')
    parser.add_argument('--project', type=str, default='commons-cli', help='project name')
    parser.add_argument('--model', type=str, default='codebert', help='model name')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
