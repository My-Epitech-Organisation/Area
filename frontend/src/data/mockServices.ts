/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** mockServices
 */

import type { Service } from '../types';

export const mockServices: Service[] = [
  {
    name: 'Facebook',
    actions: [
      { name: 'new_message_in_group', description: 'A new message is posted in a group' },
      { name: 'new_like', description: 'The user gains a like' },
      { name: 'new_comment', description: 'A new comment is posted on your post' },
    ],
    reactions: [
      { name: 'like_message', description: 'The user likes a message' },
      { name: 'post_status', description: 'Post a status on your wall' },
    ],
  },
  {
    name: 'Gmail',
    actions: [
      { name: 'email_received', description: 'A new email is received' },
      { name: 'email_from_contact', description: 'Email received from a specific contact' },
    ],
    reactions: [
      { name: 'send_email', description: 'Send an email to a user' },
      { name: 'archive_email', description: 'Archive an email automatically' },
    ],
  },
  {
    name: 'Google Drive',
    actions: [
      { name: 'new_file_uploaded', description: 'A new file is uploaded to a folder' },
      { name: 'file_shared', description: 'A file has been shared with you' },
    ],
    reactions: [
      { name: 'create_folder', description: 'Create a new folder' },
      { name: 'share_file', description: 'Share a file with a specific user' },
    ],
  },
  {
    name: 'GitHub',
    actions: [
      { name: 'new_issue', description: 'A new issue is created' },
      { name: 'new_pull_request', description: 'A new pull request is opened' },
    ],
    reactions: [
      { name: 'comment_issue', description: 'Add a comment to an issue' },
      { name: 'assign_issue', description: 'Assign an issue to a team member' },
    ],
  },
  {
    name: 'Slack',
    actions: [
      { name: 'new_message', description: 'A new message is posted in a channel' },
      { name: 'new_mention', description: 'You are mentioned in a message' },
    ],
    reactions: [
      { name: 'send_message', description: 'Send a message to a channel' },
      { name: 'add_reaction', description: 'Add an emoji reaction to a message' },
    ],
  },
  {
    name: 'Dropbox',
    actions: [
      { name: 'file_added', description: 'A new file is added to a folder' },
      { name: 'file_deleted', description: 'A file is deleted' },
    ],
    reactions: [
      { name: 'upload_file', description: 'Upload a file to Dropbox' },
      { name: 'share_link', description: 'Generate a shareable link' },
    ],
  },
  {
    name: 'Spotify',
    actions: [
      { name: 'new_song_added', description: 'A new song is added to a playlist' },
      { name: 'song_played', description: 'A specific song starts playing' },
    ],
    reactions: [
      { name: 'add_to_playlist', description: 'Add a song to a playlist' },
      { name: 'start_playback', description: 'Start playback on your device' },
    ],
  },
  {
    name: 'Twitter (X)',
    actions: [
      { name: 'new_tweet', description: 'A new tweet is posted' },
      { name: 'new_follower', description: 'You gain a new follower' },
    ],
    reactions: [
      { name: 'post_tweet', description: 'Post a new tweet' },
      { name: 'retweet', description: 'Retweet a specific tweet' },
    ],
  },
  {
    name: 'Discord',
    actions: [
      { name: 'new_message', description: 'A new message is sent in a channel' },
      { name: 'user_joined', description: 'A new user joins the server' },
    ],
    reactions: [
      { name: 'send_dm', description: 'Send a DM to a user' },
      { name: 'post_in_channel', description: 'Send a message in a specific channel' },
    ],
  },
  {
    name: 'Trello',
    actions: [
      { name: 'new_card', description: 'A new card is added to a board' },
      { name: 'card_moved', description: 'A card is moved to another list' },
    ],
    reactions: [
      { name: 'create_card', description: 'Create a new Trello card' },
      { name: 'update_card', description: 'Update a card’s description' },
    ],
  },
  {
    name: 'Notion',
    actions: [
      { name: 'page_created', description: 'A new page is created' },
      { name: 'page_edited', description: 'A page is updated' },
    ],
    reactions: [
      { name: 'add_block', description: 'Add a text block to a page' },
      { name: 'update_property', description: 'Modify a property in a database' },
    ],
  },
  {
    name: 'Outlook 365',
    actions: [
      { name: 'meeting_created', description: 'A meeting is scheduled' },
      { name: 'email_received', description: 'A new email is received' },
    ],
    reactions: [
      { name: 'send_email', description: 'Send a new email' },
      { name: 'add_calendar_event', description: 'Add an event to your calendar' },
    ],
  },
  {
    name: 'Twitch',
    actions: [
      { name: 'twitch_stream_online', description: 'Your stream goes live' },
      { name: 'twitch_stream_offline', description: 'Your stream goes offline' },
      { name: 'twitch_new_follower', description: 'Someone follows your channel' },
      { name: 'twitch_new_subscriber', description: 'Someone subscribes to your channel' },
      { name: 'twitch_channel_update', description: 'Your channel info changes (title, category)' },
    ],
    reactions: [
      { name: 'twitch_send_chat_message', description: 'Send a message to your Twitch chat' },
      { name: 'twitch_send_announcement', description: 'Send an announcement in your chat' },
      { name: 'twitch_create_clip', description: 'Create a clip from your live stream' },
      { name: 'twitch_update_title', description: 'Update your stream title' },
      { name: 'twitch_update_category', description: 'Update your stream category/game' },
    ],
  },
];
