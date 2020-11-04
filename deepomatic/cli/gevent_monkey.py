import gevent.monkey
import gevent.os


patched = False
DEEPOMATIC_CLI_GEVENT_MONKEY_PATCH = gevent.os.getenv(
    'DEEPOMATIC_CLI_GEVENT_MONKEY_PATCH', '1'
)


def patch_all():
    global patched
    if not patched:
        if DEEPOMATIC_CLI_GEVENT_MONKEY_PATCH == '1':
            patched = gevent.monkey.patch_all(thread=False,
                                              time=False,
                                              subprocess=False)
    return patched
