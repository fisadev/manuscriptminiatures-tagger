import sys

from core import Miniature


def download_pending_pictures():
    """
    Download miniatures from the metadata file, that aren't already downloaded
    in the miniatures directory (it's able to resume after an incomplete run).
    """
    for miniature_number, miniature in enumerate(Miniature.all()):
        print(miniature_number, miniature, '...', end=' ', flush=True)
        if miniature.picture_path.exists():
            print('already present')
        else:
            print('downloading...', end=' ', flush=True)
            miniature.download_picture()
            print('done')


if __name__ == '__main__':
    download_pending_pictures()
