# !/usr/bin/env bash

WORKDIR=`pwd`
export PYTHONPATH=$WORKDIR
export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/test_mutants.sh PROJECT_NAME MODEL_NAME MODEL_SIZE";
    echo "PROJECT_NAME is required [one of commons-cli, commons-codec, commons-collections, commons-compress, commons-csv, commons-jxpath, commons-lang, commons-math, gson, jackson-core, jackson-databind, jackson-dataformat-xml, jfreechart, joda-time, jsoup]";
    echo "MODEL_NAME is required [one of codebert, codet5, NatGen]";
    echo "MODEL_SIZE is required [base]";
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

if [[ $# < 3 ]]; then
  prompt;
fi

PROJECT_NAME=$1;
MODEL_NAME=$2;
MODEL_SIZE=$3;

python3 src/test/test.py --project_name $PROJECT_NAME --model_name $MODEL_NAME --model_size $MODEL_SIZE;
