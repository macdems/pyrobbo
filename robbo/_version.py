import os
from subprocess import Popen, PIPE

# Find current version form environment or git

__version__ = os.environ.get('PYROBBO_VERSION')

if not __version__:
    try:
        p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE, encoding='utf8')
        p.stderr.close()
        __version__ = p.stdout.read().strip()
        if '-' in __version__:
            ver, rev, git = __version__.split('-')
            __version__ = "{}+git{}.{}".format(ver, rev, git)
        if __version__.startswith('v'):
            __version__ = __version__[1:]
    except:
        __version__ = '0.0.0'
