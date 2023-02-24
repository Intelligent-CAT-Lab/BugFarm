# !/usr/bin/env bash

export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/extract_methods.sh LOG_FILE_NAME NUM_WORKERS";
    echo "LOG_FILE_NAME is required";
    echo "NUM_WORKERS is required";
    echo "CODESEARCHNET_DIR is required";
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

LOG_FILE_NAME=$1;
NUM_WORKERS=$3;
CODESEARCHNET_DIR=$2;

PATH_TO_JSONL_DIR="$CODESEARCHNET_DIR/java/final/jsonl";
DATASETS=("valid")

for dataset in ${DATASETS[@]};
do 
	python3 method_extractor.py --dataset "$dataset" --dir "$PATH_TO_JSONL_DIR/$dataset" --log_file $LOG_FILE_NAME --num_workers $NUM_WORKERS;
done
