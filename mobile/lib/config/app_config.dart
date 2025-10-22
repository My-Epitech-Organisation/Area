import 'package:flutter/foundation.dart';

class AppConfig {
  static const String appName = 'AREA';
  static const String appVersion = '1.0.0';
  static const String urlScheme = 'area';

  static const String defaultHost = 'localhost';
  static const int defaultPort = 8080;
  static const String androidEmulatorHost = '10.0.2.2';

  static const String apiPrefix = 'api';
  static const String authPrefix = 'auth';
  static const String appletsPrefix = 'applets';

  static const String resetPasswordDeepLink = 'reset-password';

  static const String _backendHostDefine = String.fromEnvironment(
    'BACKEND_HOST',
    defaultValue: defaultHost,
  );
  static const String _backendPortDefine = String.fromEnvironment(
    'BACKEND_PORT',
    defaultValue: '8080',
  );
  static const String _googleClientIdDefine = String.fromEnvironment(
    'GOOGLE_CLIENT_ID',
    defaultValue: '',
  );
  static const String _googleApiKeyDefine = String.fromEnvironment(
    'GOOGLE_API_KEY',
    defaultValue: '',
  );
  static const String _githubClientIdDefine = String.fromEnvironment(
    'GITHUB_CLIENT_ID',
    defaultValue: '',
  );
  static const String _environmentDefine = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: 'development',
  );

  static const String oauthPath = 'oauth';
  static const String callbackPath = 'callback';

  static bool get isProduction {
    return _environmentDefine.toLowerCase() == 'production' || !kDebugMode;
  }

  static bool get isDevelopment => !isProduction;

  static String get backendHost {
    return _backendHostDefine;
  }

  static String get backendPort {
    return _backendPortDefine;
  }

  static String get backendUrl {
    final host = backendHost;
    final port = backendPort;
    return 'http://$host:$port';
  }

  static String get googleClientId {
    if (_googleClientIdDefine.isEmpty) {
      throw Exception(
        'GOOGLE_CLIENT_ID missing - ensure it is defined via --dart-define or --dart-define-from-file',
      );
    }
    return _googleClientIdDefine;
  }

  static String get googleApiKey {
    if (_googleApiKeyDefine.isEmpty) {
      throw Exception(
        'GOOGLE_API_KEY missing - ensure it is defined via --dart-define or --dart-define-from-file',
      );
    }
    return _googleApiKeyDefine;
  }

  static String get githubClientId {
    return _githubClientIdDefine;
  }

  static void validateEnvironment() {
    final requiredVars = {
      'GOOGLE_CLIENT_ID': _googleClientIdDefine,
      'GOOGLE_API_KEY': _googleApiKeyDefine,
    };

    for (final entry in requiredVars.entries) {
      if (entry.value.isEmpty) {
        throw Exception(
          'Required variable missing: ${entry.key} - ensure it is defined via --dart-define or --dart-define-from-file',
        );
      }
    }
  }

  static void debugPrint(String message) {
    if (kDebugMode) {
      print('[CONFIG] $message');
    }
  }
}
