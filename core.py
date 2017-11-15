import json
from pathlib import Path

import attr
import requests

import settings


@attr.s
class Miniature:
    manuscript_id = attr.ib()
    miniature_id = attr.ib()
    file_name = attr.ib()
    start_year = attr.ib()
    end_year = attr.ib()
    tags = attr.ib()
    objects = attr.ib(init=False)

    @property
    def picture_path(self):
        return settings.PICTURES_DIR / self.file_name

    @property
    def objects_path(self):
        return settings.OBJECTS_DIR / '{}.json'.format(self.miniature_id)

    def download_picture(self):
        """
        Download the picture file.
        """
        try:
            url = settings.PICTURE_URL.format(self.file_name)
            response = requests.get(url)
            with self.picture_path.open("wb") as picture_file:
                picture_file.write(response.content)
        except Exception as err:
            # clean possibly broken file
            if self.picture_path.exists():
                self.picture_path.unlink()
            raise

    def open_picture(self):
        """
        Open the picture file with PIL, returning an Image instance.
        """
        picture = Image.open(self.picture_path)
        return picture

    def load_objects(self):
        """
        Load tagged objects from the json file.
        """
        if self.objects_path.exists():
            with self.objects_path.open() as objects_file:
                self.objects = [TaggedObject.deserialize(raw_object_data)
                                for raw_object_data in json.load(objects_file)]
        else:
            self.objects = []

    def save_objects(self):
        """
        Save tagged objects into the json file.
        """
        with self.objects_path.open('w') as objects_file:
            raw_data = [tagged_object.serialize()
                        for tagged_object in self.objects]
            json.dump(raw_data, objects_file)

    def __str__(self):
        return '<Miniature {} ({})>'.format(self.miniature_id, self.file_name)

    @classmethod
    def all(cls):
        """
        Read all the miniatures metadata, and return them as Miniature
        instances (ignoring bad lines in the csv).
        """
        for line in settings.METADATA_CSV_PATH.open().readlines():
            fields = [field.strip()
                      for field in line.split(',')
                      if field.strip()]

            if len(fields) > 4:
                tags = fields[5:] if len(fields) > 5 else []
                tags = [tag.lower() for tag in tags]
                yield Miniature(
                    manuscript_id=int(fields[0]),
                    miniature_id=int(fields[1]),
                    file_name=fields[2],
                    start_year=eval(fields[3]),
                    end_year=eval(fields[4]),
                    tags=tags,
                )


@attr.s
class TaggedObject:
    name = attr.ib()
    position = attr.ib()

    def serialize(self):
        """
        Serialize tagged object data.
        """
        return self.name, self.position

    @classmethod
    def deserialize(cls, raw_data):
        """
        Reconstruct tagged object from serialized data.
        """
        name, position = raw_data
        return TaggedObject(name=name, position=position)
