from peewee import *
from pathlib import Path
from utils import aprint, DATA_PATH

db = SqliteDatabase(DATA_PATH + '/notifications.db')

class BaseModel(Model):
    class Meta:
        database = db

class Show(BaseModel):
    series = TextField()
    season = TextField()
    episode = TextField()
    title = TextField()
    quality = TextField()
    timestamp = DateTimeField()

class Movie(BaseModel):
    title = TextField()
    year = TextField()
    quality = TextField()
    imdb = TextField()
    timestamp = DateTimeField()


def db_init():
    if not Path(DATA_PATH + '/notifications.db').is_file():
        aprint('Database file not found, creating...', 'WEBHOOK.MAIN')
        db.create_tables([Movie, Show])