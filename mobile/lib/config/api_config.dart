import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  // URL override (debug widget / config manuelle)
  static String? _overrideBaseUrl;
  // Cache pour l'auto-détection
  static String? _autoDetectedBase;

  // Setter manuel
  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
    debugPrint('Base URL override set to: $_overrideBaseUrl');
  }

  // Détection automatique selon la plateforme
  static bool _forceAndroidLocalhost = false; // Permet de forcer localhost même sur émulateur

  static void forceAndroidLocalhost(bool enable) {
    _forceAndroidLocalhost = enable;
    _autoDetectedBase = null; // reset pour recalcul
  }

  static String _detectBaseUrl() {
    if (_autoDetectedBase != null) return _autoDetectedBase!;

    // Web: localhost fonctionne
    if (kIsWeb) {
      _autoDetectedBase = 'http://localhost:8080';
      return _autoDetectedBase!;
    }

    try {
      if (Platform.isAndroid) {
        // Si on force, utiliser localhost sinon 10.0.2.2 (émulateur)
        _autoDetectedBase = _forceAndroidLocalhost
            ? 'http://localhost:8080'
            : 'http://10.0.2.2:8080';
      } else if (Platform.isIOS) {
        // iOS simulator peut utiliser localhost
        _autoDetectedBase = 'http://localhost:8080';
      } else if (Platform.isLinux || Platform.isMacOS || Platform.isWindows) {
        _autoDetectedBase = 'http://localhost:8080';
      } else {
        _autoDetectedBase = 'http://localhost:8080';
      }
    } catch (_) {
      // Fallback si Platform non dispo
      _autoDetectedBase = 'http://localhost:8080';
    }
    return _autoDetectedBase!;
  }

  // Base URL publique
  static String get baseUrl => _overrideBaseUrl ?? _detectBaseUrl();

  // Aide pour l'utilisateur sur appareil physique
  static String physicalDeviceHint(String lanIp) =>
      'Pour un appareil physique, définis ApiConfig.setBaseUrl("http://$lanIp:8080") dans un code debug ou via le panneau debug.';

  // URLs des endpoints
  static String get authBaseUrl => '$baseUrl/auth';
  static String get loginUrl => '$authBaseUrl/login/';
  static String get registerUrl => '$authBaseUrl/register/';
  static String get refreshUrl => '$authBaseUrl/login/refresh/';
  static String get profileUrl => '$authBaseUrl/me/';
  static String get automationsUrl => '$authBaseUrl/automations/';
  static String get servicesUrl => '$authBaseUrl/services/';
  static String get statisticsUrl => '$authBaseUrl/statistics';
  static String get userStatisticsUrl => '$authBaseUrl/users/statistics/';

  // Dynamic URLs
  static String automationUrl(int id) => '$authBaseUrl/automations/$id/';
  static String automationToggleUrl(int id) => '$authBaseUrl/automations/$id/toggle/';
  static String serviceActionsUrl(int serviceId) => '$authBaseUrl/services/$serviceId/actions/';
  static String serviceReactionsUrl(int serviceId) => '$authBaseUrl/services/$serviceId/reactions/';
  static String appletLogsUrl(int appletId, {int limit = 50}) => '$authBaseUrl/applets/$appletId/logs?limit=$limit';
  static String userAutomationsUrl(String userId) => '$authBaseUrl/users/$userId/automations/';

  // Configuration de la requête
  static const int maxRetries = 3;
  static const Duration timeout = Duration(seconds: 30);
  static const Duration cacheTimeout = Duration(minutes: 5);

  // Debug
  static const bool isDebug = true;

  static void debugPrint(String message) {
    if (isDebug) {
      // ignore: avoid_print
      print('[API] $message');
    }
  }
}