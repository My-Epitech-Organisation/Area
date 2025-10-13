import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get appletsUrl => '$baseUrl/applets/';

  static String get googleLoginUrl => '$authBaseUrl/google-login/';
  static String? _overrideBaseUrl;
  static String? _autoDetectedBase;

  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
    debugPrint('Base URL override set to: $_overrideBaseUrl');
  }

  static bool _forceAndroidLocalhost = false;

  static void forceAndroidLocalhost(bool enable) {
    _forceAndroidLocalhost = enable;
    _autoDetectedBase = null;
  }

  static String _detectBaseUrl() {
    if (_autoDetectedBase != null) return _autoDetectedBase!;

    if (kIsWeb) {
      _autoDetectedBase = 'http://localhost:8080';
      return _autoDetectedBase!;
    }

    try {
      if (Platform.isAndroid) {
        _autoDetectedBase = _forceAndroidLocalhost
            ? 'http://localhost:8080'
            : 'http://10.0.2.2:8080';
      } else if (Platform.isIOS) {
        _autoDetectedBase = 'http://localhost:8080';
      } else if (Platform.isLinux || Platform.isMacOS || Platform.isWindows) {
        _autoDetectedBase = 'http://localhost:8080';
      } else {
        _autoDetectedBase = 'http://localhost:8080';
      }
    } catch (_) {
      _autoDetectedBase = 'http://localhost:8080';
    }
    return _autoDetectedBase!;
  }

  static String get baseUrl => _overrideBaseUrl ?? _detectBaseUrl();

  static String physicalDeviceHint(String lanIp) =>
      'Pour un appareil physique, définis ApiConfig.setBaseUrl("http://$lanIp:8080") dans un code debug ou via le panneau debug.';

  static String get authBaseUrl => '$baseUrl/auth';
  static String get loginUrl => '$authBaseUrl/login/';
  static String get registerUrl => '$authBaseUrl/register/';
  static String get refreshUrl => '$authBaseUrl/login/refresh/';
  static String get profileUrl => '$authBaseUrl/me/';

  // Password Reset URLs
  static String get forgotPasswordUrl => '$authBaseUrl/password-reset/';
  static String get resetPasswordUrl => '$authBaseUrl/password-reset/confirm/';

  static String get automationsUrl => '$baseUrl/api/areas/';
  static String get servicesUrl => '$baseUrl/api/services/';
  static String get actionsUrl => '$baseUrl/api/actions/';
  static String get reactionsUrl => '$baseUrl/api/reactions/';
  static String get schemasUrl => '$baseUrl/api/schemas/';
  static String get aboutUrl => '$baseUrl/about.json';
  static String get statisticsUrl => '$authBaseUrl/statistics';
  static String get userStatisticsUrl => '$baseUrl/api/users/statistics/';

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

  static String automationUrl(int id) => '$baseUrl/api/areas/$id/';
  static String automationToggleUrl(int id) =>
      '$baseUrl/api/areas/$id/toggle/';
  static String serviceActionsUrl(int serviceId) =>
      '$baseUrl/api/services/$serviceId/actions/';
  static String serviceReactionsUrl(int serviceId) =>
      '$baseUrl/api/services/$serviceId/reactions/';
  static String appletLogsUrl(int appletId, {int limit = 50}) =>
      '$baseUrl/api/applets/$appletId/logs?limit=$limit';
  static String userAutomationsUrl(String userId) =>
      '$baseUrl/api/users/$userId/areas/';

  static const int maxRetries = 3;
  static const Duration timeout = Duration(seconds: 30);
  static const Duration cacheTimeout = Duration(minutes: 5);

  static const bool isDebug = true;

  static void debugPrint(String message) {
    if (isDebug) {
      // ignore: avoid_print
      print('[API] $message');
    }
  }
}
