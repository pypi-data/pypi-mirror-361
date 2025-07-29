"""
    A dataset (SCL2205) package for subcellular localisation prediction modelling.
    Its use cases include clustering and classification machine learning, and contain dataset tracks for the *train-eval-test* and *cross-validation-test* (`k` = 5) model development approaches.
    Preprocessing is already done, including homology reduction within and across corresponding splits.

    The package also has a command line interface with additional capabilities: use the command `scldata`. Without any options, it prints out an equivalent of `DataFrame.head()`.

    Descriptions
    ------------
    SCL2205
        The dataset name: SubCellularLocalisation and 2205 represents the UniProtKB release year (YY) and month (M).

    Citations
    ---------

    Examples
    --------
    >>> import scldata.loader as sdl # or from scldata.loader import load or from scldata import load
    >>> df_full = sdl.load("full")
    >>> df_full = sdl.load()
    >>> df_train = sdl.load("train")
    >>> df_eval = sdl.load("eval")
    >>> df_heldout = sdl.load("heldout")
    >>> df_kfold0 = sdl.load(0) # retuns a tuple of dataframes with training and testing sets at index 0 and 1, respectively
    >>> df_kfold1_train = sdl.load("1")[0]

    .. note:: The SCL2205 dataset was curated from `UniProtKB`_, the latest release as of 24/01/2023. The indices are persistent identifiers consistent with *UniProtKB entry* identifier.

    .. _UniProtKB: `https://uniprot.org/`

"""
import argparse
from importlib.metadata import version
from scldata.loader import load

__version__ = version('p-scldata')


def main():
    parser = argparse.ArgumentParser(prog='scldata',
                                     description='SCL2205 dataset loading to standard output. With no OPTION(s), outputs the HEAD of the full SCL2205 dataset.',
                                     usage='%(prog)s [OPTIONS]\nusage: %(prog)s [-h] [-s SPLIT] [-f FORMAT] [--scls] [--version]\n\nFor more information, try "-h/--help".',
                                     epilog=(
                                         '\n'
                                         'Descriptions:\n'
                                         '  full : str\n'
                                         '    The complete, unsplit SCL2205 dataset.\n'
                                         '  train : str\n'
                                         '    The part of SCL2205 used for model training in the *train-eval-test* model development approach.\n'
                                         '  eval : str\n'
                                         '    The part of SCL2205 used for model evaluation during training in the *train-eval-test* model development approach.\n'
                                         '  heldout : str\n'
                                         '    The part of SCL2205 used only for the **final** (internal) model testing.\n'
                                         '  k : int | str\n'
                                         '    The value of the "split" param specifying a fold split of the SCL2205 dataset in the k-fold cross-validation model development approach. An integer string may be provided.\n'
                                         '\n'
                                         'Examples:\n'
                                         '  scldata -h\n'
                                         '  scldata --split heldout\n'
                                         '\n'
                                         'Homepage: https://github.com/ousodaniel/scldata\n'
                                         'Repository: https://github.com/ousodaniel/scldata.git\n'
                                         'Bug Tracker: https://github.com/ousodaniel/scldata/issues\n'
                                         '\n'
                                         'Maintainer: Ouso D. O. S. daniel.ouso[at]ucdconnect.ie'
                                     ),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument(
        '-s', '--split',
        type=str,
        default='full',
        choices=['train', 'eval', 'heldout', 'full', '0', '1', '2', '3', '4'],
        help='which split to load: "train", "eval", "heldout", "full", or k-fold ("0"-"4").'
    )
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['head', 'shape', 'all'],
        default='head',
        help='print format: "head", "shape", or "all" (default: "head")'
    )
    parser.add_argument(
        '-c', '--scls',
        action='store_true',
        help='print target classes'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'scldata {__version__}'
    )
    args = parser.parse_args()

    if args.scls:
        print('SCL2205 Target Classes:\n\n', '\n'.join(load().scl.unique()), sep='')
    elif args.format == 'all':
        if args.split not in ('0', '1', '2', '3', '4'):
            print(load(args.split).to_string())
        else:
            print(f'{load(args.split)[0].to_string()}', end='#')
            print(f'{load(args.split)[1].to_string()}')
    elif args.format == 'head':
        if args.split not in ('0', '1', '2', '3', '4'):
            print(f'SCL2205 {args.split.capitalize()} (Head):\n{load(args.split).head()}')
        else:
            print(f'SCL2205 Fold-{args.split} Train (Head):\n{load(args.split)[0].head()}', end='\n\n\n')
            print(f'SCL2205 Fold-{args.split} Test (Head):\n{load(args.split)[1].head()}')

    elif args.format == 'shape':
        if args.split not in ('0', '1', '2', '3', '4'):
            print(f'SCL2205 {args.split.capitalize()} Shape:\n{load(args.split).shape}')
        else:
            print(f'SCL2205 Fold-{args.split} Train Shape:\n{load(args.split)[0].shape}', end='\n\n\n')
            print(f'SCL2205 Fold-{args.split} Test Shape:\n{load(args.split)[1].shape}')
        print(load(args.split).head())

if __name__ == '__main__':
    main()

