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
        ApiConfig.debugPrint('✅ Backend port configured: $_configuredPort');
      } else {
        ApiConfig.debugPrint('❌ Failed to parse BACKEND_PORT: "$portString"');
      }
    } else {
      ApiConfig.debugPrint(
        '⚠️  BACKEND_PORT is empty, using default: ${AppConfig.defaultPort}',
      );
    }
  }

  static void setPort(int port) {
    _configuredPort = port;
    ApiConfig.debugPrint('✅ Backend port set to: $port');
  }

  static String? _overrideBaseUrl;
  static String? _autoDetectedBase;
  static bool _forceAndroidLocalhost = false;

  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
    ApiConfig.debugPrint('✅ Base URL override set to: $_overrideBaseUrl');
  }

  static void forceAndroidLocalhost(bool enable) {
    _forceAndroidLocalhost = enable;
    _autoDetectedBase = null;
  }

  static String _detectBaseUrl() {
    // Return cached result if available
    if (_autoDetectedBase != null) return _autoDetectedBase!;

    final port = _configuredPort ?? AppConfig.defaultPort;
    String host;

    if (kIsWeb) {
      // Web always uses localhost
      host = AppConfig.defaultHost;
      ApiConfig.debugPrint('🌐 Detected: Web - using localhost');
    } else if (Platform.isAndroid && !_forceAndroidLocalhost) {
      // Android emulator needs special host IP
      host = AppConfig.androidEmulatorHost;
      ApiConfig.debugPrint('🌐 Detected: Android emulator - using 10.0.2.2');
    } else {
      // iOS, physical devices, or forced localhost
      host = AppConfig.defaultHost;
      ApiConfig.debugPrint(
        '🌐 Detected: Physical device/iOS - using localhost',
      );
    }

    final baseUrl = 'http://$host:$port';
    ApiConfig.debugPrint('🌐 Base URL: $baseUrl');
    return _autoDetectedBase = baseUrl;
  }

  static String get baseUrl => _overrideBaseUrl ?? _detectBaseUrl();

  static String get authBaseUrl {
    final url = '$baseUrl/${AppConfig.authPrefix}';
    ApiConfig.debugPrint('🔐 Auth base URL: $url');
    return url;
  }

  static String get apiBaseUrl {
    final url = '$baseUrl/${AppConfig.apiPrefix}';
    ApiConfig.debugPrint('📡 API base URL: $url');
    return url;
  }

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

  static String get googleLoginUrl {
    final url = '$authBaseUrl/google-login/';
    ApiConfig.debugPrint('🔑 Google Login URL: $url');
    return url;
  }

  static String automationUrl(int id) {
    final url = '$apiBaseUrl/areas/$id/';
    ApiConfig.debugPrint('📋 Automation URL ($id): $url');
    return url;
  }

  static String automationDuplicateUrl(int id) =>
      '$apiBaseUrl/areas/$id/duplicate/';
  static String automationPauseUrl(int id) => '$apiBaseUrl/areas/$id/pause/';
  static String automationResumeUrl(int id) => '$apiBaseUrl/areas/$id/resume/';
  static String serviceActionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/actions/';
  static String serviceReactionsUrl(int serviceId) =>
      '$apiBaseUrl/services/$serviceId/reactions/';
  static String appletExecutionsUrl(int areaId, {int limit = 50}) =>
      '$apiBaseUrl/executions/?area=$areaId&limit=$limit&ordering=-created_at';
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
