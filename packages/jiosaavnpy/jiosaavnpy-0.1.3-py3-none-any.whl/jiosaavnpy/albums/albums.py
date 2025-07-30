from typing import Optional, List, Dict, TypedDict
import html

class ThumbnailDict(TypedDict):
    quality: Dict[str, str]

class AlbumSearchDict(TypedDict):
    album_id: str
    title: str
    artists: str
    artists_ids: str
    artists_urls: str
    track_count: str
    album_url: str
    thumbnails: ThumbnailDict
    release_year: str
    album_language: str
    is_explicit: bool
    
class AlbumArtistDict(TypedDict):
    album_id: str
    title: str
    primary_artists: str
    primary_artists_id: str
    track_count: str
    album_url: str
    thumbnails: ThumbnailDict
    release_year: str
    album_language: str
    is_explicit: bool

class AlbumDetailDict(TypedDict):
    album_id: str
    title: str
    primary_artists: str
    primary_artists_id: str
    album_url: str
    thumbnails: ThumbnailDict
    release_date: str
    tracks: List[dict]  # Stays generic unless track type is structured too

class Albums:
    def search_albums(self, search_query: str, limit: Optional[int] = None) -> List[AlbumSearchDict]:
        """
            Search for albums on JioSaavn.

        Args:
                search_query: The album name or keywords.
                limit: Max number of results to return (default: 5).

            Returns:
                A list of AlbumSearchDict objects matching the query.
            """
    
        if limit is None:
            limit = 5  ## Default to 5 results.
        SEARCH_URL = self.endpoints.SEARCH_ALBUMS_URL.replace("&n=20", f"&n={limit}")
        response = self.requests.get(SEARCH_URL + search_query).json()
        return [self.format_json_search_albums(i) for i in response.get('results', [])]

    def album_info(self, album_id: str) -> AlbumDetailDict:
        """
            Get detailed info for a specific album.

            Args:
                album_id: The JioSaavn album ID.
                Example: `10061198`

            Returns:
                An AlbumDetailDict with full album metadata and tracks.
            """
            
        response = self.requests.get(self.endpoints.ALBUM_DETAILS_URL + album_id).json()
        return self.format_json_info_albums(response)

    def format_json_search_albums(self, album_json: dict) -> AlbumSearchDict:
        artists_location = album_json['more_info']['artistMap']['artists']
        image = album_json['image']
        return {
            'album_id': album_json['id'],
            'title': html.unescape(album_json['title']),
            'artists': self.get_primary_artists(artists_location),
            'artists_ids': self.get_primary_artists_ids(artists_location),
            'artists_urls': self.get_primary_artists_urls(artists_location),
            'track_count': album_json['more_info']['song_count'],
            'album_url': album_json['perma_url'],
            'thumbnails': {
                'quality': {
                    '50x50': image.replace("150x150", "50x50"),
                    '150x150': image,
                    '500x500': image.replace("150x150", "500x500")
                }
            },
            'release_year': album_json['year'],
            'album_language': album_json['language'],
            'is_explicit': self.is_explicit(album_json['explicit_content'])
        }

    def format_json_info_albums(self, album_json: dict) -> AlbumDetailDict:
        image = album_json['image']
        tracks = [self.format_json_info_songs(i) for i in album_json.get('songs', [])]
        return {
            'album_id': album_json['albumid'],
            'title': html.unescape(album_json['title']),
            'primary_artists': album_json['primary_artists'],
            'primary_artists_id': album_json['primary_artists_id'],
            'album_url': album_json['perma_url'],
            'thumbnails': {
                'quality': {
                    '50x50': image.replace("150x150", "50x50"),
                    '150x150': image,
                    '500x500': image.replace("150x150", "500x500")
                }
            },
            'release_date': album_json['release_date'],
            'tracks': tracks
        }
        
    def format_json_artists_albums(self, artist_json: dict) -> AlbumArtistDict:
        image = artist_json['imageUrl']
        return {
            'album_id': artist_json['albumid'],
            'title': html.unescape(artist_json['album']),
            'primary_artists': artist_json['primaryArtists'],
            'primary_artists_ids': artist_json['primaryArtistsIds'],
            'track_count': artist_json['numSongs'],
            'album_url': artist_json['url'],
            'thumbnails': {
                'quality': {
                    '50x50': image.replace("150x150", "50x50"),
                    '150x150': image,
                    '500x500': image.replace("150x150", "500x500")
                }
            },
            'release_year': artist_json['year'],
            'album_language': artist_json['language'],
            'is_explicit': self.is_explicit(artist_json['explicitContent'])
        }