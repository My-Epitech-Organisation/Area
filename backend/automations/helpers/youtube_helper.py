##
## EPITECH PROJECT, 2025
## Area
## File description:
## youtube_helper
##

"""YouTube Data API v3 helper functions for actions and reactions."""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def get_youtube_service(access_token: str):
    """
    Build YouTube Data API v3 service from access token.

    Args:
        access_token: Valid Google OAuth2 access token with YouTube scopes

    Returns:
        YouTube API service resource
    """
    creds = Credentials(token=access_token)
    return build("youtube", "v3", credentials=creds)


def get_latest_videos(
    access_token: str,
    channel_id: str,
    max_results: int = 10,
    published_after: Optional[str] = None,
) -> List[Dict]:
    """
    Get latest videos from a YouTube channel.

    Args:
        access_token: Valid Google OAuth token
        channel_id: YouTube channel ID (e.g., 'UC_x5XG1OV2P6uZZ5FSM9Ttw')
        max_results: Max videos to return (default: 10, max: 50)
        published_after: ISO 8601 timestamp to filter videos (e.g., '2024-01-01T00:00:00Z')

    Returns:
        List of video dicts with id, title, description, publishedAt, thumbnails

    Raises:
        HttpError: If YouTube API request fails
    """
    try:
        service = get_youtube_service(access_token)

        # Build search parameters
        search_params = {
            "part": "id,snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": min(max_results, 50),
        }

        if published_after:
            search_params["publishedAfter"] = published_after

        # Execute search
        results = service.search().list(**search_params).execute()

        videos = []
        for item in results.get("items", []):
            video_data = {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
                "thumbnail_url": item["snippet"]["thumbnails"]["default"]["url"],
            }
            videos.append(video_data)

        logger.info(
            f"Found {len(videos)} videos for channel {channel_id} "
            f"(published_after={published_after})"
        )
        return videos

    except HttpError as e:
        logger.error(f"YouTube get_latest_videos failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_latest_videos: {e}")
        raise


def get_channel_statistics(access_token: str, channel_id: str) -> Dict:
    """
    Get channel statistics (subscribers, views, video count).

    Args:
        access_token: Valid Google OAuth token
        channel_id: YouTube channel ID

    Returns:
        Dict with channel stats:
        - subscriber_count: Total subscribers
        - view_count: Total channel views
        - video_count: Total videos uploaded

    Raises:
        HttpError: If YouTube API request fails
    """
    try:
        service = get_youtube_service(access_token)

        results = (
            service.channels()
            .list(part="statistics", id=channel_id)
            .execute()
        )

        if not results.get("items"):
            logger.warning(f"Channel not found: {channel_id}")
            return {}

        stats = results["items"][0]["statistics"]
        channel_stats = {
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        }

        logger.info(f"Channel {channel_id} stats: {channel_stats}")
        return channel_stats

    except HttpError as e:
        logger.error(f"YouTube get_channel_statistics failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_statistics: {e}")
        raise


def search_videos(
    access_token: str,
    query: str,
    max_results: int = 10,
    channel_id: Optional[str] = None,
    published_after: Optional[str] = None,
) -> List[Dict]:
    """
    Search for videos matching query.

    Args:
        access_token: Valid Google OAuth token
        query: Search keywords
        max_results: Max videos to return (default: 10, max: 50)
        channel_id: Optional channel ID to limit search
        published_after: ISO 8601 timestamp to filter videos

    Returns:
        List of video dicts with id, title, description, publishedAt

    Raises:
        HttpError: If YouTube API request fails
    """
    try:
        service = get_youtube_service(access_token)

        # Build search parameters
        search_params = {
            "part": "id,snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "maxResults": min(max_results, 50),
        }

        if channel_id:
            search_params["channelId"] = channel_id
        if published_after:
            search_params["publishedAfter"] = published_after

        # Execute search
        results = service.search().list(**search_params).execute()

        videos = []
        for item in results.get("items", []):
            video_data = {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
                "thumbnail_url": item["snippet"]["thumbnails"]["default"]["url"],
            }
            videos.append(video_data)

        logger.info(f"Found {len(videos)} videos for query: '{query}'")
        return videos

    except HttpError as e:
        logger.error(f"YouTube search_videos failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_videos: {e}")
        raise


