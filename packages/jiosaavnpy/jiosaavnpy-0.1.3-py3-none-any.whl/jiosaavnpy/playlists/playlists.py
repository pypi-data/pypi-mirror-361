from typing import Optional, List, Dict, TypedDict
import html


class ThumbnailDict(TypedDict):
    quality: Dict[str, str]


class PlaylistDict(TypedDict, total=False):
    playlist_id: str
    title: str
    subtitle: str
    playlist_url: str
    thumbnails: ThumbnailDict
    track_count: str
    is_explicit: bool
    playlist_language: str
    playlist_followers: str
    playlist_type: str
    tracks: List[dict]


class Playlists:
    def search_playlists(self, search_query: str, limit: Optional[int] = None) -> List[PlaylistDict]:
        """
            Search for playlists on JioSaavn.

            Args:
                search_query: Playlist name or keywords.
                limit: Max number of results to return (default: 5).

            Returns:
                A list of PlaylistDict objects matching the query.
        """
        
        if limit is None:
            limit = 5  ## Default to 5 results.
        SEARCH_URL = self.endpoints.SEARCH_PLAYLISTS_URL.replace("&n=20", f"&n={limit}")
        response = self.requests.get(SEARCH_URL + search_query).json()
        return [self.format_json_search_playlists(p) for p in response.get("results", [])]

    def playlist_info(self, playlist_id: str) -> PlaylistDict:
        """
            Get detailed info for a specific playlist.

            Args:
                playlist_id: The JioSaavn playlist ID.
                Example: `386221272`

            Returns:
                A PlaylistDict containing playlist metadata and track list.
        """
    
        response = self.requests.get(self.endpoints.PLAYLIST_DETAILS_URL + playlist_id).json()
        return self.format_json_info_playlists(response)

    def format_json_search_playlists(self, playlist_json: dict) -> PlaylistDict:
        playlist: PlaylistDict = {
            'playlist_id': playlist_json.get('id', ''),
            'title': html.unescape(playlist_json.get('title', '')),
            'subtitle': playlist_json.get('subtitle', ''),
            'playlist_url': playlist_json.get('perma_url', ''),
            'thumbnails': self._format_thumbnails(playlist_json.get('image', '')),
            'track_count': playlist_json.get('more_info', {}).get('song_count', '0'),
            'is_explicit': self.is_explicit(playlist_json.get('explicit_content', 0)),
            'playlist_language': playlist_json.get('more_info', {}).get('language', '')
        }
        return playlist

    def format_json_info_playlists(self, playlist_json: dict) -> PlaylistDict:
        playlist: PlaylistDict = {
            'playlist_id': playlist_json.get('listid', ''),
            'title': playlist_json.get('listname', ''),
            'playlist_followers': playlist_json.get('follower_count', '0'),
            'playlist_url': playlist_json.get('perma_url', ''),
            'playlist_type': playlist_json.get('type', ''),
            'thumbnails': self._format_thumbnails(playlist_json.get('image', '')),
            'track_count': playlist_json.get('list_count', '0'),
            'tracks': [self.song_info(i) for i in playlist_json.get('content_list', [])]
        }
        return playlist

    def _format_thumbnails(self, image_url: str) -> ThumbnailDict:
        return {
            'quality': {
                '50x50': image_url.replace("150x150", "50x50"),
                '150x150': image_url,
                '500x500': image_url.replace("150x150", "500x500")
            }
        }