import os
import json
import requests
import pandas as pd
import datetime
from google.oauth2.credentials import Credentials
import isodate

# Set up your API key here
Data_API_KEY = 'AIzaSyCWRFtlxzVZQVPFSCIdtYKaaBXEMaIZVE4'

# Set up your API key here
def load_csv(filename, columns=None):
    """
    Load data from a CSV file.

    Args:
        filename (str): The name of the file to load the data from.
        columns (list[str], optional): The list of column names for the DataFrame. Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing the loaded data.
    """
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            if columns:
                return pd.DataFrame(columns=columns)
            else:
                return pd.DataFrame()
    else:
        if columns:
            return pd.DataFrame(columns=columns)
        else:
            return pd.DataFrame()
channel_columns = [
    'channel_id', 'channel_title', 'description', 'published_at', 'thumbnail_url',
    'country', 'playlist_likes', 'playlist_uploads', 'view_count', 'subscriber_count',
    'video_count', 'topic_ids'
]
channel_stats_df = load_csv('channels.csv', columns=channel_columns)

video_columns = [
    'video_id', 'video_title', 'published_at', 'channel_id', 'channel_title', 'video_duration',
    'video_view_count', 'video_likes', 'video_dislikes', 'video_comments', 'video_category_id',
    'video_live_streaming'
]
video_stats_df = load_csv('videos.csv', columns=video_columns)

playlist_columns = [
    'playlist_id', 'playlist_title', 'published_at', 'video_count', 'playlist_duration'
]
playlist_stats_df = load_csv('playlists.csv', columns=playlist_columns)


def fetch_data(url):
    """
    Fetches data from a given URL using the GET method and returns it as JSON.

    Args:
        url (str): The URL to fetch data from.

    Returns:
        dict: The fetched data as a dictionary.

    Raises:
        Any exceptions that requests.get() or response.json() may raise.
    """
    response = requests.get(url)
    data = response.json()
    return data

def get_channel_id(channel_title):
    """
    Returns the YouTube channel ID associated with the given channel title.

    :param channel_title: A string representing the title of the desired channel.
    :type channel_title: str
    :return: A string representing the unique identifier of the channel.
    :rtype: str
    """
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&maxResults=5&q={channel_title}&key={Data_API_KEY}'
    data = fetch_data(url)

    for item in data.get('items', []):
        if item['snippet']['title'].lower() == channel_title.lower():
            return item['snippet']['channelId']

    return ''


def get_playlist_ids(channel_id, max_results):
    """
    Given a YouTube channel ID and maximum number of results, this function fetches the playlists associated with the channel and returns a list of their IDs.
    
    :param channel_id: The ID of the YouTube channel.
    :type channel_id: str
    :param max_results: The maximum number of playlists to fetch.
    :type max_results: int
    :return: A list of playlist IDs.
    :rtype: list[str]
    """
    url = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId={channel_id}&maxResults={max_results}&key={Data_API_KEY}'
    data = fetch_data(url)
    playlist_ids = [item['id'] for item in data['items']]
    return playlist_ids

def get_video_ids(channel_id, max_results):
    """
    Given a YouTube channel ID and a maximum number of results, returns a list of video IDs
    ordered by view count using the YouTube Data API.

    :param channel_id: A string representing the ID of the YouTube channel.
    :type channel_id: str
    :param max_results: An integer representing the maximum number of results to return.
    :type max_results: int
    :return: A list of video IDs ordered by view count.
    :rtype: list
    """
    url = f'https://www.googleapis.com/youtube/v3/search?part=id&type=video&order=viewCount&channelId={channel_id}&maxResults={max_results}&key={Data_API_KEY}'
    data = fetch_data(url)
    # Check if 'items' key exists in data dictionary
    if 'items' in data:
        video_ids = [item['id']['videoId'] for item in data['items']]
    else:
        video_ids = []

    return video_ids


