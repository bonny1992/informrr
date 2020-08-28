import time

def aprint(msg, source='MAIN'):
    now = time.ctime()
    message = '{SOURCE}\t\t| {TIME} |\t\t{MSG}'
    print(message.format(
        SOURCE = source,
        MSG = msg,
        TIME = now
    ))