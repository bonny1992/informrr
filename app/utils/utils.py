import time

def aprint(msg, source='MAIN'):
    now = time.strftime('%l:%M%p %z on %b %d, %Y')
    message = '{SOURCE}\t| {TIME} |\t{MSG}'
    print(message.format(
        SOURCE = source,
        MSG = msg,
        TIME = now
    ))