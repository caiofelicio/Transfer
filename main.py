import spotipy
import spotipy.util as util
import os, sys
from copy import deepcopy
from datetime import datetime
from dotenv import dotenv_values


keys = dotenv_values(dotenv_path=".env")

CLI_ID_ACCOUNT_1 = keys["CLI_ID_ACCOUNT_1"]
CLI_SECRET_ACCOUNT_1 = keys["CLI_SECRET_ACCOUNT_1"]
REDIRECT_URI_1 = keys["REDIRECT_URI_1"]
# =================================================================
CLI_ID_ACCOUNT_2 = keys["CLI_ID_ACCOUNT_2"]
CLI_SECRET_ACCOUNT_2 = keys["CLI_SECRET_ACCOUNT_2"]
REDIRECT_URI_2 = keys["REDIRECT_URI_2"]
# =================================================================
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-library-modify user-library-read"

COMMAND = "clear" if sys.platform == "linux" else "cls"

class Spotify():
    def __init__(self):
        token1 = util.prompt_for_user_token(
            client_id=CLI_ID_ACCOUNT_1,
            client_secret=CLI_SECRET_ACCOUNT_1,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI_1,
            cache_path="cache"
        )

        token2 = util.prompt_for_user_token(

            client_id=CLI_ID_ACCOUNT_2,
            client_secret=CLI_SECRET_ACCOUNT_2,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI_2,
            cache_path="cache-2"
        )

        if token1 and token2:
            self.user1 = spotipy.Spotify(token1)
            self.user2 = spotipy.Spotify(token2)

    def main(self):
        os.system(COMMAND)
        
        print(f"Hora de Inicio: {datetime.now().strftime('%H:%M:%S')}")

        pls = self.getMyPlaylistsAndFollowedPlaylists()
        tracksAndNames = self.getTracksFromPlaylists(pls[0])
        self.createPlaylist(tracksAndNames)
        
        print(f"Hora de Término: {datetime.now().strftime('%H:%M:%S')}")
        
    def getMyPlaylistsAndFollowedPlaylists(self):
        myPLaylists = []
        followedPlaylists = []

        name = self.user1.me()["display_name"]
        pls = self.user1.current_user_playlists()
        
        for i in range(len(pls["items"])):
            if pls["items"][i]["owner"]["display_name"] == name:
                myPLaylists.append(pls["items"][i]["id"])
            else:
                followedPlaylists.append(pls["items"][i]["id"])
        
        pls = self.user1.current_user_playlists(offset=50+1)
        
        for i in range(len(pls["items"])):
            if pls["items"][i]["owner"]["display_name"] == name:
                myPLaylists.append(pls["items"][i]["id"])
            else:
                followedPlaylists.append(pls["items"][i]["id"])
            
        
        pls = self.user1.current_user_playlists(offset=100+1)
        
        for i in range(len(pls["items"])):
            if pls["items"][i]["owner"]["display_name"] == name:
                myPLaylists.append(pls["items"][i]["id"])
            else:
                followedPlaylists.append(pls["items"][i]["id"])
            

        return (myPLaylists, followedPlaylists)

    def getTracksFromPlaylists(self, playlists=list):
        
        tracksAndNames = {}
        trackIds = []
        i = len(playlists) - 1
        print("\n")
        while i >= 0:
            currentPlaylistsName = self.user1.playlist(playlists[i])["name"]
            total = self.user1.playlist(playlists[i])["tracks"]["total"]
    
            print(f"Buscando dados da playlist {currentPlaylistsName}\nTotal de Musicas: {total}\n")
    
            try:
                for j in range(0, total):
                    trackIds.append(self.user1.playlist_tracks(playlists[i], limit=1, offset=j)["items"][0]["track"]["id"])
            except Exception as erro:
                pass
            
            tracksAndNames[currentPlaylistsName] = deepcopy(trackIds)
            trackIds.clear()
            i -= 1

        return tracksAndNames

    def createPlaylist(self, playlists):

        print("\n=================================\n\nCriando PLaylists\n\n")

        nPls = 0
        nMusics = 0

        me = self.user2.me()["id"]
        for name, ids in playlists.items():
            currentPlaylistId = self.user2.user_playlist_create(user=me, name=name, public=False)["id"]
            nPls += 1
            while ids:
                try:
                    self.user2.user_playlist_add_tracks(user=me, playlist_id=currentPlaylistId, tracks=ids[:1])
                    ids = ids[1:]
                except Exception:
                    pass
                else:
                    nMusics += 1
        
        print(f"\nNumero de playlists criadas: {nPls}\nTotal de Musicas adicionadas: {nMusics}\n")

    def followPlaylists(self, ids):
        print("Seguindo playlists")
        i = len(ids) - 1
        while i >= 0:
            self.user2.current_user_follow_playlist(ids[i])
            i -= 1

run = Spotify()
run.main()
