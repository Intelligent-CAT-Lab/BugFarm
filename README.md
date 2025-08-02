# BugFarm

[ali]: https://alirezai.cs.illinois.edu/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm
[paper]: https://arxiv.org/abs/2310.02407

Artifact repository for the paper [_Challenging Bug Prediction and Repair Models with
Synthetic Bugs_][paper], accepted at _SCAM 2025_, Auckland, New Zealand.
Authors are [Ali Reza Ibrahimzada][ali], Yang Chen, Ryan Rong, and [Reyhaneh Jabbarvand][reyhaneh].

## Table of Contents
- [Overview](#overview)
- [Data Archive](#data-archive)
- [Getting Started](#getting-started)
  - [Using Docker (Recommended)](#using-docker-recommended)
  - [Manual Setup](#manual-setup)
- [Project Modules](#project-modules)
  - [Attention Analyzer](#attention-analyzer)
  - [Bug Generator](#bug-generator)
  - [Create Defect Dataset](#create-defect-dataset)
  - [Bug Prediction](#bug-prediction)
  - [Bug Repair](#bug-repair)
  - [LEAM](#leam)
  - [muBERT](#mubert)
- [Citation](#citation)
- [Contact](#contact)

## Overview

BugFarm is a framework that generates synthetic bugs through the analysis of least-attended tokens and statements in code. These synthetic bugs challenge and evaluate bug prediction and repair models. The pipeline involves extracting methods from projects, analyzing attention weights, determining least-attended components, and using LLMs to generate plausible bugs.

## Data Archive

Please visit [Zenodo](https://doi.org/10.5281/zenodo.13886318) to access the results of BugFarm. We will refer to certain files from this archive in the following sections.

## Getting Started

### Using Docker (Recommended)

The easiest way to set up BugFarm is using Docker:

```bash
# Build the Docker image
docker build -t bugfarm .

# Run the container
docker run -it bugfarm bash
```

### Manual Setup

If you prefer a manual setup:

1. Install [`miniconda`](https://www.anaconda.com/docs/getting-started/miniconda/install)

2. Create and activate the environment:

   ```bash
   conda env create -f environment.yaml
   conda activate bugfarm
   ```

3. Set up the [tokenizer tool](https://github.com/devreplay/source-code-tokenizer)

4. Install dependencies and download projects:

   ```bash
   bash setup.sh
   ```

## Project Modules

### Attention Analyzer

This module extracts methods from projects and analyzes attention weights to determine least attended tokens (LAT) and least attended statements (LAS).

Key steps:
1. Extract methods from projects
2. Extract attention weights
3. Analyze attention weights to determine LAT/LAS

For detailed instructions, see [Attention Analyzer README](src/attention_analyzer/README.md).

### Bug Generator

This module uses LLMs to generate synthetic bugs based on the attention analysis results.

Key steps:
1. Prompt LLM with LAT/LAS information
2. Parse LLM responses to extract buggy methods
3. Select the most suitable bugs

For detailed instructions, see [Bug Generator README](src/bug_generator/README.md).

We provide synthetic bugs on Zenodo. Please download `mutants.zip` from the [BugFarm Zenodo archive](https://doi.org/10.5281/zenodo.13886318).

### Create Defect Dataset

This module creates datasets for training and evaluating bug detection models using various sources:

- BugSwarm
- Mockito-Closure (from Defects4J)
- RegMiner
- LEAM
- muBERT

For detailed instructions, see [Create Defect Dataset README](src/create_defect_dataset/README.md).

We provide defect datasets on Zenodo. Please download `defect_datasets.zip` from the [BugFarm Zenodo archive](https://doi.org/10.5281/zenodo.13886318).

### Bug Prediction

This module finetunes models for bug prediction using the created defect datasets.

For detailed instructions, see [Finetuning README](src/finetuning/README.md).

### Bug Repair

We use artifacts of [FitRepair](https://zenodo.org/records/8327890) for performing bug repair on the generated mutants. Please refer to the original repository for details on how to use FitRepair. We provide the generated patches from FitRepair on Zenodo. Please download `apr.zip` from the [BugFarm Zenodo archive](https://doi.org/10.5281/zenodo.13886318).

### LEAM

This module generates mutants using the LEAM framework.

For detailed instructions, see [LEAM README](src/leam/README.md).

### muBERT

This module generates mutants using the muBERT framework.

For detailed instructions, see [muBERT README](src/mubert/README.md).

## Contact

For any questions or issues, please contact [Ali Reza Ibrahimzada](https://alirezai.cs.illinois.edu/).
