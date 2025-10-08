import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/utils/service_icons.dart';

void main() {
  group('ServiceIcons', () {
    test('getServiceIcon should return correct icons for known services', () {
      expect(ServiceIcons.getServiceIcon('github'), Icons.code);
      expect(ServiceIcons.getServiceIcon('discord'), Icons.chat);
      expect(ServiceIcons.getServiceIcon('gmail'), Icons.email);
      expect(ServiceIcons.getServiceIcon('spotify'), Icons.music_note);
      expect(ServiceIcons.getServiceIcon('youtube'), Icons.play_circle_fill);
      expect(ServiceIcons.getServiceIcon('facebook'), Icons.facebook);
      expect(ServiceIcons.getServiceIcon('twitter'), Icons.alternate_email);
      expect(ServiceIcons.getServiceIcon('x'), Icons.alternate_email);
      expect(ServiceIcons.getServiceIcon('slack'), Icons.message);
      expect(ServiceIcons.getServiceIcon('telegram'), Icons.send);
      expect(ServiceIcons.getServiceIcon('weather'), Icons.wb_sunny);
      expect(ServiceIcons.getServiceIcon('timer'), Icons.timer);
      expect(ServiceIcons.getServiceIcon('rss'), Icons.rss_feed);
    });

    test('getServiceIcon should return default icon for unknown services', () {
      expect(ServiceIcons.getServiceIcon('unknown'), Icons.apps);
      expect(ServiceIcons.getServiceIcon('randomservice'), Icons.apps);
      expect(ServiceIcons.getServiceIcon(''), Icons.apps);
    });

    test('getServiceIcon should be case insensitive', () {
      expect(ServiceIcons.getServiceIcon('GITHUB'), Icons.code);
      expect(ServiceIcons.getServiceIcon('Discord'), Icons.chat);
      expect(ServiceIcons.getServiceIcon('GMAIL'), Icons.email);
    });
  });
}