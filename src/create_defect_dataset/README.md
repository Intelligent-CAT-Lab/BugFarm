## BugSwarm

We use the real dataset provided by [BugSwarm](http://www.bugswarm.org/) to evaluate the performance of finetuned models. The extracted dataset from BugSwarm is uploaded under `/BUGFARM/real_bugs/` in the anonymous Google Drive folder shared as part of the artifacts. Project files are not uploaded because they are too big, but one can download and mine them using the BugSwarm tool. If project files are available, you can execute the following to create BugSwarm defect dataset:

`python3 src/create_defect_dataset/extract_bugswarm.py`

## Mockito-Closure

We use the real dataset (Mockito and Closure) provided by [Defects4J](https://github.com/rjust/defects4j) to evaluate the performance of finetuned models. The extracted dataset from Defects4J (MC) is uploaded under `/BUGFARM/real_bugs/` in the anonymous Google Drive folder shared as part of the artifacts. You need to have Defects4J V2.0.0 set in order to extract correct and buggy method pairs using the patches provided by Defects4J. Once everything is set, you should execute the following in order to extract method pairs:

`python3 src/create_defect_dataset/extract_mc.py`

## RegMiner

We use the real dataset provided by [RegMiner](https://github.com/SongXueZhi/RegMiner) to evaluate the performance of finetuned models. The extracted dataset is uploaded under `RegMiner/RegMiner_mutants` in the anonymous Google Drive folder shared as part of the artifacts. One can run the following command to extract mutants and methods:

`python3 src/create_defect_dataset/extract_regminer.py`


## Finetuning Dataset
