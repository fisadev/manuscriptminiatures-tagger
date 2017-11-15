import numpy as np
import pandas as pd
from PIL import Image


def input_columns_names(picture_size):
    """
    Generate the names of the input columns representing the pixels of the
    pictures, for a given picture size.
    """
    input_columns = []
    for color in 'rgb':
        input_columns.extend(['%s%i' % (color, i)
                              for i in range(picture_size ** 2)])

    return input_columns


def get_picture_data(picture_path, picture_size, input_columns):
    """
    Extract pixels from one particular picture.
    """
    picture = Image.open(picture_path)
    picture = picture.resize((picture_size, picture_size), Image.ANTIALIAS)

    # convert grayscale ones to rgb
    if picture.mode == 'L':
        picture = picture.convert('RGB')

    picture_data = np.array(list(zip(*picture.getdata())))
    picture_data = picture_data.reshape(len(input_columns))

    return picture_data


def get_dataframe_from_dir(pictures_dir, picture_size):
    """
    Create a pandas dataframe from a dir of picture files.
    """
    input_columns = input_columns_names(picture_size)
    sorted_picture_paths = list(sorted(pictures_dir.glob('*.jpg')))

    def extract_all_data():
        for picture_path in sorted_picture_paths:
            yield get_picture_data(picture_path, picture_size, input_columns)

    pictures_df = pd.DataFrame(extract_all_data(), columns=input_columns)
    pictures_df['file'] = [p.name for p in sorted_picture_paths]

    return pictures_df
