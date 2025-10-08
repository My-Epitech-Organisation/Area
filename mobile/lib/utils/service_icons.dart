import 'package:flutter/material.dart';

class ServiceIcons {
  static IconData getServiceIcon(String serviceName) {
    switch (serviceName.toLowerCase()) {
      case 'facebook':
        return Icons.facebook;
      case 'twitter':
      case 'x':
        return Icons.alternate_email;
      case 'gmail':
      case 'email':
        return Icons.email;
      case 'discord':
        return Icons.chat;
      case 'github':
        return Icons.code;
      case 'spotify':
        return Icons.music_note;
      case 'youtube':
        return Icons.play_circle_fill;
      case 'slack':
        return Icons.message;
      case 'telegram':
        return Icons.send;
      case 'weather':
        return Icons.wb_sunny;
      case 'timer':
        return Icons.timer;
      case 'rss':
        return Icons.rss_feed;
      default:
        return Icons.apps;
    }
  }
}
