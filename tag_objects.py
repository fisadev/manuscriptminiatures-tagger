"""
Tag objects in miniatures

Usage:
    tag_objects.py OBJECT_NAME

Options:
    OBJECT_NAME         the name of the object to tag in miniatures

During tagging, you can:
    - click twice in the picture, to generate a tagged rectangle (and a preview will be available at preview.png)
    - press backspace to undo the last action (either click or tagged object)
    - press left and right arrows to move through pictures
      (WARNING: don't do it too fast, it will crash TK)
    - press escape to quit
"""
import sys

import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

import attr
from docopt import docopt

from core import Miniature, TaggedObject
import settings


@attr.s
class TaggingStatus:
    current_index = attr.ib(default=0)
    last_click = attr.ib(default=None)
    keep_tagging = attr.ib(default=True)


def tagging_loop(object_name, maximized=True):
    """
    Loop where the user interacts with the miniatures by tagging objects in them.
    """
    status = TaggingStatus()

    miniatures = list(Miniature.all())

    # tag objects until the user quits
    while status.keep_tagging:
        miniature = miniatures[status.current_index]
        miniature.load_objects()

        picture = Image.open(str(miniature.picture_path))

        def on_click(event):
            if event.button == 1:
                x = int(round(event.xdata))
                y = int(round(event.ydata))

                if status.last_click:
                    last_x, last_y = status.last_click

                    # for a rectangle with the two corners, but we don't know
                    # which one is on the top left, etc. Sort them:
                    from_x = min(x, last_x)
                    from_y = min(y, last_y)
                    to_x = max(x, last_x)
                    to_y = max(y, last_y)

                    # save a preview
                    window = picture.copy()
                    window = window.crop((from_x, from_y, to_x, to_y))
                    window.save(str(settings.OBJECT_PREVIEW_PATH))

                    # store rectangle
                    tagged_object = TaggedObject(
                        name=object_name,
                        position=[from_x, from_y, to_x, to_y]
                    )
                    miniature.objects.append(tagged_object)
                    miniature.save_objects()

                    # infor the user
                    print('Tagged', tagged_object, 'in', miniature)

                    # reset clicks
                    status.last_click = None
                else:
                    # first click, store and wait for the second click
                    status.last_click = x, y
                    print('Waiting for second click...')

        def on_move(event):
            if status.last_click and event.xdata is not None and event.ydata is not None:
                rect_x, rect_y = status.last_click
                width, height = event.xdata - rect_x, event.ydata - rect_y
                rect.set_width(width)
                rect.set_height(height)
                rect.set_xy((rect_x, rect_y))
                rect.figure.canvas.draw()

        def on_key(event):
            if event.key == 'escape':
                # stop tagging
                print('User is tired of tagging')
                status.keep_tagging = False
                plt.close('all')
            elif event.key == 'right':
                # next picture
                if status.current_index < len(miniatures) - 1:
                    status.current_index += 1
                    plt.close('all')
            elif event.key == 'left':
                # previous picture
                if status.current_index > 0:
                    status.current_index -= 1
                    plt.close('all')
            elif event.key == 'backspace':
                # clear selection
                rect.set_width(0.1)
                rect.set_height(0.1)
                rect.figure.canvas.draw()

                if status.last_click:
                    # reset clicks
                    status.last_click = None
                    print('Undo click')
                else:
                    print("Can't undo a saved tag")

        # show picture and map events
        ax = plt.imshow(mpimg.imread(str(miniature.picture_path)))

        fig = ax.get_figure()
        fig.canvas.set_window_title(str(miniature))
        fig.canvas.mpl_connect('button_press_event', on_click)
        fig.canvas.mpl_connect('key_press_event', on_key)
        fig.canvas.mpl_connect('motion_notify_event', on_move)

        rect = Rectangle((0, 0), 0, 0, linewidth=1, edgecolor='r', facecolor='none')
        selection = fig.add_subplot(111)
        selection.add_patch(rect)

        status.last_click = None

        if maximized:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())

        plt.show(block=True)


if __name__ == '__main__':
    opts = docopt(__doc__)
    object_name = opts['OBJECT_NAME']

    tagging_loop(object_name)
