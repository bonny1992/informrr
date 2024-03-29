import time, urllib, yaml, datetime, logging, json
import requests
import schedule
from pytz import timezone
from pathlib import Path
from models import Show, Movie, Track
from utils import aprint, DATA_PATH

config_file = Path(DATA_PATH + '/config.yml')

def get_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f%z')

def get_hours_min(datetime_obj):
    return datetime_obj.strftime('%H:%M')

while True:
    if not config_file.is_file():
        aprint('Waiting 5 seconds for config file generation', 'NOTIFICATOR')
        time.sleep(500)
    break

with open(DATA_PATH + '/config.yml', 'r') as opened:
    CONFIG = yaml.load(opened, Loader=yaml.SafeLoader)

aprint('Starting Informrr notificator...', 'NOTIFICATOR')

current_tz = timezone(CONFIG['timezone'])

def create_shows_msg():
    msg = '*Shows*\n\n{SHOWS}\n\n\n'
    episodes = Show.select().order_by(Show.series).order_by(Show.season).order_by(Show.episode)
    if len(episodes) > 0:
        eps = []
        for episode in episodes:
            timestamp = get_datetime(episode.timestamp)
            eps.append(
                CONFIG['custom_tv_entry'].format(
                    SERIES = episode.series,
                    SEASON = episode.season,
                    EPISODE = episode.episode,
                    TITLE = episode.title,
                    QUALITY = episode.quality,
                    TIME = get_hours_min(timestamp)
                )
            )
        eps_full_text = '\n'.join(eps)
        msg = msg.format(
            SHOWS = eps_full_text
        )
        return {
            'number': len(eps),
            'msg': msg,
            'type': 'shows'
        }
    return {
        'number': 0,
        'msg': '',
        'type': 'shows'
    }

        
def create_movies_msg():
    msg = '*Movies*\n\n{MOVIES}\n\n\n'
    movies = Movie.select().order_by(Movie.title)
    if len(movies) > 0:
        mvs = []
        for movie in movies:
            timestamp = get_datetime(movie.timestamp)
            mvs.append(
                CONFIG['custom_movie_entry'].format(
                    TITLE = movie.title,
                    YEAR = movie.year,
                    QUALITY = movie.quality,
                    IMDB_LINK = '[IMDB Link](https://www.imdb.com/title/{}/)'.format(movie.imdb),
                    TIME = get_hours_min(timestamp)
                )
            )
        mvs_full_text = '\n'.join(mvs)
        msg = msg.format(
            MOVIES = mvs_full_text
        )
        return {
            'number': len(mvs),
            'msg': msg,
            'type': 'movies'
        }
    return {
        'number': 0,
        'msg': '',
        'type': 'movies'
    }

def create_tracks_msg():
    msg = '*Tracks*\n\n{TRACKS}\n\n\n'
    tracks = Track.select().order_by(Track.artist).order_by(Track.tracknumber)
    if len(tracks) > 0:
        tks = []
        for track in tracks:
            timestamp = get_datetime(track.timestamp)
            tks.append(
                CONFIG['custom_track_entry'].format(
                    ARTIST = track.artist,
                    TITLE = track.title,
                    TRACK_NUMBER = track.tracknumber,
                    QUALITY = track.quality,
                    TIME = get_hours_min(timestamp)
                )
            )
        tks_full_text = '\n'.join(tks)
        msg = msg.format(
            TRACKS = tks_full_text
        )
        return {
            'number': len(tks),
            'msg': msg,
            'type': 'tracks'
            }
    return {
        'number': 0,
        'msg': '',
        'type': 'tracks'
        }

