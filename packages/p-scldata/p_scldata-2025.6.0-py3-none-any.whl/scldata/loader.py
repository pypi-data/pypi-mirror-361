import argparse
import json
import pandas as pd
from typing import Tuple, Union
from pathlib import Path

_DATA_DIR = Path(__file__).parent/'data'

with open(f'{_DATA_DIR}/labels.json', 'r') as f:
    labels = json.load(f)

with open(f'{_DATA_DIR}/splits.json', 'r') as f:
    splits = json.load(f)

with open(f'{_DATA_DIR}/entries.json', 'r') as f:
    entries = json.load(f)

def load(split: Union[str, int, None] = None) -> Union[pd.DataFrame, Tuple[pd.DataFrame]]:
    """
    A function for loading the full or split SCL2205 dataset.

    Parameters
    ----------
    `split`: `str` | `int`, optional

    :param split: `str` or `int` or `None`. If `str`, it can be either of "full", "train", "eval", "heldout". Integers can be provided in string form.

    Returns
    -------
    `pandas.DataFrame`

    :return: A `Pandas DataFrame` with UniProtKB unique entries as indices. The first column is "seq" (protein sequence), and the second is "scl" (subcellular location).

    Descriptions
    -----
    full : str
        The complete, unsplit SCL2205 dataset.
    train : str
        The part of SCL2205 used for model training in the *train-eval-test* model development approach.
    eval : str
        The part of SCL2205 used for model evaluation during training in the *train-eval-test* model development approach.
    heldout : str
        The part of SCL2205 used only for the **final** (internal) model testing.
    k : int | str
        The value of the "split" param specifying a fold split of the SCL2205 dataset in the k-fold cross-validation model development approach. An integer string may be provided.

    """

    df_full = pd.read_csv(f'{_DATA_DIR}/scl2205.csv', index_col='entry')

    if split is None or split == 'full':
        return df_full.replace({int(k): v for k, v in labels['index_to_label'].items()})
    elif split == 'train':
        return df_full.loc[[entries[str(idx)] for idx in splits['trn']]].replace({int(k): v for k, v in labels['index_to_label'].items()})
    elif split == 'eval':
        return df_full.loc[[entries[str(idx)] for idx in splits['evl']]].replace({int(k): v for k, v in labels['index_to_label'].items()})
    elif split == 'heldout':
        return df_full.loc[[entries[str(idx)] for idx in splits['tst']]].replace({int(k): v for k, v in labels['index_to_label'].items()})
    elif (isinstance(split, int) or isinstance(int(split), int)) and int(split) in range(5):
        k = int(split)
        return (df_full.loc[[entries[str(idx)] for idx in splits['cv'][f'f{k}']['trn']]].replace({int(k): v for k, v in labels['index_to_label'].items()}),
                df_full.loc[[entries[str(idx)] for idx in splits['cv'][f'f{k}']['tst']]].replace({int(k): v for k, v in labels['index_to_label'].items()}))
    else:
        raise ValueError('split must be either None, "full", "train", "eval", "heldout" or an integer(-string) representing a k-fold split, eg. 0 0r "0"')

def main():
    pass

if __name__ == '__main__':
    main()