def get_channel_statistics(channel_id):
    """
    Retrieves the statistics of a YouTube channel given its channel ID and returns a dictionary of the channel's statistics.
    
    Args:
        channel_id (str): The ID of the YouTube channel to retrieve statistics for.
        
    Returns:
        dict: A dictionary containing the following statistics for the specified channel:
            - channel_id (str): The ID of the channel.
            - channel_title (str): The title of the channel.
            - description (str): The description of the channel.
            - published_at (str): The date and time when the channel was created.
            - thumbnail_url (str): The URL of the channel's default thumbnail image.
            - country (str): The country in which the channel is based.
            - playlist_likes (str): The ID of the playlist containing the channel's liked videos.
            - playlist_uploads (str): The ID of the playlist containing the channel's uploaded videos.
            - view_count (int): The total number of views on the channel.
            - subscriber_count (int): The total number of subscribers to the channel.
            - video_count (int): The total number of videos uploaded to the channel.
            - topic_ids (list): A list of topic IDs that apply to the channel.
    """
    
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet,brandingSettings,contentDetails,topicDetails&id={channel_id}&key={Data_API_KEY}'
    data = fetch_data(url)
    channel_data = data['items'][0]
    
    if channel_id not in channel_stats_df['channel_id'].values:
        channel_stats = {
            'channel_id': channel_id,
            'channel_title': channel_data['snippet']['title'],
            'description': channel_data['snippet']['description'],
            'published_at': channel_data['snippet']['publishedAt'],
            'thumbnail_url': channel_data['snippet']['thumbnails']['default']['url'],
            'country': channel_data['snippet'].get('country', ''),
            # 'banner_image_url': channel_data['brandingSettings']['image'].get('bannerImageUrl', ''),
            'playlist_likes': channel_data['contentDetails']['relatedPlaylists']['likes'],
            'playlist_uploads': channel_data['contentDetails']['relatedPlaylists']['uploads'],
            'view_count': int(channel_data['statistics']['viewCount']),
            'subscriber_count': int(channel_data['statistics']['subscriberCount']),
            'video_count': int(channel_data['statistics']['videoCount']),
            'topic_ids': channel_data['topicDetails']['topicIds'] if 'topicDetails' in channel_data else []
        }
    else:
            print(f'Channel {channel_id} already exists in the database.')
            channel_stats={}
    return channel_stats


def get_video_statistics(channel_id, max_results):
    """
    Retrieves statistics for the latest videos uploaded by a given YouTube channel.
    
    Args:
        channel_id (str): The channel ID for the YouTube channel to retrieve statistics for.
        max_results (int): The maximum number of video statistics to retrieve.
        
    Returns:
        list: A list of dictionaries containing the statistics for each video. Each dictionary contains the following keys:
            - video_id (str): The ID of the video.
            - video_title (str): The title of the video.
            - published_at (str): The date and time the video was published.
            - channel_id (str): The ID of the channel that uploaded the video.
            - channel_title (str): The title of the channel that uploaded the video.
            - video_duration (str): The duration of the video.
            - video_view_count (int): The number of views the video has.
            - video_likes (int): The number of likes the video has.
            - video_dislikes (int): The number of dislikes the video has.
            - video_comments (int): The number of comments the video has.
            - video_category_id (str): The ID of the category the video belongs to.
            - video_live_streaming (dict): A dictionary containing information about the live streaming status of the video. The dictionary contains the following keys:
                - actual_start_time (str): The date and time the live stream started.
                - actual_end_time (str): The date and time the live stream ended.
                - scheduled_start_time (str): The date and time the live stream was scheduled to start.
                - scheduled_end_time (str): The date and time the live stream was scheduled to end.
                - concurrent_viewers (int): The number of viewers watching the live stream at the same time.
    """
    video_ids = get_video_ids(channel_id, max_results)
    video_stats_list = []

    for video_id in video_ids:
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics,liveStreamingDetails&id={video_id}&key={Data_API_KEY}'
        data = fetch_data(url)
        video_data = data['items'][0]
        if video_id not in video_stats_df['video_id'].values:
            video_stats = {
                'video_id': video_id,
                'video_title': video_data['snippet']['title'],
                # 'description': video_data['snippet']['description'],
                'published_at': video_data['snippet']['publishedAt'],
                # 'thumbnail_url': video_data['snippet']['thumbnails']['default']['url'],
                'channel_id': video_data['snippet']['channelId'],
                'channel_title': video_data['snippet']['channelTitle'],
                'video_duration': video_data['contentDetails']['duration'],
                # Modify the 'video_view_count' key in the video_stats dictionary in the get_video_statistics() function
                'video_view_count': int(video_data['statistics'].get('viewCount', 0)),
                'video_likes': int(video_data['statistics'].get('likeCount', 0)),
                'video_dislikes': int(video_data['statistics'].get('dislikeCount', 0)),
                'video_comments' : int(video_data['statistics'].get('commentCount', 0)),
                'video_category_id': video_data['snippet']['categoryId'],
                'video_live_streaming': {
                'actual_start_time': video_data['liveStreamingDetails']['actualStartTime'] if 'liveStreamingDetails' in video_data else None,
                'actual_end_time': video_data['liveStreamingDetails']['actualEndTime'] if 'liveStreamingDetails' in video_data else None,
                'scheduled_start_time': video_data['liveStreamingDetails']['scheduledStartTime'] if 'liveStreamingDetails' in video_data else None,
                'scheduled_end_time': video_data['liveStreamingDetails']['scheduledEndTime'] if 'liveStreamingDetails' in video_data else None,
                'concurrent_viewers': video_data['liveStreamingDetails']['concurrentViewers'] if 'liveStreamingDetails' in video_data else None
                }
            }
            video_stats_list.append(video_stats)
        else:
                print( f'Video ID {video_id} already exists in the database.')
                continue
    return video_stats_list
