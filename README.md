# The NineRec Dataset Suite: Benchmarking Transfer Learning Performance for Modality-Based Recommender Systems


# Dataset
**Note that collecting data and running these MoRec experiments cost a lot of money. Our corresponding author and lead suggested a sample of 1000 images in the submission version. If reviewers need to see the entire dataset, we are more than happy to provide full datasets.**

Download link: https://sandbox.zenodo.org/record/1153424#.Y9dALnZByw4



# Benchmark
## Environments
```
Pytorch==1.12.1
cudatoolkit==11.2.1
sklearn==1.2.0
python==3.9.12
```
## Dataset Preparation
Run `get_lmdb.py` to get lmdb database for easier image loading. Run `get_behaviour.py` to convert the user-item pairs into item sequences format.
## Run Experiments
Run `train.py` for pre-training and transferring. Run `test.py` for testing.

# Leaderboard
coming soon.
