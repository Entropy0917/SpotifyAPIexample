from flask import Flask, session, url_for, request, redirect
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)

client_id = '' # make your own in spotify with Spotify Web API
client_secret = '' # make your own in spotify with Spotify Web API
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = 'playlist-read-private, user-top-read'

cache_handler = FlaskSessionCacheHandler(session)
sp_auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(oauth_manager=sp_auth)


@app.route('/')
def home():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_auth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_artists'))


@app.route('/callback')
def callback():
    sp_auth.get_access_token(request.args['code'])
    return redirect(url_for('get_artists'))


@app.route('/get_playlists')
def get_playlists():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_auth.get_authorize_url()
        return redirect(auth_url)

    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join(f'{name}: {url}' for name, url in playlists_info)

    return playlists_html


@app.route('/get_artists')
def get_artists():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_auth.get_authorize_url()
        return redirect(auth_url)

    artists = sp.current_user_top_artists(time_range='short_term', limit=50)
    artists_info = [(ar['name'], ar['popularity'], ar['genres'], ar['followers']['total']) for ar in artists['items']]
    artists_html = '<br>'.join(f'{name}: {pop}, {genre}, followers: {followers}' for name, pop, genre, followers in artists_info)

    return artists_html


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


app.run(debug=True)
