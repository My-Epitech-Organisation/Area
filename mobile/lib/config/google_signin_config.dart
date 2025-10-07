import 'package:flutter/foundation.dart';

/// Google Sign-In Configuration
class GoogleSignInConfig {

  static const String webClientId =
      '810500685105-bsetto3ag8e6n45p1j3378e6ommfeq7e.apps.googleusercontent.com';

  static const List<String> scopes = [
    'email',
    'profile',
  ];

  static bool get isDebug => kDebugMode;

  /// Log configuration info
  static void printConfig() {
    if (isDebug) {
      debugPrint('=== Google Sign-In Configuration ===');
      debugPrint('Web Client ID: $webClientId');
      debugPrint('Scopes: $scopes');
      debugPrint('====================================');
    }
  }
}
