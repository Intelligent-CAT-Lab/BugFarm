# Intelligent-Bug-Generation
In this project, we will find model vulnerabilities and change them to generate hard-to-find bugs.

## Dependencies
Please execute the following to install dependencies:

`pip3 install -r requirements.txt`

## Method Extraction
The first step is to extract the methods from all relevant classes in a java project. Please refer to [defects4j](https://github.com/rjust/defects4j) for a detailed explanation of different java projects.

`python3 method_extractor.py --project_name JacksonXml`

This will store all methods and their metadata inside `data/JacksonXml/JacksonXml.jsonl`. Each line in this file corresponds to a method and it comes in the following format:

```
{
    "index": "0", 
    "project": "JacksonXml", 
    "bug_id": "3", 
    "file_path": "./projects/JacksonXml/3/src/main/java/com/fasterxml/jackson/dataformat/xml/deser/FromXmlParser.java", 
    "start_line": "57", 
    "end_line": "61", 
    "method": "        private Feature(boolean defaultState) {\n            _defaultState = defaultState;\n            _mask = (1 << ordinal());\n        }\n\n", 
    "tokens": [["private", ["source.java", "storage.modifier.java"]], ["Feature", ["source.java", "meta.function-call.java", "entity.name.function.java"]], ["(", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.begin.bracket.round.java"]], ["boolean", ["source.java", "meta.function-call.java", "storage.type.primitive.java"]], ["defaultState", ["source.java", "meta.function-call.java"]], [")", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.end.bracket.round.java"]], ["{", ["source.java", "punctuation.section.block.begin.bracket.curly.java"]], ["_defaultState", ["source.java"]], ["=", ["source.java", "keyword.operator.assignment.java"]], ["defaultState", ["source.java"]], [";", ["source.java", "punctuation.terminator.java"]], ["_mask", ["source.java"]], ["=", ["source.java", "keyword.operator.assignment.java"]], ["(", ["source.java", "punctuation.bracket.round.java"]], ["1", ["source.java", "constant.numeric.decimal.java"]], ["<<", ["source.java", "keyword.operator.bitwise.java"]], ["ordinal", ["source.java", "meta.function-call.java", "entity.name.function.java"]], ["(", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.begin.bracket.round.java"]], [")", ["source.java", "meta.function-call.java", "punctuation.definition.parameters.end.bracket.round.java"]], [")", ["source.java", "punctuation.bracket.round.java"]], [";", ["source.java", "punctuation.terminator.java"]], ["}", ["source.java", "punctuation.section.block.end.bracket.curly.java"]]]
}
```

## Attention Analysis
In order to feed every method to the model, analyze its attention and locate least attended statements, please execute the following:

`python3 attention_analysis.py --project_name JacksonXml --model_type codebert`

This will create an HTML file inside `codebert_attention_analysis` which shows the attention analysis for the `JacksonXml` project.