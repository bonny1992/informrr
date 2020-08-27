from peewee import *
from pathlib import Path

db = SqliteDatabase('/data/notifications.db')

class BaseModel(Model):
    class Meta:
        database = db

class Show(BaseModel):
    series = TextField()
    season = TextField()
    episode = TextField()
    title = TextField()
    quality = TextField()

class Movie(BaseModel):
    title = TextField()
    year = TextField()
    quality = TextField()
    imdb = TextField()


def db_init():
    if not Path('/data/notifications.db').is_file():
        print('Database file not found, creating...')
        db.create_tables([Movie, Show])