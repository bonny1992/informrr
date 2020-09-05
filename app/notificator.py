import time, urllib, yaml, datetime, logging, json
import requests
import schedule
from pytz import timezone
from pathlib import Path
from models import Show, Movie
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

aprint('Starting the notificator...', 'NOTIFICATOR')

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
        return len(eps), msg
    return 0, ''

        
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
        return len(mvs), msg
    return 0, ''

def send_tg_message():
    aprint('Preparing the notification for Telegram...', 'NOTIFICATOR')
    tv_n, tv_msg = create_shows_msg()
    mo_n, mo_msg = create_movies_msg()
    msg = tv_msg + mo_msg
    if msg == '':
        return
    quiet = False
    if len(msg) < 1:
        aprint('Nothing to notify')
        return
    if len(msg) > 4000:
        msg = CONFIG['custom_too_long_message'].format(
            N_TV = tv_n,
            N_MOVIE = mo_n
            )
    hour = int(datetime.datetime.now(current_tz).hour)
    if hour >= int(CONFIG['start_quiet']) or hour <= int(CONFIG['end_quiet']):
        quiet = True
        msg = CONFIG['custom_quiet_mode_message'] + '\n\n' + msg
    TG_URL = 'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&disable_web_page_preview=true&parse_mode=Markdown{QUIET}&text={MSG}'
    TG_URL = TG_URL.format(
        BOT_TOKEN = CONFIG['telegram_bot_token'],
        TG_CHAT_ID = CONFIG['telegram_chat_id'],
        QUIET = '&disable_notification=true' if quiet else '',
        MSG = urllib.parse.quote_plus(msg)
    )
    aprint(
        'Sending notification to Telegram - No. of TV Series: {} - No. of Movies: {}'.format(
            tv_n, mo_n
        ), 'NOTIFICATOR'
    )
    requests.get(TG_URL)

def send_discord_message():
    aprint('Preparing the notification for Discord...', 'NOTIFICATOR')
    tv_n, tv_msg = create_shows_msg()
    mo_n, mo_msg = create_movies_msg()
    msg = tv_msg + mo_msg
    if msg == '':
        return
    if len(msg) < 1:
        aprint('Nothing to notify')
        return
    if len(msg) > 2000:
        msg = CONFIG['custom_too_long_message'].format(
            N_TV = tv_n,
            N_MOVIE = mo_n
            )
    DISCORD_URL = CONFIG['discord_webhook']
    if 'slack' not in DISCORD_URL:
        DISCORD_URL = DISCORD_URL + '/slack'
    cond = {
        'text': msg
    }
    requests.post(DISCORD_URL, data=cond)

def db_cleanup():
    # Movie cleanup
    aprint('Cleaning up movies...', 'NOTIFICATOR')
    movies = Movie.select().order_by(Movie.title)
    n_movies = len(movies)
    for movie in movies:
        deletion = Movie.delete().where(
                Movie.imdb == movie.imdb,
            )
        deletion.execute()
    aprint('Deleted {} movies.'.format(n_movies), 'NOTIFICATOR')

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
    aprint('Deleted {} episodes.'.format(n_episodes), 'NOTIFICATOR')

def send_messages():
    if CONFIG['telegram_bot_token'] != '':
        send_tg_message()
    if CONFIG['discord_webhook'] != '':
        send_discord_message()
    db_cleanup()
    


if __name__ == '__main__':
    schedule.every(int(CONFIG['skip_hours'])).hour.at(':00').do(send_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)