import time, os, shutil, sys, string, random, pprint, logging, datetime
import yaml
from pathlib import Path
from bottle import Bottle, run, route, request, abort, HTTPResponse
from truckpad.bottle.cors import CorsPlugin, enable_cors
from pytz import timezone

from models import db_init, Show, Movie, Track
from utils import aprint, DATA_PATH



def id_generator(size=128, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

config_file = Path(DATA_PATH + '/config.yml')

if not config_file.is_file():
    config_file_copy = Path('/app/config.yml.sample')
    shutil.copy(config_file_copy, config_file)
    sys.exit('Please compile ' + DATA_PATH + '/config.yml file')

with open(DATA_PATH + '/config.yml', 'r') as opened:
    CONFIG = yaml.load(opened, Loader=yaml.SafeLoader)



if CONFIG['safe_key'] == None:
    CONFIG['safe_key'] = id_generator()
    with open(DATA_PATH + '/config.yml', 'w') as opened:
        yaml.dump(CONFIG, opened)

if CONFIG['enable_telegram'] == False and CONFIG['enable_discord'] == False:
    sys.exit('Please compile ' + DATA_PATH + '/config.yml file, as it needs to have at least one of Telegram or Discord enabled.')

if CONFIG['domain'] == None:
    sys.exit('You have to enter your domain.')
else:
    with open (DATA_PATH + '/url.txt', 'w') as opened:
        if CONFIG['domain'].startswith('http://'):
            sys.exit('Your domain should be https://')
        if not CONFIG['domain'].startswith('https://'):
            CONFIG['domain'] = 'https://' + CONFIG['domain']
        if not CONFIG['domain'].endswith('/'):
            CONFIG['domain'] = CONFIG['domain'] + '/'
        opened.write(
            '{DOMAIN}{KEY}/sonarr\n'.format(
                DOMAIN = CONFIG['domain'],
                KEY = CONFIG['safe_key']
            ))
        opened.write(
            '{DOMAIN}{KEY}/radarr\n'.format(
                DOMAIN = CONFIG['domain'],
                KEY = CONFIG['safe_key']
            ))
        opened.write(
            '{DOMAIN}{KEY}/lidarr'.format(
                DOMAIN = CONFIG['domain'],
                KEY = CONFIG['safe_key']
            ))

db_init()

app = Bottle()

current_tz = timezone(CONFIG['timezone'])

@app.route('/')
def index():
    return abort(404)

@enable_cors
@app.route('/'+CONFIG['safe_key']+'/sonarr', method='POST')
def webhook_sonarr():
    try:
        if request.json['eventType'] == 'Test':
            aprint('Received TEST webhook', 'WEBHOOK.MAIN')
            return HTTPResponse(status=200)
        if not request.json:
            error = {
                'error': 'Request JSON not correct',
                'code': 10,
            }
            return HTTPResponse(status=500, body=error)
        webhook_request = request.json
        episodes = webhook_request['episodes']
    except:
        error = {
                'error': 'Request JSON not correct',
                'code': 10,
            }
        return HTTPResponse(status=500, body=error)
    
    
    for episode in episodes:
        episode_data = {
            'SERIES': webhook_request['series']['title'],
            'SEASON': str(episode['seasonNumber']).zfill(2),
            'EPISODE': str(episode['episodeNumber']).zfill(2),
            'TITLE': episode['title'],
            'QUALITY': episode.get('quality', 'Unknown')
        }

        msg = '{SERIES} - {SEASON}x{EPISODE} - {TITLE} | {QUALITY}'.format(
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
            quality = episode_data['QUALITY'],
            timestamp = datetime.datetime.now(current_tz)
        )
        new_show.save()
        aprint(msg, 'WEBHOOK.TV')
    return HTTPResponse(status=200)

@enable_cors
@app.route('/'+CONFIG['safe_key']+'/radarr', method='POST')
def webhook_radarr():
    try:
        if request.json['eventType'] == 'Test':
            aprint('Received TEST webhook', 'WEBHOOK.MAIN')
            return HTTPResponse(status=200)
        if not request.json:
            error = {
                'error': 'Request JSON not correct',
                'code': 10,
            }
            return HTTPResponse(status=500, body=error)
        webhook_request = request.json
        movie = webhook_request['remoteMovie']
    except:
        error = {
                'error': 'Request JSON not correct',
                'code': 10,
            }
        return HTTPResponse(status=500, body=error)
    
    movie_data = {
        'TITLE': movie['title'],
        'YEAR': movie['year'],
        'QUALITY': webhook_request['movieFile']['quality'] if 'movieFile' in webhook_request else 'Unknown',
        'IMDB':movie['imdbId']
    }
    
    msg = '{TITLE} ({YEAR}) | {QUALITY}'.format(
        TITLE = movie_data['TITLE'],
        YEAR = movie_data['YEAR'],
        QUALITY = movie_data['QUALITY']
    )
    new_movie = Movie(
        title = movie_data['TITLE'],
        year = movie_data['YEAR'],
        quality = movie_data['QUALITY'],
        imdb = movie_data['IMDB'],
        timestamp = datetime.datetime.now(current_tz)
    )
    new_movie.save()
    aprint(msg, 'WEBHOOK.MOVIE')
    return HTTPResponse(status=200)

@enable_cors
@app.route('/'+CONFIG['safe_key']+'/lidarr', method='POST')
def webhook_lidarr():
    try:
        if request.json['eventType'] == 'Test':
            aprint('Received TEST webhook', 'WEBHOOK.MAIN')
            return HTTPResponse(status=200)
        if not request.json:
            error = {
                'error': 'Request JSON not correct',
                'code': 10,
            }
            return HTTPResponse(status=500, body=error)
        # pprint.pprint(request.json)
        webhook_request = request.json
        artist = webhook_request['artist']['name']
        tracks = webhook_request['tracks']
    except Exception as e:
        error = {
                'error': 'Request JSON not correct',
                'code': 10,
                'stack_trace': str(e)
            }
        return HTTPResponse(status=500, body=error)
    for track in tracks:
        track_data = {
            'ARTIST': artist,
            'TITLE': track['title'],
            'TRACK_NUMBER': track['trackNumber'],
            'QUALITY': track['quality']
        }
        msg = '{ARTIST} - {TITLE} ({TRACK_NUMBER}) | {QUALITY}'.format(
            ARTIST = track_data['ARTIST'],
            TITLE = track_data['TITLE'],
            TRACK_NUMBER = track_data['TRACK_NUMBER'],
            QUALITY = track_data['QUALITY']
        )
        new_track = Track(
            artist = track_data['ARTIST'],
            title = track_data['TITLE'],
            tracknumber = track_data['TRACK_NUMBER'],
            quality = track_data['QUALITY'],
            timestamp = datetime.datetime.now(current_tz)
        )
        new_track.save()
        aprint(msg, 'WEBHOOK.MUSIC')
    return HTTPResponse(status=200)

app.install(CorsPlugin(origins=['*']))



if __name__ == '__main__':
    aprint('Starting Informrr server on port 5445...', 'WEBHOOK.MAIN')
    aprint('Listening on endpoint /{KEY}/sonarr'.format(KEY=CONFIG['safe_key']), 'WEBHOOK.MAIN')
    aprint('Listening on endpoint /{KEY}/radarr'.format(KEY=CONFIG['safe_key']), 'WEBHOOK.MAIN')
    aprint('Listening on endpoint /{KEY}/lidarr'.format(KEY=CONFIG['safe_key']), 'WEBHOOK.MAIN')
    from waitress import serve
    serve(app, listen='*:5445', _quiet=True)
