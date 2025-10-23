import 'dart:io';
import 'package:flutter/foundation.dart';
import 'app_config.dart';

class ApiConfig {
  static int? _configuredPort;

  static void initialize() {
    final portString = AppConfig.backendPort;
    if (portString.isNotEmpty) {
      _configuredPort = int.tryParse(portString);
      if (_configuredPort != null) {
        ApiConfig.debugPrint('Backend port configured: $_configuredPort');
      }
    }
  }

  static void setPort(int port) {
    _configuredPort = port;
    ApiConfig.debugPrint('Backend port set to: $port');
  }

  static String? _overrideBaseUrl;
  static String? _autoDetectedBase;
  static bool _forceAndroidLocalhost = false;

  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
    ApiConfig.debugPrint('Base URL override set to: $_overrideBaseUrl');
  }

  static void forceAndroidLocalhost(bool enable) {
    _forceAndroidLocalhost = enable;
    _autoDetectedBase = null;
  }

  static String _detectBaseUrl() {
    if (_autoDetectedBase != null) return _autoDetectedBase!;

    if (kIsWeb) {
      final port = _configuredPort ?? AppConfig.defaultPort;
      return _autoDetectedBase = _buildBaseUrl(AppConfig.defaultHost, port);
    }

    try {
      final platformConfig = _getPlatformConfig();
      return _autoDetectedBase = _buildBaseUrl(
        platformConfig['host'] as String,
        platformConfig['port'] as int,
      );
    } catch (_) {
      final port = _configuredPort ?? AppConfig.defaultPort;
      return _autoDetectedBase = _buildBaseUrl(AppConfig.defaultHost, port);
    }
  }

  static Map<String, dynamic> _getPlatformConfig() {
    final port = _configuredPort ?? AppConfig.defaultPort;

    if (Platform.isAndroid) {
      return {
        'host': _forceAndroidLocalhost
            ? AppConfig.defaultHost
            : AppConfig.androidEmulatorHost,
        'port': port,
      };
    }

    return {'host': AppConfig.defaultHost, 'port': port};
  }

  static String _buildBaseUrl(String host, int port) {
    return 'http://$host:$port';
  }

  static String get baseUrl => _overrideBaseUrl ?? _detectBaseUrl();

  static String get authBaseUrl => '$baseUrl/${AppConfig.authPrefix}';
  static String get apiBaseUrl => '$baseUrl/${AppConfig.apiPrefix}';

  static String get loginUrl => '$authBaseUrl/login/';
  static String get registerUrl => '$authBaseUrl/register/';
  static String get refreshUrl => '$authBaseUrl/login/refresh/';
  static String get profileUrl => '$authBaseUrl/me/';

  static String get forgotPasswordUrl => '$authBaseUrl/password-reset/';
  static String get resetPasswordUrl => '$authBaseUrl/password-reset/confirm/';

  static String get automationsUrl => '$apiBaseUrl/areas/';
  static String get servicesUrl => '$apiBaseUrl/services/';
  static String get actionsUrl => '$apiBaseUrl/actions/';
  static String get reactionsUrl => '$apiBaseUrl/reactions/';
  static String get schemasUrl => '$apiBaseUrl/schemas/';
  static String get aboutUrl => '$baseUrl/about.json';

  static String get statisticsUrl => '$authBaseUrl/statistics';
  static String get userStatisticsUrl => '$apiBaseUrl/users/statistics/';

  static String get appletsUrl => '$baseUrl/${AppConfig.appletsPrefix}/';
  static String get googleLoginUrl => '$authBaseUrl/google-login/';

  static String automationUrl(int id) => '$apiBaseUrl/areas/$id/';
  static String automationToggleUrl(int id) => '$apiBaseUrl/areas/$id/toggle/';
  static String serviceActionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/actions/';
  static String serviceReactionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/reactions/';
  static String appletLogsUrl(int appletId, {int limit = 50}) =>
      '$baseUrl/${AppConfig.appletsPrefix}/$appletId/logs?limit=$limit';
  static String userAutomationsUrl(String userId) =>
      '$apiBaseUrl/users/$userId/areas/';

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

  static const int maxRetries = 3;
  static const Duration timeout = Duration(seconds: 30);
  static const Duration cacheTimeout = Duration(minutes: 5);
  static const bool isDebug = true;

  static String physicalDeviceHint(String lanIp) =>
      'For physical devices, set ApiConfig.setBaseUrl("http://$lanIp:${AppConfig.defaultPort}") in debug code or via debug panel.';

  static void debugPrint(String message) {
    if (kDebugMode) {
      print('[API] $message');
    }
  }
}
