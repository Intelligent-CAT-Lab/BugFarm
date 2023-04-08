# !/usr/bin/env bash

WORKDIR=`pwd`
export PYTHONPATH=$WORKDIR
export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/test_mutants.sh MODEL_NAME MODEL_SIZE NUM_WORKERS";
    echo "MODEL_NAME is required [one of codebert, codet5, NatGen]";
    echo "MODEL_SIZE is required [base]";
    echo "NUM_WORKERS is required";    
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

MODEL_NAME=$1;
MODEL_SIZE=$2;
NUM_WORKERS=$3;

projects=("commons-cli" "commons-codec" "commons-collections" "commons-compress" "commons-csv" "commons-jxpath" "commons-lang" "commons-math" "gson" "jackson-core" "jackson-databind" "jackson-dataformat-xml" "jfreechart" "joda-time" "jsoup");

for project in "${projects[@]}"
do
    python3 src/test/test.py --project_name $project --model_name $MODEL_NAME-$MODEL_SIZE --num_workers $NUM_WORKERS;
done
