import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Google Sign-In Configuration
class GoogleSignInConfig {
  static String get webClientId {
    try {
      // Check if dotenv is loaded
      if (!dotenv.isInitialized) {
        debugPrint('⚠️ WARNING: dotenv not initialized');
        return '';
      }
      return dotenv.env['GOOGLE_CLIENT_ID'] ?? '';
    } catch (e) {
      debugPrint('⚠️ ERROR accessing GOOGLE_CLIENT_ID: $e');
      return '';
    }
  }

  static const List<String> scopes = ['email', 'profile'];

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
