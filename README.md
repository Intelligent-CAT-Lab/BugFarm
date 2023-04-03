# BUGFARM
In this project, we interpret code-language models to produce bug-inducing transformations to inject a bug without the model noticing it.

## Dependencies
All experiments require Python 3.7 (some experiments may need a higher version, i.e., when using OpenAI API) and a Linux/Mac OS. Please execute the following to install dependencies and download the projects:

`sudo bash setup.sh`

Moreover, you need to setup the [tokenizer tool](https://github.com/devreplay/source-code-tokenizer).

## Method Extraction
The first step is to extract the methods from the listed projects in `setup.sh`. Execute the following to extract the methods using 8 CPU cores:

`bash scripts/extract_methods.sh method_extractor.log 8`

This will create a log file which contains some stats about methods in `logs/method_extractor.log`. Moreover, it will store all methods and their metadata inside `data/$project/unique_methods.jsonl`. Each line in this file corresponds to a method and it comes in the following format:

```
{
    "index": "0", 
    "project": "commons-cli", 
    "file_path": "projects/commons-cli/src/main/java/org/apache/commons/cli/CommandLineParser.java", 
    "start_line": "65", 
    "end_line": "66", 
    "method": "    CommandLine parse(Options options, String[] arguments, boolean stopAtNonOption) throws ParseException;\n\n", 
    "tokens": [["CommandLine", ["source.java", "storage.type.java"]], ["parse", ["source.java", "meta.function-call.java", "entity.name.function.java"]], ["(", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.begin.bracket.round.java"]], ["Options", ["source.java", "meta.function-call.java", "storage.type.java"]], ["options", ["source.java", "meta.function-call.java"]], [",", ["source.java", "meta.function-call.java", "punctuation.separator.delimiter.java"]], ["String", ["source.java", "meta.function-call.java", "storage.type.object.array.java"]], ["[", ["source.java", "meta.function-call.java", "punctuation.bracket.square.java"]], ["]", ["source.java", "meta.function-call.java", "punctuation.bracket.square.java"]], ["arguments", ["source.java", "meta.function-call.java"]], [",", ["source.java", "meta.function-call.java", "punctuation.separator.delimiter.java"]], ["boolean", ["source.java", "meta.function-call.java", "storage.type.primitive.java"]], ["stopAtNonOption", ["source.java", "meta.function-call.java"]], [")", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.end.bracket.round.java"]], ["throws ParseException", ["source.java"]], [";", ["source.java", "punctuation.terminator.java"]]]
}
```

## Attention Extraction
The second step is to extract attention weights from the methods in `data/$project/unique_methods.jsonl`. Execute the following to extract attention weights of codebert-base using GPU 0:

`bash scripts/extract_attentions.sh attention_extractor.log codebert base 0`

This will create a log file which contains some stats about methods in `logs/attention_extractor.log`. Moreover, it will store all methods and their attention weights inside `data/$project/unique_methods_codebert-base_attnw.jsonl`.

## Attention Analysis
The third step is to analyze attention weights and determine Least Attended Tokens (LAT) and Least Attended Statements (LAS). Execute the following to analyze the attention weights of codebert-base and determine the LAT/LAS using 8 CPU cores with a threshold (k) of 10:

`bash scripts/analyze_attentions.sh attention_analyzer.log codebert base 10 8`

This will create a log file which contains some stats about methods in `logs/attention_analyzer.log`. Moreover, it will store all methods, attention weights, and LAS/LAT inside `data/$project/unique_methods_codebert-base_las_lat.jsonl`.

## Prompting LLM
The fourth step is to use the LASs/LATs, craft custom prompts, and query an LLM (i.e., ChatGPT). Execute the following to send custom prompts of codebert-base to ChatGPT and store its responses inside `data/$project/unique_methods_codebert-base_chatgpt.jsonl`. If a connection error happens because of OpenAI API, you may execute the same command and the requests will resume without deleting existing responses. You may want to change `python3` to point to a higher version (i.e., 3.9) because OpenAI API is not compatible with older versions of python.

`bash scripts/prompting.sh codebert base`

## Parsing LLM Response
The fifth step is to parse the LLM response. Execute the following to parse ChatGPT responses from codebert-base using 8 CPU cores, and save each buggy method inside `data/$project/unique_methods_codebert-base_NBugs.jsonl`:

`bash scripts/parse_response.sh parse_chatgpt.log codebert base 8`
