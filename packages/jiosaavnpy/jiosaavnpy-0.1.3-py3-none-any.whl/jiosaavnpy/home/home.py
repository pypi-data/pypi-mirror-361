from typing import Optional, List, Dict, TypedDict
import html

class HomeDict(TypedDict, total=False):
    trending_tracks: Dict[str, str]
    top_playlists: Dict[str, str]
    new_albums: Dict[str, str]
    top_charts: Dict[str, str]
    
class Home:
    def get_home(self, language: str) -> dict:
        """
            Returns JioSaavn home page data such as new trending, top playlists and charts.

            Args:
                language: The language to return home data in.
                Example: `english`, `tamil` (Case Sensitive!)

            Returns:
                A list of HomeDict objects matching the query.
        """
        HOME_URL = self.endpoints.HOME_DETAILS_URL
        headers = {'Cookie': f'L={language};'}
        response = self.requests.get(HOME_URL, headers=headers).json()
        result = self.format_json_home(response)
        return result
    
    def format_json_home(self, home_json: dict) -> HomeDict:
        home = {}
        trending_media = []
        top_playlists = []
        new_albums = []
        charts = []
        
        for i in home_json['new_trending']:
            if i['type'] == "song":
                trending_media.append(self.format_json_search_songs(i))
            elif i['type'] == "album":
                trending_media.append(self.format_json_search_albums(i))
            elif i['type'] == "playlist":
                trending_media.append(self.format_json_search_playlists(i))
        
        for i in home_json['top_playlists']:
            top_playlists.append(self.format_json_search_playlists(i))
            
        for i in home_json['new_albums']:
            if i['type'] == "album":
                new_albums.append(self.format_json_search_albums(i))
            elif i['type'] == "song":
                new_albums.append(self.format_json_search_songs(i))
                
        for i in home_json['charts']:
            charts.append(self.format_json_search_playlists(i))
        
        home['now_trending'] = trending_media
        home['top_playlists'] = top_playlists
        home['new_albums'] = new_albums
        home['top_charts'] = charts
        return home