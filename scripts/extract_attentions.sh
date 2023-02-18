# !/usr/bin/env bash

export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/extract_attentions.sh LOG_FILE_NAME MODEL_NAME NUM_LAYERS NUM_WORKERS GPU_ID";
    echo "LOG_FILE_NAME is required";
    echo "MODEL_NAME is required [one of codebert, codet5, codegen]";
    echo "NUM_LAYERS is required [12 for codebert, codet5. 20 for codegen]";
    echo "NUM_WORKERS is required";
    echo "GPU_ID is required";
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

if [[ $# < 5 ]]; then
  prompt;
fi

LOG_FILE_NAME=$1;
MODEL_NAME=$2;
NUM_LAYERS=$3;
NUM_WORKERS=$4;
GPU_ID=$5;

projects=("commons-cli" "commons-codec" "commons-collections" "commons-compress" "commons-csv" "commons-jxpath" "commons-lang" "commons-math" "gson" "jackson-core" "jackson-databind" "jackson-dataformat-xml" "jfreechart" "joda-time" "jsoup")

for project in "${projects[@]}"
do
    python3 attention_extractor.py --project_name $project --log_file $LOG_FILE_NAME --model_type $MODEL_NAME --num_layers $NUM_LAYERS --num_workers $NUM_WORKERS --gpu_id $GPU_ID;
done
