import ssl
from string import ascii_lowercase
from random import choice
import urllib
import urllib2
import json
import time

# Default port that Spotify Web Helper binds to.
PORT = 4370
DEFAULT_RETURN_ON = ['login', 'logout', 'play', 'pause', 'error', 'ap']

# I had some troubles with the version of Spotify's SSL cert and Python 2.7 on Mac.
# Did this monkey dirty patch to fix it. Your milage may vary.
def new_wrap_socket(*args, **kwargs):
    kwargs['ssl_version'] = ssl.PROTOCOL_SSLv3
    return orig_wrap_socket(*args, **kwargs)

orig_wrap_socket, ssl.wrap_socket = ssl.wrap_socket, new_wrap_socket

def get_json(url, params={}, headers={}):
    if params:
        url += "?" + urllib.urlencode(params)
    request = urllib2.Request(url, headers=headers)
    request.add_header('Referer', 'https://open.spotify.com')
    return json.loads(urllib2.urlopen(request).read())


def generate_local_hostname():
    """Generate a random hostname under the .spotilocal.com domain"""
    return '127.0.0.1'
    subdomain = ''.join(choice(ascii_lowercase) for x in range(10))
    return subdomain + '.spotilocal.com'


def get_url(url):
    return "https://%s:%d%s" % (generate_local_hostname(), PORT, url)


def get_version():
    return get_json(get_url('/service/version.json'), params={'service': 'remote'})


def get_oauth_token():
    return get_json('http://open.spotify.com/token')['t']


def get_csrf_token():
    # Requires Origin header to be set to generate the CSRF token.
    headers = {'Origin': 'https://open.spotify.com'}
    return get_json(get_url('/simplecsrf/token.json'), headers=headers)['token']


def get_status(oauth_token, csrf_token, return_after=59, return_on=DEFAULT_RETURN_ON):
    params = {
        'oauth': oauth_token,
        'csrf': csrf_token,
        'returnafter': return_after,
        'returnon': ','.join(return_on)
    }
    return get_json(get_url('/remote/status.json'), params=params)


def pause(oauth_token, csrf_token, pause=True):
    params = {
        'oauth': oauth_token,
        'csrf': csrf_token,
        'pause': 'true' if pause else 'false'
    }
    get_json(get_url('/remote/pause.json'), params=params)


def unpause(oauth_token, csrf_token):
    pause(oauth_token, csrf_token, pause=False)


def play(oauth_token, csrf_token, spotify_uri):
    params = {
        'oauth': oauth_token,
        'csrf': csrf_token,
        'uri': spotify_uri,
        'context': spotify_uri,
    }
    get_json(get_url('/remote/play.json'), params=params)


def open_spotify_client():
    headers = {'Origin': 'https://open.spotify.com'}
    return get(get_url('/remote/open.json'), headers=headers).text


if __name__ == '__main__':
    oauth_token = get_oauth_token()
    csrf_token = get_csrf_token()

    # print "Playing album.."
    # play(oauth_token, csrf_token, 'spotify:album:6eWtdQm0hSlTgpkbw4LaBG')
    # time.sleep(5)
    print "Pausing song.."
    pause(oauth_token, csrf_token)
    time.sleep(2)
    print "Unpausing song.."
    unpause(oauth_token, csrf_token)
