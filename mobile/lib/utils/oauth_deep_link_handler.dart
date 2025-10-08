import 'dart:async';
import 'package:app_links/app_links.dart';
import 'package:flutter/foundation.dart';
import '../services/oauth_service.dart';
import '../config/app_config.dart';

/// Handler for OAuth2 deep link callbacks
class OAuthDeepLinkHandler {
  final OAuthService _oauthService = OAuthService();
  final _appLinks = AppLinks();

  StreamSubscription<Uri>? _linkSubscription;

  // Callback when OAuth is completed
  Function(String provider, bool success, String? message)? onOAuthComplete;

  // Singleton pattern
  static final OAuthDeepLinkHandler _instance =
      OAuthDeepLinkHandler._internal();
  factory OAuthDeepLinkHandler() => _instance;
  OAuthDeepLinkHandler._internal();

  /// Initialize deep link listening
  Future<void> initialize() async {
    // Handle initial link if app was opened from a link
    try {
      final initialUri = await _appLinks.getInitialLink();
      if (initialUri != null) {
        await _handleDeepLink(initialUri);
      }
    } catch (e) {
      debugPrint('Error handling initial link: $e');
    }

    // Handle links while app is running
    _linkSubscription = _appLinks.uriLinkStream.listen(
      (uri) => _handleDeepLink(uri),
      onError: (err) {
        debugPrint('Deep link error: $err');
      },
    );
  }

  /// Handle OAuth deep link callback
  Future<void> _handleDeepLink(Uri uri) async {
    debugPrint('Handling deep link: $uri');

    // Check if this is an OAuth callback
    // Expected format: myapp://auth/oauth/{provider}/callback?code=xxx&state=yyy
    if (uri.scheme == AppConfig.urlScheme && uri.host == AppConfig.authHost) {
      final pathSegments = uri.pathSegments;

      if (pathSegments.length >= 3 &&
          pathSegments[0] == AppConfig.oauthPath &&
          pathSegments[2] == AppConfig.callbackPath) {
        final provider = pathSegments[1];
        final code = uri.queryParameters['code'];
        final state = uri.queryParameters['state'];
        final error = uri.queryParameters['error'];

        if (error != null) {
          // OAuth error
          final errorDescription =
              uri.queryParameters['error_description'] ?? error;
          debugPrint('OAuth error: $errorDescription');
          onOAuthComplete?.call(provider, false, errorDescription);
          return;
        }

        if (code == null || state == null) {
          debugPrint('Missing code or state in OAuth callback');
          onOAuthComplete?.call(
            provider,
            false,
            'Invalid OAuth callback parameters',
          );
          return;
        }

        // Complete OAuth flow
        try {
          final result = await _oauthService.handleOAuthCallback(
            provider: provider,
            code: code,
            state: state,
          );

          final message =
              result['message'] as String? ??
              'Successfully connected to $provider';

          debugPrint('OAuth success: $message');
          onOAuthComplete?.call(provider, true, message);
        } catch (e) {
          debugPrint('OAuth callback error: $e');
          onOAuthComplete?.call(provider, false, e.toString());
        }
      }
    }
  }

  /// Dispose the handler
  void dispose() {
    _linkSubscription?.cancel();
    _linkSubscription = null;
  }
}
