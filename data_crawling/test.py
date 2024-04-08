import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
 
cid = 'ecd654ce83084fad9d37d9f05bb169e8'
secret = '31142deadb7e4300901f2179ea5c7429'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
 
result = sp.search("Closer Fabiana Palladino", limit=10, type="track")
pprint.pprint(result['tracks']['items'][0]['name'])
pprint.pprint(result['tracks']['items'][0]['artists'][0]['name'])
pprint.pprint(result['tracks']['items'][0]['album']['images'][0]['url'])