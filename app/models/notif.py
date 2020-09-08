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

class Track(BaseModel):
    artist = TextField()
    title = TextField()
    quality = TextField()
    tracknumber = TextField()
    timestamp = DateTimeField()

def db_init():
    tables = db.get_tables()
    if 'movie' not in tables:
        aprint('`Movie` table not found in db, adding...', 'WEBHOOK.MAIN')
        db.create_tables([Movie])
    if 'show' not in tables:
        aprint('`Show` table not found in db, adding...', 'WEBHOOK.MAIN')
        db.create_tables([Show])
    if 'track' not in tables:
        aprint('`Track` table not found in db, adding...', 'WEBHOOK.MAIN')
        db.create_tables([Track])