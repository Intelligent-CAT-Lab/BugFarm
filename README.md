# BUGFARM

[ali]: https://alirezai.cs.illinois.edu/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm
[paper]: https://arxiv.org/abs/2310.02407

Artifact repository for the paper [_Challenging Bug Prediction and Repair Models with
Synthetic Bugs_][paper], accepted at _SCAM 2025_, Auckland, New Zealand.
Authors are [Ali Reza Ibrahimzada][ali], Yang Chen, Ryan Rong, and [Reyhaneh Jabbarvand][reyhaneh].

## Data Archive
Please visit [Zenodo](https://doi.org/10.5281/zenodo.13886318) to access the results of BugFarm. We will refer to certain files from this archive in the following sections.

## Dependencies
All experiments require Python 3.9 and a Linux/Mac OS. Please execute the following to install dependencies and download the projects:

`sudo bash setup.sh`

Moreover, you need to setup the [tokenizer tool](https://github.com/devreplay/source-code-tokenizer).

Please refer to each module under `/src` for detailed explanation of how to perform the experiments.
