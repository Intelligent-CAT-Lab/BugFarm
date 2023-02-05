# !/usr/bin/env bash

export PYTHONIOENCODING=utf-8;

function prompt() {
    echo;
    echo "Syntax: bash scripts/augment_methods.sh LOG_FILE_NAME";
    echo "LOG_FILE_NAME is required";
    exit;
}

while getopts ":h" option; do
    case $option in
        h) # display help
          prompt;
    esac
done

if [[ $# < 1 ]]; then
  prompt;
fi

LOG_FILE_NAME=$1;

projects=("commons-cli" "jfreechart" "commons-codec" "commons-collections" "commons-compress" "commons-csv" "gson" "commons-lang" "commons-math" "commons-jxpath" "jackson-dataformat-xml" "jackson-core" "jackson-databind" "jsoup" "joda-time" "mockito")

for project in "${projects[@]}"
do
    python3 method_augmentor.py --project_name $project --log_file $LOG_FILE_NAME;
done
