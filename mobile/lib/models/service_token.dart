import '../config/service_provider_config.dart';

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
    return ServiceToken(
      serviceName: json['service_name'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      isExpired: json['is_expired'] as bool? ?? false,
      expiresInMinutes: json['expires_in_minutes'] as int?,
      hasRefreshToken: json['has_refresh_token'] as bool? ?? false,
    );
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

  /// Get service icon path
  String get iconPath => ServiceProviderConfig.getIconPath(serviceName);

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
    return ServiceConnectionList(
      connectedServices: (json['connected_services'] as List<dynamic>)
          .map((e) => ServiceToken.fromJson(e as Map<String, dynamic>))
          .toList(),
      availableProviders: (json['available_providers'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      totalConnected: json['total_connected'] as int,
    );
  }

  /// Get list of providers that are not yet connected
  List<String> get unconnectedProviders {
    final connectedNames =
        connectedServices.map((s) => s.serviceName).toSet();
    return availableProviders
        .where((p) => !connectedNames.contains(p))
        .toList();
  }
}
