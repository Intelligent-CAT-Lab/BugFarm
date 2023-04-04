# BUGFARM
In this project, we interpret code-language models to produce bug-inducing transformations to inject a bug without the model noticing it.

## Dependencies
All experiments require Python 3.7 (some experiments may need a higher version, i.e., when using OpenAI API) and a Linux/Mac OS. Please execute the following to install dependencies and download the projects:

`sudo bash setup.sh`

Moreover, you need to setup the [tokenizer tool](https://github.com/devreplay/source-code-tokenizer).

Please refer to each module under `/src` for detailed explanation of how to perform the experiments.
