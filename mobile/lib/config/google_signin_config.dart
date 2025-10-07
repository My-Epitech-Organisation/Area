import 'package:flutter/foundation.dart';

/// Google Sign-In Configuration
///
/// This file contains the configuration for Google Sign-In authentication.
///
/// ## Architecture
///
/// 1. Mobile app uses this Web Client ID to initialize Google Sign-In
/// 2. User authenticates with Google
/// 3. Mobile receives an ID token signed by Google
/// 4. Mobile sends this token to backend at /auth/google-login/
/// 5. Backend verifies the token using the SAME Web Client ID
/// 6. Backend returns JWT tokens for API authentication
///
/// ## Important Notes
///
/// - ⚠️ This MUST be the **WEB Client ID**, NOT the Android Client ID
/// - The same Web Client ID must be configured in backend/.env
/// - Android Client ID is used automatically by Google (don't put it in code)
/// - See /mobile/GOOGLE_SIGNIN_SETUP.md for complete setup instructions
///
/// ## Configuration Sources
///
/// This Web Client ID should match:
/// - Backend: `backend/.env` → GOOGLE_CLIENT_ID
/// - Backend: `backend/area_project/settings/base.py` → GOOGLE_CLIENT_ID
///
class GoogleSignInConfig {
  /// Web Client ID from Google Cloud Console
  ///
  /// Type: OAuth 2.0 Client ID for **Web application**
  ///
  /// Where to get this:
  /// 1. https://console.cloud.google.com/apis/credentials
  /// 2. CREATE CREDENTIALS → OAuth 2.0 Client ID
  /// 3. Application type: **Web application**
  /// 4. Copy the Client ID
  ///
  /// Current value: Set for development/production
  static const String webClientId =
      '810500685105-bsetto3ag8e6n45p1j3378e6ommfeq7e.apps.googleusercontent.com';

  /// Scopes requested from Google
  static const List<String> scopes = [
    'email',
    'profile',
  ];

  /// Debug mode
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
