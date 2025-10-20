import 'package:flutter/material.dart';

/// Model for connection history entry
class ConnectionHistoryEntry {
  final String id;
  final String serviceName;
  final String action; // 'connected', 'disconnected', 'refreshed', 'failed'
  final DateTime timestamp;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  ConnectionHistoryEntry({
    required this.id,
    required this.serviceName,
    required this.action,
    required this.timestamp,
    this.errorMessage,
    this.metadata,
  });

  factory ConnectionHistoryEntry.fromJson(Map<String, dynamic> json) {
    return ConnectionHistoryEntry(
      id: json['id'] as String? ?? '',
      serviceName: json['service_name'] as String? ?? '',
      action: json['action'] as String? ?? 'unknown',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      errorMessage: json['error_message'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  String get displayAction {
    switch (action) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'refreshed':
        return 'Token refreshed';
      case 'failed':
        return 'Connection failed';
      default:
        return action;
    }
  }

  Color get actionColor {
    switch (action) {
      case 'connected':
        return Colors.green;
      case 'disconnected':
        return Colors.orange;
      case 'refreshed':
        return Colors.blue;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // Additional properties used by the widget
  Color get eventColor {
    switch (action) {
      case 'connected':
        return Colors.green;
      case 'disconnected':
        return Colors.orange;
      case 'refreshed':
        return Colors.blue;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData get eventIcon {
    switch (action) {
      case 'connected':
        return Icons.check_circle;
      case 'disconnected':
        return Icons.link_off;
      case 'refreshed':
        return Icons.refresh;
      case 'failed':
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  bool get isError => action == 'failed';

  String get displayServiceName => serviceName;

  String get formattedTimestamp {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays}d';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m';
    } else {
      return 'now';
    }
  }

  String get eventDisplayText => displayAction;

  String? get message => errorMessage;
}

/// Model for connection history list
class ConnectionHistoryList {
  final List<ConnectionHistoryEntry> entries;
  final int totalEntries;

  ConnectionHistoryList({required this.entries, required this.totalEntries});

  factory ConnectionHistoryList.fromJson(Map<String, dynamic> json) {
    final entries = <ConnectionHistoryEntry>[];

    final entriesList = json['entries'] as List<dynamic>? ?? [];
    for (final entryJson in entriesList) {
      if (entryJson == null) continue;

      try {
        final entry = ConnectionHistoryEntry.fromJson(
          entryJson as Map<String, dynamic>,
        );
        entries.add(entry);
      } catch (e) {
        // Skip invalid entries
      }
    }

    return ConnectionHistoryList(
      entries: entries,
      totalEntries: json['total_entries'] as int? ?? entries.length,
    );
  }
}
