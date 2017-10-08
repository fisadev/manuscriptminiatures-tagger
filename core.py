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

    @property
    def picture_path(self):
        return settings.PICTURES_DIR / self.file_name

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

    def __str__(self):
        return '<Miniature {} ({})>'.format(self.miniature_id, self.file_name)

    @classmethod
    def all(cls):
        """
        Read all the miniatures metadata, and return them as Miniature
        instances (ignoring bad lines in the csv).
        """
        for line in settings.METADATA_CSV.open().readlines():
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
