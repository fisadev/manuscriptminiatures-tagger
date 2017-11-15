from pathlib import Path

# general settings
PICTURE_URL = 'http://manuscriptminiatures.com/media/manuscriptminiatures.com/original/{}'
PICTURES_DIR = Path('./data/pictures/')
METADATA_CSV_PATH = Path('./data/miniatures_metadata.csv')
OBJECTS_DIR = Path('./data/objects/')
OBJECTS_PICTURES_SETS_DIR = Path('./data/object_picture_sets/')

# objects tagger
OBJECT_PREVIEW_PATH = Path('./last_object_preview.png')
LAST_TAGGED_OBJECTS_PATH = Path('./last_tagged_objects.json')
EMPTY_PICTURE_PATH = PICTURES_DIR / 'no_picture.png'
