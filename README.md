# Intelligent-Bug-Generation
In this project, we will find model vulnerabilities and change them to generate hard-to-find bugs.

## Dependencies
Please execute the following to install dependencies and download the projects:

`sudo bash setup.sh`

## Method Extraction
The first step is to extract the methods from the listed projects in `setup.sh`.

`bash scripts/extract_methods.sh method_extractor.log`

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

## Attention Analysis