import isodate

def get_playlist_duration(playlist_id, api_key):
    next_page_token = None
    total_duration = 0

    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={api_key}&pageToken={next_page_token or ""}'
        data = fetch_data(url)

        video_ids = ','.join([item['contentDetails']['videoId'] for item in data['items']])
        video_url = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_ids}&key={api_key}'
        video_data = fetch_data(video_url)

        for item in video_data['items']:
            duration = item['contentDetails']['duration']
            duration_timedelta = isodate.parse_duration(duration)
            total_duration += duration_timedelta.total_seconds()

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return total_duration


def get_playlist_statistics(channel_id, max_results):
    """
    Retrieves statistics for a playlist given a YouTube channel ID and a maximum
    number of results to fetch.

    Args:
        channel_id (str): The ID of the YouTube channel containing the playlists.
        max_results (int): The maximum number of playlists to retrieve statistics for.

    Returns:
        list: A list of dictionaries containing statistics for each playlist. Each
        dictionary includes the playlist ID, title, published date, video count,
        and duration.
    """
    playlist_ids = get_playlist_ids(channel_id, max_results)
    playlist_stats_list = []

    for playlist_id in playlist_ids:
        url = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&id={playlist_id}&key={Data_API_KEY}'
        data = fetch_data(url)
        
        if 'items' not in data or len(data['items']) == 0:
            continue

        playlist_data = data['items'][0]
        if playlist_id not in playlist_stats_df['playlist_id'].values:
            playlist_stats = {
                'playlist_id': playlist_id,
                'playlist_title': playlist_data['snippet']['title'],
                # 'description': playlist_data['snippet']['description'],
                'published_at': playlist_data['snippet']['publishedAt'],
                # 'thumbnail_url': playlist_data['snippet']['thumbnails']['default']['url'],
                'video_count': playlist_data['contentDetails']['itemCount'],
                'playlist_duration': get_playlist_duration(playlist_id, Data_API_KEY)
            }
            playlist_stats_list.append(playlist_stats)
        else :
                print( f'Playlist ID {playlist_id} already exists in the database.')
                # Change this line to continue instead of assigning an empty dictionary
                continue
    return playlist_stats_list



def save_to_csv(data, filename):
    """
    Save data to a CSV file.

    Args:
        data (list or dict): The data to be saved.
        filename (str): The name of the file to save the data in.

    Returns:
        None
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    """
    Executes the main function which processes a list of YouTube channels represented by channel_titles.
    For each channel, it retrieves its ID using the get_channel_id function and uses it to get channel statistics,
    video statistics, and playlist statistics. The statistics are then stored in respective CSV files.
    If a channel ID is not found, the function logs a message and skips the channel.
    """
    channel_titles = [
        "MrBeast",
        "MrBeast Gaming",
        "Beast Reacts",
        "MrBeast 2",
        "PewDiePie",
        "Marques Brownlee",
        "xQc",
        "Billie Eilish"
    ]
    channel_stats_df = pd.DataFrame()
    video_stats_df = pd.DataFrame()
    playlist_stats_df = pd.DataFrame()

    for channel_title  in channel_titles:
        channel_id = get_channel_id(channel_title )
        if not channel_id:
            print(f"Channel '{channel_title}' not found. Skipping.")
            continue
        print(f"Processing channel '{channel_title}' with ID: {channel_id}")
        channel_stats = get_channel_statistics(channel_id)
        channel_videos = get_video_statistics(channel_id, 100)
        channel_playlists = get_playlist_statistics(channel_id, 25)
        print(f"- Channel Stats: {len(channel_stats)}")
        print(f"- Video Stats: {len(channel_videos)}")
        print(f"- Playlist Stats: {len(channel_playlists)}")

        if channel_stats:
            channel_stats_df = pd.DataFrame(channel_stats)  # Convert the list to a DataFrame
            channel_stats_df = pd.concat([channel_stats_df, channel_stats], ignore_index=True)
            channel_stats_df.to_csv('channels.csv', index=False)
        if channel_videos:
            channel_videos_df = pd.DataFrame(channel_videos)  # Convert the list to a DataFrame
            video_stats_df = pd.concat([video_stats_df, channel_videos_df], ignore_index=True)
            video_stats_df.to_csv('videos.csv', index=False)
        if channel_playlists:      
            channel_playlists_df = pd.DataFrame(channel_playlists)  # Convert the list to a DataFrame
            playlist_stats_df = pd.concat([playlist_stats_df, channel_playlists_df], ignore_index=True)
            playlist_stats_df.to_csv('playlists.csv', index=False)


        print(f"Finished processing channel '{channel_title}'\n")

if __name__ == '__main__':
    main()
