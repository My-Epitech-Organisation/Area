import '../config/service_provider_config.dart';
import 'package:flutter/material.dart';

class ServiceTokenParseException implements Exception {
  final String message;
  final Map<String, dynamic>? json;
  final Object? originalError;

  ServiceTokenParseException(this.message, {this.json, this.originalError});

  @override
  String toString() {
    return 'ServiceTokenParseException: $message\n'
        'JSON: $json\n'
        'Original Error: $originalError';
  }
}

/// Model representing a connected OAuth2 service token
class ServiceToken {
  final String serviceName;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final bool isExpired;
  final int? expiresInMinutes;
  final bool hasRefreshToken;

  ServiceToken({
    required this.serviceName,
    required this.createdAt,
    this.expiresAt,
    required this.isExpired,
    this.expiresInMinutes,
    required this.hasRefreshToken,
  });

  factory ServiceToken.fromJson(Map<String, dynamic> json) {
    try {
      return ServiceToken(
        serviceName: json['service_name'] as String? ?? '',
        createdAt: json['created_at'] != null
            ? DateTime.parse(json['created_at'] as String)
            : DateTime.now(),
        expiresAt: json['expires_at'] != null
            ? DateTime.parse(json['expires_at'] as String)
            : null,
        isExpired: json['is_expired'] as bool? ?? false,
        expiresInMinutes: json['expires_in_minutes'] as int?,
        hasRefreshToken: json['has_refresh_token'] as bool? ?? false,
      );
    } catch (e) {
      throw ServiceTokenParseException(
        'Failed to parse ServiceToken from JSON: $e',
        json: json,
        originalError: e,
      );
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'service_name': serviceName,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'is_expired': isExpired,
      'expires_in_minutes': expiresInMinutes,
      'has_refresh_token': hasRefreshToken,
    };
  }

  /// Get user-friendly service name
  String get displayName => ServiceProviderConfig.getDisplayName(serviceName);

  /// Get status color
  String get statusColor {
    if (isExpired) return 'red';
    if (expiresInMinutes != null && expiresInMinutes! < 60) return 'orange';
    return 'green';
  }

  /// Get status text
  String get statusText {
    if (isExpired) return 'Expiré';
    if (expiresInMinutes == null) return 'Connecté';
    if (expiresInMinutes! < 60) {
      return 'Expire dans $expiresInMinutes min';
    }
    final hours = (expiresInMinutes! / 60).floor();
    return 'Expire dans $hours h';
  }
}

/// Model for OAuth2 initiation response
class OAuthInitiateResponse {
  final String redirectUrl;
  final String state;
  final String provider;
  final int expiresIn;

  OAuthInitiateResponse({
    required this.redirectUrl,
    required this.state,
    required this.provider,
    required this.expiresIn,
  });

  factory OAuthInitiateResponse.fromJson(Map<String, dynamic> json) {
    return OAuthInitiateResponse(
      redirectUrl: json['redirect_url'] as String,
      state: json['state'] as String,
      provider: json['provider'] as String,
      expiresIn: json['expires_in'] as int? ?? 600,
    );
  }
}

/// Model for service connection list
class ServiceConnectionList {
  final List<ServiceToken> connectedServices;
  final List<String> availableProviders;
  final int totalConnected;

  ServiceConnectionList({
    required this.connectedServices,
    required this.availableProviders,
    required this.totalConnected,
  });

  factory ServiceConnectionList.fromJson(Map<String, dynamic> json) {
    final connectedServices = <ServiceToken>[];

    final servicesList = json['connected_services'] as List<dynamic>? ?? [];
    for (final serviceJson in servicesList) {
      if (serviceJson == null) continue;

      try {
        final serviceToken = ServiceToken.fromJson(
          serviceJson as Map<String, dynamic>,
        );
        connectedServices.add(serviceToken);
      } catch (e) {
        if (e is ServiceTokenParseException) {
        } else {
          rethrow;
        }
      }
    }

    return ServiceConnectionList(
      connectedServices: connectedServices,
      availableProviders:
          (json['available_providers'] as List<dynamic>?)
              ?.where((e) => e != null)
              .map((e) => e as String)
              .toList() ??
          [],
      totalConnected:
          json['total_connected'] as int? ?? connectedServices.length,
    );
  }

  /// Get list of providers that are not yet connected
  List<String> get unconnectedProviders {
    final connectedNames = connectedServices.map((s) => s.serviceName).toSet();
    return availableProviders
        .where((p) => !connectedNames.contains(p))
        .toList();
  }
}

/// Model representing a connection history entry
class ConnectionHistoryEntry {
  final String serviceName;
  final String
  eventType; // 'connected', 'disconnected', 'expired', 'refreshed', 'failed'
  final DateTime timestamp;
  final String? message;
  final bool isError;

  ConnectionHistoryEntry({
    required this.serviceName,
    required this.eventType,
    required this.timestamp,
    this.message,
    this.isError = false,
  });

  factory ConnectionHistoryEntry.fromJson(Map<String, dynamic> json) {
    return ConnectionHistoryEntry(
      serviceName: json['service_name'] as String? ?? '',
      eventType: json['event_type'] as String? ?? 'unknown',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      message: json['message'] as String?,
      isError: json['is_error'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'service_name': serviceName,
      'event_type': eventType,
      'timestamp': timestamp.toIso8601String(),
      'message': message,
      'is_error': isError,
    };
  }

  /// Get display name for the service
  String get displayServiceName =>
      ServiceProviderConfig.getDisplayName(serviceName);

  /// Get event icon
  IconData get eventIcon {
    switch (eventType.toLowerCase()) {
      case 'connected':
        return Icons.link;
      case 'disconnected':
        return Icons.link_off;
      case 'expired':
        return Icons.warning;
      case 'refreshed':
        return Icons.refresh;
      case 'failed':
        return Icons.error;
      default:
        return Icons.info;
    }
  }

  /// Get event color
  Color get eventColor {
    if (isError) return Colors.red;
    switch (eventType.toLowerCase()) {
      case 'connected':
        return Colors.green;
      case 'disconnected':
        return Colors.orange;
      case 'expired':
        return Colors.red;
      case 'refreshed':
        return Colors.blue;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  /// Get event display text
  String get eventDisplayText {
    switch (eventType.toLowerCase()) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'expired':
        return 'Expired';
      case 'refreshed':
        return 'Refreshed';
      case 'failed':
        return 'Failed';
      default:
        return eventType;
    }
  }

  /// Get formatted timestamp
  String get formattedTimestamp {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays}d';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}min';
    } else {
      return 'Now';
    }
  }
}