def send_tg_message():
    aprint('Preparing the notification for Telegram...', 'NOTIFICATOR')
    tv = create_shows_msg()
    movies = create_movies_msg()
    tracks = create_tracks_msg()
    msgs = [
        tv,
        movies,
        tracks
    ]
    for msg in msgs:
        if msg['msg'] == '':
            return
        quiet = False
        if msg['number'] < 1:
            aprint('Nothing to notify')
            continue
        if msg['number'] > 4000:
            if msg['type'] == 'shows':
                msg_type = CONFIG['shows_label']
            if msg['type'] == 'movies':
                msg_type = CONFIG['movies_label']
            if msg['type'] == 'tracks':
                msg_type = CONFIG['tracks_label']
            msg = CONFIG['custom_too_long_message'].format(
                TYPE = msg_type,
                N_IMPORTED = msg['number']
            )
        hour = int(datetime.datetime.now(current_tz).hour)
        to_be_sent = msg['msg']
        if hour >= int(CONFIG['start_quiet']) or hour <= int(CONFIG['end_quiet']):
            quiet = True
            to_be_sent = CONFIG['custom_quiet_mode_message'] + '\n\n' + to_be_sent
        TG_URL = 'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&disable_web_page_preview=true&parse_mode=Markdown{QUIET}&text={MSG}'
        TG_URL = TG_URL.format(
            BOT_TOKEN = CONFIG['telegram_bot_token'],
            TG_CHAT_ID = CONFIG['telegram_chat_id'],
            QUIET = '&disable_notification=true' if quiet else '',
            MSG = urllib.parse.quote_plus(to_be_sent)
        )
        aprint(
            'Sending notification to Telegram - No. of {}: {}'.format(
                msg['type'], msg['number']
            ), 'NOTIFICATOR'
        )
        requests.get(TG_URL)

def send_discord_message():
    aprint('Preparing the notification for Discord...', 'NOTIFICATOR')
    tv = create_shows_msg()
    movies = create_movies_msg()
    tracks = create_tracks_msg()
    msgs = [
        tv,
        movies,
        tracks
    ]
    for msg in msgs:
        if msg['msg'] == '':
            return
        quiet = False
        if msg['number'] < 1:
            aprint('Nothing to notify')
            continue
        if msg['number'] > 2000:
            if msg['type'] == 'shows':
                msg_type = CONFIG['shows_label']
            if msg['type'] == 'movies':
                msg_type = CONFIG['movies_label']
            if msg['type'] == 'tracks':
                msg_type = CONFIG['tracks_label']
            msg = CONFIG['custom_too_long_message'].format(
                TYPE = msg_type,
                N_IMPORTED = msg['number']
            )
        DISCORD_URL = CONFIG['discord_webhook']
        if 'slack' not in DISCORD_URL:
            DISCORD_URL = DISCORD_URL + '/slack'
        cond = {
            'text': msg['msg']
        }
        aprint(
            'Sending notification to Discord - No. of {}: {}'.format(
                msg['type'], msg['number']
            ), 'NOTIFICATOR'
        )
        requests.post(DISCORD_URL, data=cond)

def db_cleanup():
    # Movie cleanup
    aprint('Cleaning up movies...', 'NOTIFICATOR')
    movies = Movie.select().order_by(Movie.title)
    n_movies = len(movies)
    for movie in movies:
        deletion = Movie.delete().where(
                Movie.imdb == movie.imdb,
                Movie.quality == movie.quality
            )
        deletion.execute()
    aprint('Deleted {} movies.'.format(n_movies), 'DB.CLEAN')

    # TV cleanup
    aprint('Cleaning up tv shows...', 'NOTIFICATOR')
    episodes = Show.select().order_by(Show.series).order_by(Show.season).order_by(Show.episode)
    n_episodes = len(episodes)
    for episode in episodes:
        deletion = Show.delete().where(
                Show.series == episode.series,
                Show.season == episode.season,
                Show.episode == episode.episode
            )
        deletion.execute()
    aprint('Deleted {} episodes.'.format(n_episodes), 'DB.CLEAN')

    # Tracks cleanup
    aprint('Cleaning up tracks...', 'NOTIFICATOR')
    tracks = Track.select().order_by(Track.artist).order_by(Track.tracknumber)
    n_tracks = len(tracks)
    for track in tracks:
        deletion = Track.delete().where(
                Track.artist == track.artist,
                Track.title == track.title,
                Track.tracknumber == track.tracknumber,
                Track.quality == track.quality
            )
        deletion.execute()
    aprint('Deleted {} tracks.'.format(n_tracks), 'DB.CLEAN')

def send_messages():
    if CONFIG['telegram_bot_token']:
        aprint('Telegram is enabled.', 'NOTIFICATOR')
        send_tg_message()
    if CONFIG['discord_webhook']:
        aprint('Discord is enabled.', 'NOTIFICATOR')
        send_discord_message()
    try:
        db_cleanup()
    except:
        aprint('There was an error cleaning the database. Please contact support.', 'DB.CLEAN')
    


if __name__ == '__main__':
    schedule.every(int(CONFIG['skip_hours'])).hour.at(':00').do(send_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)