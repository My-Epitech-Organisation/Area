import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  // ============================================================================
  // CONSTANTS
  // ============================================================================

  static const String _defaultHost = 'localhost';
  static const int _defaultPort = 8080;
  static const String _androidEmulatorHost = '10.0.2.2';

  static const String _apiPrefix = 'api';
  static const String _authPrefix = 'auth';
  static const String _appletsPrefix = 'applets';

  // Dynamic port configuration
  static int? _configuredPort;

  /// Initialize configuration from environment
  static void initialize() {
    try {
      final portString = dotenv.env['BACKEND_PORT'];
      if (portString != null && portString.isNotEmpty) {
        _configuredPort = int.tryParse(portString);
        if (_configuredPort != null) {
          ApiConfig.debugPrint(
            'Backend port configured from env: $_configuredPort',
          );
        }
      }
    } catch (e) {
      ApiConfig.debugPrint('Failed to parse BACKEND_PORT from env: $e');
    }
  }

  /// Set custom port for testing or runtime configuration
  static void setPort(int port) {
    _configuredPort = port;
    ApiConfig.debugPrint('Backend port set to: $port');
  }

  // ============================================================================
  // CONFIGURATION
  // ============================================================================

  static String? _overrideBaseUrl;
  static String? _autoDetectedBase;
  static bool _forceAndroidLocalhost = false;

  /// Override the base URL for custom configurations
  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
    ApiConfig.debugPrint('Base URL override set to: $_overrideBaseUrl');
  }

  /// Force Android to use localhost instead of emulator IP
  static void forceAndroidLocalhost(bool enable) {
    _forceAndroidLocalhost = enable;
    _autoDetectedBase = null;
  }

  // ============================================================================
  // BASE URL DETECTION
  // ============================================================================

  static String _detectBaseUrl() {
    if (_autoDetectedBase != null) return _autoDetectedBase!;

    if (kIsWeb) {
      final port = _configuredPort ?? _defaultPort;
      return _autoDetectedBase = _buildBaseUrl(_defaultHost, port);
    }

    try {
      final platformConfig = _getPlatformConfig();
      return _autoDetectedBase = _buildBaseUrl(
        platformConfig['host'] as String,
        platformConfig['port'] as int,
      );
    } catch (_) {
      final port = _configuredPort ?? _defaultPort;
      return _autoDetectedBase = _buildBaseUrl(_defaultHost, port);
    }
  }

  static Map<String, dynamic> _getPlatformConfig() {
    final port = _configuredPort ?? _defaultPort;

    if (Platform.isAndroid) {
      return {
        'host': _forceAndroidLocalhost ? _defaultHost : _androidEmulatorHost,
        'port': port,
      };
    }

    // iOS, Linux, macOS, Windows, and other platforms
    return {'host': _defaultHost, 'port': port};
  }

  static String _buildBaseUrl(String host, int port) {
    return 'http://$host:$port';
  }

  static String get baseUrl => _overrideBaseUrl ?? _detectBaseUrl();

  // ============================================================================
  // URL BUILDERS
  // ============================================================================

  static String get authBaseUrl => '$baseUrl/$_authPrefix';
  static String get apiBaseUrl => '$baseUrl/$_apiPrefix';

  // Authentication URLs
  static String get loginUrl => '$authBaseUrl/login/';
  static String get registerUrl => '$authBaseUrl/register/';
  static String get refreshUrl => '$authBaseUrl/login/refresh/';
  static String get profileUrl => '$authBaseUrl/me/';

  // Password Reset URLs
  static String get forgotPasswordUrl => '$authBaseUrl/password-reset/';
  static String get resetPasswordUrl => '$authBaseUrl/password-reset/confirm/';

  // Service URLs
  static String get automationsUrl => '$apiBaseUrl/areas/';
  static String get servicesUrl => '$apiBaseUrl/services/';
  static String get actionsUrl => '$apiBaseUrl/actions/';
  static String get reactionsUrl => '$apiBaseUrl/reactions/';
  static String get schemasUrl => '$apiBaseUrl/schemas/';
  static String get aboutUrl => '$baseUrl/about.json';

  // Statistics URLs
  static String get statisticsUrl => '$authBaseUrl/statistics';
  static String get userStatisticsUrl => '$apiBaseUrl/users/statistics/';

  // Legacy URLs (keeping for compatibility)
  static String get appletsUrl => '$baseUrl/$_appletsPrefix/';
  static String get googleLoginUrl => '$authBaseUrl/google-login/';

  // ============================================================================
  // DYNAMIC URL BUILDERS
  // ============================================================================

  static String automationUrl(int id) => '$apiBaseUrl/areas/$id/';
  static String automationToggleUrl(int id) => '$apiBaseUrl/areas/$id/toggle/';
  static String serviceActionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/actions/';
  static String serviceReactionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/reactions/';
  static String appletLogsUrl(int appletId, {int limit = 50}) =>
      '$baseUrl/$_appletsPrefix/$appletId/logs?limit=$limit';
  static String userAutomationsUrl(String userId) =>
      '$apiBaseUrl/users/$userId/areas/';

  // OAuth2 URLs
  static String oauthInitiateUrl(String provider) =>
      '$authBaseUrl/oauth/$provider/';
  static String oauthCallbackUrl(
    String provider, {
    required String code,
    required String state,
  }) => '$authBaseUrl/oauth/$provider/callback/?code=$code&state=$state';
  static String serviceDisconnectUrl(String provider) =>
      '$authBaseUrl/services/$provider/disconnect/';
  static String get connectedServicesUrl => '$authBaseUrl/services/';
  static String get connectionHistoryUrl => '$authBaseUrl/oauth/history/';

  // ============================================================================
  // CONFIGURATION CONSTANTS
  // ============================================================================

  static const int maxRetries = 3;
  static const Duration timeout = Duration(seconds: 30);
  static const Duration cacheTimeout = Duration(minutes: 5);
  static const bool isDebug = true;

  // ============================================================================
  // UTILITIES
  // ============================================================================

  static String physicalDeviceHint(String lanIp) =>
      'For physical devices, set ApiConfig.setBaseUrl("http://$lanIp:$_defaultPort") in debug code or via debug panel.';

  static void debugPrint(String message) {
    if (isDebug) {
      // ignore: avoid_print
      print('[API] $message');
    }
  }
}
