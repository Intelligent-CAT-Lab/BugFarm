# Intelligent-Bug-Generation
In this project, we will find model vulnerabilities and change them to generate hard-to-find bugs.


# Prequisites
- python
- Java, including Java 8 for some projects (commons-lang and joda-project)

## Dependencies
Please execute the following to install dependencies and download the projects:

`sudo bash setup.sh`

## Method Extraction
The first step is to extract the methods from the listed projects in `setup.sh`. The following is the way to execute the extraction:

`bash scripts/extract_methods.sh {LOG_FILENAME} {PATH_TO_CODESEARCHNET_JAVA_DIR} {NUM_CPU_WORKER}`

"PATH_TO_CODESEARCHNET_JAVA_DIR" refers to the root path to the of the extracted CodeSearchNet dataset (that is, to the path that include both .pkl file).

Inside the extract_methods.sh , you can adjust which dataset (from valid, train, test) that you want to use.

The will create a log file which contains some stats about methods in `logs/{LOG_FILENAME}`. Moreover, it will store all methods and their metadata inside `data` (separated per train/test/valid) and per their file origin (e.g. train1.jsonl or train2.jsonl). Each line in this file corresponds to a method and it comes in the following format:

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

## Attention Analysis
The second step is to extract attention weights from the methods in `data/$project/unique_methods.jsonl`. Execute the following to extract attention weights of codebert on GPU 0:

`bash scripts/extract_attentions.sh attention_extractor.log codebert 12 0`

This will create a log file which contains some stats about methods in `logs/attention_extractor.log`. Moreover, it will store all methods and their attention weights inside `data/$project/unique_methods_codebert_attnw.jsonl`.

## Attention Visualization and LAT/LAS
The third step is to visualize attention weights and determine Least Attended Tokens (LAT) and Least Attended Statements (LAS). Execute the following to visualize the attention weights of codebert and determine the LAT/LAS:

`bash scripts/visualize_attentions.sh visualize_attention.log codebert 12 10 8`

This will create an HTML file inside `visualizations/codebert_$project$_True_0_attention_analysis` which contains the visualizations.
