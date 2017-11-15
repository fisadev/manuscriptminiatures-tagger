"""
Generate a set of picture files containing and not containing the specified
object.

Usage:
    generate_set.py OBJECT_NAME NEGATIVES_RATIO

Options:
    OBJECT_NAME         the name of the object.
    NEGATIVES_RATIO     how many negative examples to generate per miniature.
"""
from random import randint

from docopt import docopt

from core import Miniature
import settings


def rectangle_to_square(rectangle, width, height):
    """
    Converts a rectangle in the image, to a valid square. Keeps the original
    rectangle centered whenever possible, but when that requires going outside
    the original picture, it moves the square so it stays inside.

    Assumes the square is able to fit inside the original picture.
    """
    from_x, from_y, to_x, to_y = rectangle

    rectangle_width = to_x - from_x
    rectangle_height = to_y - from_y
    size = max(rectangle_width, rectangle_height)

    x_center = from_x + rectangle_width // 2
    y_center = from_y + rectangle_height // 2

    from_x = x_center - size // 2
    to_x = x_center + size // 2
    from_y = y_center - size // 2
    to_y = y_center + size // 2

    # ensure fitting horizontally
    if from_x < 0:
        to_x = to_x - from_x
        from_x = 0
    elif to_x > width:
        from_x = from_x - (to_x - width)
        to_x = width

    # ensure fitting vertically
    if from_y < 0:
        to_y = to_y - from_y
        from_y = 0
    elif to_y > height:
        from_y = from_y - (to_y - height)
        to_y = height

    return from_x, from_y, to_x, to_y


def rectangles_overlap(rectangle1, rectangle2):
    """
    True when two rectangles overlap.
    """
    from_x1, from_y1, to_x1, to_y1 = rectangle1
    from_x2, from_y2, to_x2, to_y2 = rectangle2

    def overlap_1d(from1, from2, to1, to2):
        return from1 < to2 and to1 > from2

    return (overlap_1d(from_x1, from_x2, to_x1, to_x2) and
            overlap_1d(from_y1, from_y2, to_y1, to_y2))


def extract_positive_rectangles(miniatures, object_name):
    """
    Generate squares containing the specified object.
    """
    for miniature in miniatures:
        width, height = miniature.picture.size

        for tagged_object in miniature.objects:
            if tagged_object.name == object_name:
                yield miniature, rectangle_to_square(tagged_object.position,
                                                     width, height)


def extract_negative_rectangles(miniatures, object_name, negatives_ratio):
    """
    Generate squares not containing the specified object.
    """
    for miniature in miniatures:
        avoid_positions = [tagged_object.position
                           for tagged_object in miniature.objects
                           if tagged_object.name == object_name]

        width, height = miniature.picture.size
        shortest_size = min(width, height)

        generated = 0
        while generated < negatives_ratio:
            example_size = randint(int(shortest_size / 10),
                                   int(shortest_size / 4))
            from_x = randint(0, width - example_size)
            to_x = from_x + example_size
            from_y = randint(0, height - example_size)
            to_y = from_y + example_size

            has_object = any(rectangles_overlap(tagged_object.position,
                                                (from_x, from_y, to_x, to_y))
                             for tagged_object in miniature.objects
                             if tagged_object.name == object_name)

            if not has_object:
                generated += 1
                yield miniature, (from_x, from_y, to_x, to_y)


def miniatures_with_info_about(object_name):
    """
    Extract miniatures that have info regarding an specific object.
    """
    miniatures = []
    for miniature in Miniature.all():
        miniature.load_objects()
        has_object = any(tagged_object.name == object_name
                         for tagged_object in miniature.objects)

        if has_object:
            miniatures.append(miniature)

    return miniatures


def save_pictures(object_name, set_name, rectangles):
    """
    Save all the rectangles from a set as separated picture files.
    """
    set_path = settings.OBJECTS_PICTURES_SETS_DIR / object_name / set_name

    for miniature, rectangle in rectangles:
        file_name = '{}_{}_{}_{}_{}.png'.format(miniature.miniature_id,
                                                *rectangle)
        rectangle_path = set_path / file_name
        picture = miniature.picture.copy()
        picture = picture.crop(rectangle)
        picture.save(rectangle_path)


def generate(object_name, negatives_ratio):
    """
    Generate picture files having the object, and not having the object.
    """
    miniatures = miniatures_with_info_about(object_name)

    print('Will use', len(miniatures), 'miniatures')

    print('Opening all pictures...')
    for m in miniatures:
        m.open_picture()

    print('Extracting positive examples positions...')
    positives = list(extract_positive_rectangles(miniatures, object_name))
    print('Saving positive examples pictures...')
    save_pictures(object_name, 'positives', positives)

    print('Extracting negative examples positions...')
    negatives = list(extract_negative_rectangles(miniatures, object_name,
                                                 negatives_ratio))
    print('Saving negative examples pictures...')
    save_pictures(object_name, 'negatives', negatives)


if __name__ == '__main__':
    opts = docopt(__doc__)
    object_name = opts['OBJECT_NAME']
    negatives_ratio = int(opts['NEGATIVES_RATIO'])

    generate(object_name, negatives_ratio)
