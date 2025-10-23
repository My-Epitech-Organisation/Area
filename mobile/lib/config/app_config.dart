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

  static String get urlSchemeHost {
    return 'auth';
  }

  static String get oauthPath {
    return 'oauth';
  }

  static String get callbackPath {
    return 'callback';
  }

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

  // Validation flag to ensure validateEnvironment() is called once at startup
  static bool _validated = false;

  /// Safe getters that return values after validation
  /// Call validateEnvironment() during app initialization before using these
  static String get googleClientId {
    assert(
      _validated,
      'Call AppConfig.validateEnvironment() before accessing googleClientId',
    );
    return _googleClientIdDefine;
  }

  static String get googleApiKey {
    assert(
      _validated,
      'Call AppConfig.validateEnvironment() before accessing googleApiKey',
    );
    return _googleApiKeyDefine;
  }

  static String get githubClientId {
    return _githubClientIdDefine;
  }

  /// Validate required environment variables once at app startup
  /// Should be called in main() before runApp()
  /// Throws exception if any required variable is missing
  static void validateEnvironment() {
    if (_validated) return; // Already validated

    final requiredVars = {
      'GOOGLE_CLIENT_ID': _googleClientIdDefine,
      'GOOGLE_API_KEY': _googleApiKeyDefine,
    };

    final missingVars = <String>[];
    for (final entry in requiredVars.entries) {
      if (entry.value.isEmpty) {
        missingVars.add(entry.key);
      }
    }

    if (missingVars.isNotEmpty) {
      throw Exception(
        'Required environment variables missing: ${missingVars.join(", ")}\n'
        'Ensure they are defined via --dart-define or --dart-define-from-file',
      );
    }

    _validated = true;
    debugPrint('✅ Environment validation passed');
  }

  static void debugPrint(String message) {
    if (kDebugMode) {
      print('[CONFIG] $message');
    }
  }
}