def post_comment(
    access_token: str, video_id: str, comment_text: str
) -> Dict:
    """
    Post a comment on a YouTube video.

    Args:
        access_token: Valid Google OAuth token with force-ssl scope
        video_id: YouTube video ID
        comment_text: Text content of the comment

    Returns:
        Dict with comment details (id, text, published_at)

    Raises:
        HttpError: If YouTube API request fails
    """
    try:
        service = get_youtube_service(access_token)

        # Build comment resource
        comment_resource = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }

        # Insert comment
        result = (
            service.commentThreads()
            .insert(part="snippet", body=comment_resource)
            .execute()
        )

        comment_data = {
            "comment_id": result["id"],
            "text": result["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
            "published_at": result["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
            "video_id": video_id,
        }

        logger.info(f"Posted comment on video {video_id}: {comment_data['comment_id']}")
        return comment_data

    except HttpError as e:
        logger.error(f"YouTube post_comment failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in post_comment: {e}")
        raise


def add_video_to_playlist(
    access_token: str, video_id: str, playlist_id: str
) -> Dict:
    """
    Add a video to a YouTube playlist.

    Args:
        access_token: Valid Google OAuth token with force-ssl scope
        video_id: YouTube video ID
        playlist_id: YouTube playlist ID

    Returns:
        Dict with playlist item details (id, position)

    Raises:
        HttpError: If YouTube API request fails
    """
    try:
        service = get_youtube_service(access_token)

        # Build playlist item resource
        playlist_item = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

        # Insert playlist item
        result = (
            service.playlistItems()
            .insert(part="snippet", body=playlist_item)
            .execute()
        )

        item_data = {
            "playlist_item_id": result["id"],
            "video_id": video_id,
            "playlist_id": playlist_id,
            "position": result["snippet"]["position"],
        }

        logger.info(
            f"Added video {video_id} to playlist {playlist_id} at position {item_data['position']}"
        )
        return item_data

    except HttpError as e:
        logger.error(f"YouTube add_video_to_playlist failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_video_to_playlist: {e}")
        raise


def rate_video(access_token: str, video_id: str, rating: str) -> bool:
    """
    Rate a YouTube video (like, dislike, or remove rating).

    Args:
        access_token: Valid Google OAuth token with force-ssl scope
        video_id: YouTube video ID
        rating: Rating type ('like', 'dislike', or 'none' to remove rating)

    Returns:
        True if rating was successful

    Raises:
        HttpError: If YouTube API request fails
        ValueError: If rating is not 'like', 'dislike', or 'none'
    """
    if rating not in ["like", "dislike", "none"]:
        raise ValueError(f"Invalid rating: {rating}. Must be 'like', 'dislike', or 'none'")

    try:
        service = get_youtube_service(access_token)

        # Rate the video
        service.videos().rate(id=video_id, rating=rating).execute()

        logger.info(f"Rated video {video_id} as '{rating}'")
        return True

    except HttpError as e:
        logger.error(f"YouTube rate_video failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in rate_video: {e}")
        raise


def parse_atom_feed_entry(xml_string: str) -> Optional[Dict]:
    """
    Parse YouTube PubSubHubbub Atom feed XML into structured data.

    Args:
        xml_string: Raw XML string from YouTube PubSubHubbub notification

    Returns:
        Dict with video details (video_id, title, channel_id, published_at, etc.)
        None if parsing fails
    """
    try:

        # Parse XML
        root = ET.fromstring(xml_string)

        # Atom namespace
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015'
        }

        # Find entry element
        entry = root.find('atom:entry', ns)
        if entry is None:
            logger.warning("No entry element found in Atom feed")
            return None

        # Extract video ID
        video_id_elem = entry.find('yt:videoId', ns)
        video_id = video_id_elem.text if video_id_elem is not None else ""

        # Extract title
        title_elem = entry.find('atom:title', ns)
        title = title_elem.text if title_elem is not None else ""

        # Extract channel ID
        channel_id_elem = entry.find('yt:channelId', ns)
        channel_id = channel_id_elem.text if channel_id_elem is not None else ""

        # Extract author/channel name
        author_elem = entry.find('atom:author/atom:name', ns)
        channel_title = author_elem.text if author_elem is not None else ""

        # Extract published date
        published_elem = entry.find('atom:published', ns)
        published_at = published_elem.text if published_elem is not None else ""

        # Extract updated date
        updated_elem = entry.find('atom:updated', ns)
        updated_at = updated_elem.text if updated_elem is not None else ""

        # Extract link
        link_elem = entry.find('atom:link[@rel="alternate"]', ns)
        link = link_elem.get('href', '') if link_elem is not None else ""

        # Extract thumbnail (media:group/media:thumbnail)
        thumbnail_url = ""
        try:
            media_ns = {'media': 'http://search.yahoo.com/mrss/'}
            thumbnail_elem = entry.find('.//media:thumbnail', media_ns)
            if thumbnail_elem is not None:
                thumbnail_url = thumbnail_elem.get('url', '')
        except:
            pass

        video_data = {
            "video_id": video_id,
            "title": title,
            "channel_id": channel_id,
            "channel_title": channel_title,
            "published_at": published_at,
            "updated_at": updated_at,
            "link": link,
            "thumbnail_url": thumbnail_url,
        }

        logger.debug(f"Parsed Atom feed entry: video_id={video_id}, title={title}")
        return video_data

    except ET.ParseError as e:
        logger.error(f"Failed to parse Atom feed XML: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing Atom feed: {e}", exc_info=True)
        return None
