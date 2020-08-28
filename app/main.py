import time, os, shutil, sys, string, random, pprint
import yaml
from pathlib import Path
from bottle import Bottle, run, route, request, abort, HTTPResponse
from truckpad.bottle.cors import CorsPlugin, enable_cors

from models import db_init, Show, Movie

def id_generator(size=128, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

Path("/data").mkdir(parents=True, exist_ok=True)

config_file = Path('/data/config.yml')

if not config_file.is_file():
    config_file_copy = Path('/app/config.yml.sample')
    shutil.copy(config_file_copy, config_file)
    sys.exit('Please compile /data/config.yml file')

with open('/data/config.yml', 'r') as opened:
    CONFIG = yaml.load(opened, Loader=yaml.SafeLoader)



if CONFIG['safe_key'] == None:
    CONFIG['safe_key'] = id_generator()
    with open('/data/config.yml', 'w') as opened:
        yaml.dump(CONFIG, opened)

if CONFIG['telegram_bot_token'] == None:
    sys.exit('Please compile /data/config.yml file')

db_init()

app = Bottle()

@app.route('/')
def index():
    return abort(404)

@enable_cors
@app.route('/'+CONFIG['safe_key']+'/sonarr', method='POST')
def webhook_sonarr():
    if request.json['eventType'] == 'Test':
        return HTTPResponse(status=200)
    if not request.json:
        error = {
            'error': 'Request JSON not correct',
            'code': 10,
        }
        return HTTPResponse(status=500, body=error)
    webhook_request = request.json
    episodes = webhook_request['episodes']
    
    for episode in episodes:
        episode_data = {
            'SERIES': webhook_request['series']['title'],
            'SEASON': str(episode['seasonNumber']).zfill(2),
            'EPISODE': str(episode['episodeNumber']).zfill(2),
            'TITLE': episode['title'],
            'QUALITY': episode.get('quality', 'Unknown')
        }

        msg = 'Download Show {SERIES} - {SEASON}x{EPISODE} - {TITLE} | {QUALITY}'.format(
            SERIES = episode_data['SERIES'],
            SEASON = episode_data['SEASON'],
            EPISODE = episode_data['EPISODE'],
            TITLE = episode_data['TITLE'],
            QUALITY = episode_data['QUALITY']
        )
        new_show = Show(
            series = episode_data['SERIES'],
            season = episode_data['SEASON'],
            episode = episode_data['EPISODE'],
            title = episode_data['TITLE'],
            quality = episode_data['QUALITY']
        )
        new_show.save()
        print(msg)
    return HTTPResponse(status=200)

@enable_cors
@app.route('/'+CONFIG['safe_key']+'/radarr', method='POST')
def webhook_radarr():
    if request.json['eventType'] == 'Test':
        return HTTPResponse(status=200)
    if not request.json:
        error = {
            'error': 'Request JSON not correct',
            'code': 10,
        }
        return HTTPResponse(status=500, body=error)
    webhook_request = request.json
    movie = webhook_request['remoteMovie']

    movie_data = {
        'TITLE': movie['title'],
        'YEAR': movie['year'],
        'QUALITY': webhook_request['movieFile']['quality'] if 'movieFile' in webhook_request else 'Unknown',
        'IMDB':movie['imdbId']
    }
    
    msg = 'Download Movie {TITLE} ({YEAR}) | {QUALITY}'.format(
        TITLE = movie_data['TITLE'],
        YEAR = movie_data['YEAR'],
        QUALITY = movie_data['QUALITY']
    )
    new_movie = Movie(
        title = movie_data['TITLE'],
        year = movie_data['YEAR'],
        quality = movie_data['QUALITY'],
        imdb = movie_data['IMDB']
    )
    new_movie.save()
    print(msg)
    return HTTPResponse(status=200)

app.install(CorsPlugin(origins=['*']))


if __name__ == '__main__':
    from waitress import serve
    serve(app, listen='*:5445')
