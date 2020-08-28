import sys, yaml
from pathlib import Path

config_file = Path('/data/config.yml')

if not config_file.is_file():
    sys.exit('Please compile /data/config.yml file')

with open('/data/config.yml', 'r') as opened:
    CONFIG = yaml.load(opened, Loader=yaml.SafeLoader)

if CONFIG['telegram_bot_token'] == None:
    sys.exit('Please compile /data/config.yml file')

print('URLs:', flush=True)
print('https://' + CONFIG['domain'] + '/' + CONFIG['safe_key'] + '/sonarr', flush=True)
print('https://' + CONFIG['domain'] + '/' + CONFIG['safe_key'] + '/radarr', flush=True)