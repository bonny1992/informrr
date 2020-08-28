import time

def aprint(msg, source='MAIN'):
    now = time.ctime()
    message = '{TIME}\t\t| {SOURCE} |\t\t{MSG}'
    print(message.format(
        TIME = now,
        SOURCE = source,
        MSG = msg
    ))