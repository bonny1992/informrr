import time

def aprint(msg, source='MAIN'):
    now = time.ctime()
    message = '{TIME}\t| {SOURCE:<13} |\t\t{MSG}'
    print(message.format(
        TIME = now,
        SOURCE = source,
        MSG = msg
    ))