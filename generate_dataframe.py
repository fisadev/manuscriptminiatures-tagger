"""
Generate a pandas dataframe from a pictures set.

Usage:
    generate_dataframe.py OBJECT_NAME PICTURE_SIZE

Options:
    OBJECT_NAME         the name of the object.
    PICTURE_SIZE        the size of the pictures inside the dataframe.
"""
from docopt import docopt
import numpy as np
import pandas as pd

from utils import get_dataframe_from_dir
from settings import OBJECTS_PICTURES_SETS_DIR


def get_subset_dataframe(object_name, picture_size, subset_name, label):
    """
    Get the dataframe containing all the pictures from a subset of an
    object-or-not set (subsets are either positive or negative examples).
    """
    subset_path = OBJECTS_PICTURES_SETS_DIR / object_name / subset_name

    get_id_from_file = lambda x: x.split('_')[0]

    pictures_df = get_dataframe_from_dir(subset_path, picture_size)
    pictures_df['miniature_id'] = pictures_df.file.map(get_id_from_file)
    pictures_df.loc[:, 'label'] = label

    return pictures_df


def generate(object_name, picture_size):
    """
    Generate a dataframe containing all the pictures from an object-or-not set.
    """
    print('Extracting positive examples pictures...')
    positives = get_subset_dataframe(object_name, picture_size, 'positives', 1)
    print('Extracting negative examples pictures...')
    negatives = get_subset_dataframe(object_name, picture_size, 'negatives', 0)

    print('Joining both subsets...')
    whole_set = pd.concat([positives, negatives])

    print('Dumping the final dataframe...')
    file_name = 'dataframe_{}.pkl'.format(picture_size)
    dataframe_path = OBJECTS_PICTURES_SETS_DIR / object_name / file_name
    whole_set.to_pickle(str(dataframe_path))

    return whole_set

if __name__ == '__main__':
    opts = docopt(__doc__)
    object_name = opts['OBJECT_NAME']
    picture_size = int(opts['PICTURE_SIZE'])

    generate(object_name, picture_size)
