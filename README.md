# Sonarr Radarr Notification Aggregator
(name suggesions open)

![TravisCI.com build status](https://travis-ci.com/bonny1992/sonarr-radarr-notification-aggregator.svg?branch=master&status=passed "TravisCI.com build status")

A simple aggregator for notification from Sonarr and Radarr.

What can it do:
- Configurable pause (in hours)
- Customizable movie and episode entries
- Notification to Telegram
- Notification to Discord



# Install with Docker
I mainly chose to create this to be used with Docker.

You can find the image on Docker Hub [here](https://hub.docker.com/r/bonny1992/sonarr-radarr-notification-aggregator)

1. Here's the `docker run` command needed to start it up:

   ```
   docker run -d \
      --name notificator \
      --restart=always \
      -e PGID=1000 -e PUID=1000 \
      -p 5445:5445 \
      -v /some/folder/to/store/your/data:/data \
   bonny1992/sonarr-radarr-notification-aggregator:latest
   ```

   At the first run it will create the database and the config needed in the folder `/data` (I suggest you to mount it as a volume in the `docker run` command). Plus, at the very first start, it will generate a random string which you will need to access the "notificator webhook".

2. Then, I suggest you to stop the container so you can start editing the `config.yml` file needed.

   ```
   docker stop notificator 
   ```

   You can find it in your chosen folder during the container run (`/some/folder/to/store/your/data`).

   The `config.yml` explaination can be found [later](#config-file).

3. Now you can start the container again:
   
   ```
   docker start notificator
   ```

4. That's it, you can configure the webhook in Sonarr and Radarr with the url you will find in the `/some/folder/to/store/your/data` folder in the file `url.txt`.

# Config file

| Key | Content |
| ------- | ------- |
| skip_hours | Time between one notification and the next one (in hours) |
| discord_webhook | (Standard) Discord webhook (you can leave it empty to disable Discord notifications) |
| telegram_bot_token | Telegram bot token (Obtained from BotFather bot) |
| telegram_chat_id | Telegram chat id of where you want the notificator to sends messages to |
| safe_key | Safe key generated if empty or first run. You can however customize it how you please (I think, I did not try). |
| timezone | Your timezone, to customize log entries. Example: `Europe/London` |
| start_quiet | The `hour` where the quiet mode starts (if you want the quiet mode to start at 21 till 9, write here 21) |
| end_quiet | The `hour` where the quiet mode ends (if you want the quiet mode to start at 21 till 9, write here 8, as it counts till `8:59`) |
| domain | Your domain. Example: `notificator.domain.com`. The program will add the `https://` part, so you should reverse proxy this. |
| custom_quiet_mode_message | You can customize the header of the quiet mode message here. Example: `SILENT NOTIFICATION HERE!` (Works only with Telegram) |
| custom_tv_entry | Customizable TV episode entry. Available keys: `{SERIES}`, `{SEASON}`, `{EPISODE}`, `{TITLE}`, `{QUALITY}`, `{TIME}`. See below for explaination and examples. |
| custom_movie_entry | Customizable movie entry. Available keys: `{TITLE}`, `{YEAR}`, `{QUALITY}`, `{IMDB_LINK}`, `{TIME}`. See below for explaination and examples. |
| custom_too_long_message | Customizable message for when the message is too long (Max 4000 characters for Telegram and 2000 for Discord). Available keys: `{N_TV}`, `{N_MOVIE}`. See below for explaination and examples. |


## Custom TV entry keys

| Key | Content | Example |
| --- | --- | --- |
| `{SERIES}`  | Name of the series.                         | `Lucifer`                     |
| `{SEASON}`  | Two digit number of the season.             | `01`                          |
| `{EPISODE}` | Two digit number of the episode.            | `02`                          |
| `{TITLE}`   | Title of the episode.                       | `Lucifer, Stay. Good Devil.`  |
| `{QUALITY}` | Quality of the episode.                     | `HDTV-1080`                   |
| `{TIME}`    | Time (`hh:mm`) of the received notification | `08:30` |

Let's say we write a custom entry like this:
```
{TIME} - {SERIES} S{SEASON}E{EPISODE} - {TITLE} - {QUALITY}
```

Using the same examples as above, we get:
```
08:30 - Lucifer S01E02 - Lucifer, Stay. Good Devil. - HDTV-1080
```

You can also customize it with Markdown syntax (please refer to Telegram and Discord documentation).

## Custom movie entry keys

| Key | Content | Example |
| --- | --- | --- |
| `{TITLE}`       | Title of the movie.                         | `The Godfather` |
| `{YEAR}`        | Four digit number of the year of the release of the movie.           | `1972`  |
| `{QUALITY}`     | Quality of the movie release.               | `Blueray-1008p`   |
| `{IMDB_LINK}`   | Link to the movie IMDB page in Markdown syntax                       | `[IMDB Link](https://www.imdb.com/title/tt0068646/)`|
| `{TIME}`        | Time (`hh:mm`) of the received notification | `08:30` |

Let's say we write a custom entry like this:
```
{TIME} - {TITLE} ({YEAR}) - {QUALITY} - {IMDB_LINK}
```

Using the same examples as above, we get:
```
08:30 - The Godfather (1972) - Blueray-1008p - [IMDB Link](https://www.imdb.com/title/tt0068646/)
```
Which, will result like this, in Telegram and Discord:

08:30 - The Godfather (1972) - Blueray-1008p - [IMDB Link](https://www.imdb.com/title/tt0068646/)


You can also customize it with Markdown syntax (please refer to Telegram and Discord documentation).

# Install without Dockerfile
You can, however, install this without the use of Docker (though I did not test it, also I'm not an expert).

### Prerequisites
I'm assuming you will use Linux - I used Fedora Remix on Windows' WSL
- Python 3 (I used 3.8 but I believe any recent version of 3 would work)
- Pip
- Knowledge with systemd; or
- Tmux or similar software

### Steps

1. Clone this repository
   ```
   git clone https://github.com/bonny1992/sonarr-radarr-notification-aggregator.git ~/notificator
   ```
2. Go into the repository folder and in the `/app` folder
   ```
   cd ~/notificator/app
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Edit this line in `~/notificator/app/utils/__init__.py` file:
   ```
   DATA_PATH = '/data'
   ```
   with whatever folder you want (will be created on first start, be sure you have permissions to do that)
5. Now you will have to see how you want to start the programs, if as services or manually, for example with `tmux`

   - With systemd:
      - Sorry, not so much experience here, create two files to run `python ~/notificator/app/main.py` and `python ~/notificator/app/notifiator.py` for systemd; reload the daemon and enable them.
   - With tmux:
       1. Run `tmux new -s notificator_webhook`
       2. Run `python ~/notificator/app/main.py`
       3. Press your `detach` key combination (Default should be `CTRL + B then D`)
       4. Run `tmux new -s notificator_notify`
       5. Run `python ~/notificator/app/notificator.py`
       6. Press your `detach` key combination (Default should be `CTRL + B then D`)
       7. Enjoy!
       8. But not that much because you will have to redo this process everytime you reboot the system.

I ultimately suggest you to run this with Docker, or at the very least with systemd.

# Contribution
I have a very little experience with git or GitHub, as I use this majorly as a "cloud" for my (very crappy) code when I go from a PC to another.

So feel like to contribute as you like!

### Vagrant
I still haven't tested this with Vagrant, sorry.

# Final thoughs
I wrote this as I grew tired of the too many notifications I received when using Sonarr and Radarr, I hope you will find this useful too, even if it's not exactly polished or even... Good!




