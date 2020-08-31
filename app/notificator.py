import time, urllib, yaml, datetime, logging
from urllib.request import urlopen
import schedule
from pytz import timezone
from pathlib import Path
from models import Show, Movie
from utils import aprint, DATA_PATH

config_file = Path(DATA_PATH + '/config.yml')

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
            eps.append(
                '{SERIES} - {SEASON}x{EPISODE} - {TITLE} | {QUALITY} alle {TIME}'.format(
                    SERIES = episode.series,
                    SEASON = episode.season,
                    EPISODE = episode.episode,
                    TITLE = episode.title,
                    QUALITY = episode.quality,
                    TIME = '{}:{}'.format(episode.timestamp.hours, episode.timestamp.minutes)
                )
            )
            deletion = Show.delete().where(
                Show.series == episode.series,
                Show.season == episode.season,
                Show.episode == episode.episode
            )
            deletion.execute()
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
            mvs.append(
                '{TITLE} ({YEAR}) | {QUALITY} | {IMDB_LINK} alle {TIME}'.format(
                    TITLE = movie.title,
                    YEAR = movie.year,
                    QUALITY = movie.quality,
                    IMDB_LINK = '[IMDB Link](https://www.imdb.com/title/{}/)'.format(movie.imdb),
                    TIME = '{}:{}'.format(movie.timestamp.hours, movie.timestamp.minutes)
                )
            )
            deletion = Movie.delete().where(
                Movie.imdb == movie.imdb,
            )
            deletion.execute()
        mvs_full_text = '\n'.join(mvs)
        msg = msg.format(
            MOVIES = mvs_full_text
        )
        return len(mvs), msg
    return 0, ''

def send_tg_message():
    aprint('Preparing the notification...', 'NOTIFICATOR')
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
        msg = 'Troppi caratteri per Telegram.\nN. episodi Serie TV importati: {}\nN. film importati: {}'.format(tv_n, mo_n)
    hour = int(datetime.datetime.now(current_tz).hour)
    if hour >= int(CONFIG['start_quiet']) or hour <= int(CONFIG['end_quiet']):
        quiet = True
        msg = '💤 *Modalità notte* 💤\n\n\n\n' + msg
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
    urlopen(TG_URL)

if __name__ == '__main__':
    schedule.every(int(CONFIG['skip_hours'])).hour.at(':00').do(send_tg_message)
    while True:
        schedule.run_pending()
        time.sleep(1)