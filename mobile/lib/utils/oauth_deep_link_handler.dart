import 'dart:async';
import 'package:flutter/foundation.dart';
import '../services/oauth_service.dart';
import '../config/app_config.dart';

class OAuthDeepLinkHandler {
  final OAuthService _oauthService = OAuthService();
  final Set<String> _processedStates = {};

  Function(String provider, bool success, String? message)? onOAuthComplete;

  static final OAuthDeepLinkHandler _instance =
      OAuthDeepLinkHandler._internal();
  factory OAuthDeepLinkHandler() => _instance;
  OAuthDeepLinkHandler._internal();

  bool isOAuthCallback(Uri uri) {
    if (uri.scheme == AppConfig.urlScheme && uri.host == AppConfig.authPrefix) {
      final pathSegments = uri.pathSegments;
      return pathSegments.length >= 3 &&
          pathSegments[0] == AppConfig.oauthPath &&
          pathSegments[2] == AppConfig.callbackPath;
    } else if (uri.scheme == 'http' || uri.scheme == 'https') {
      final path = uri.path;
      final pathSegments = path.split('/').where((s) => s.isNotEmpty).toList();
      return pathSegments.length >= 4 &&
          pathSegments[0] == 'auth' &&
          pathSegments[1] == 'oauth' &&
          pathSegments[3] == 'callback';
    }
    return false;
  }

  Future<void> handleDeepLink(Uri uri) async {
    if (!isOAuthCallback(uri)) {
      return;
    }
    await _handleDeepLink(uri);
  }

  Map<String, dynamic>? _parseOAuthCallback(Uri uri) {
    String? provider;
    final code = uri.queryParameters['code'];
    final state = uri.queryParameters['state'];
    final error = uri.queryParameters['error'];
    final errorDescription = uri.queryParameters['error_description'];

    if (uri.scheme == AppConfig.urlScheme && uri.host == AppConfig.authPrefix) {
      final pathSegments = uri.pathSegments;
      if (pathSegments.length >= 3 &&
          pathSegments[0] == AppConfig.oauthPath &&
          pathSegments[2] == AppConfig.callbackPath) {
        provider = pathSegments[1];
      }
    } else if (uri.scheme == 'http' || uri.scheme == 'https') {
      final path = uri.path;
      final pathSegments = path.split('/').where((s) => s.isNotEmpty).toList();

      if (pathSegments.length >= 4 &&
          pathSegments[0] == 'auth' &&
          pathSegments[1] == 'oauth' &&
          pathSegments[3] == 'callback') {
        provider = pathSegments[2];
      }
    }

    if (provider == null) {
      debugPrint('Could not parse OAuth provider from URI: $uri');
      return null;
    }

    return {
      'provider': provider,
      'code': code,
      'state': state,
      'error': error,
      'errorDescription': errorDescription,
    };
  }

  Future<void> _handleDeepLink(Uri uri) async {
    debugPrint('[OAUTH-HANDLER] Handling deep link: $uri');

    final oauthData = _parseOAuthCallback(uri);
    if (oauthData == null) {
      debugPrint('[OAUTH-HANDLER] Failed to parse OAuth data from URI');
      return;
    }

    final provider = oauthData['provider'] as String;
    final code = oauthData['code'] as String?;
    final state = oauthData['state'] as String?;
    final error = oauthData['error'] as String?;
    final errorDescription = oauthData['errorDescription'] as String?;

    debugPrint(
      '[OAUTH-HANDLER] Parsed: provider=$provider, code=${code?.substring(0, 10)}..., state=$state',
    );

    if (state != null && _processedStates.contains(state)) {
      debugPrint('[OAUTH-HANDLER] OAuth state already processed: $state');
      return;
    }

    if (state != null) {
      _processedStates.add(state);
    }

    if (error != null) {
      final description = errorDescription ?? error;
      debugPrint('OAuth error: $description');
      onOAuthComplete?.call(provider, false, description);
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

    try {
      debugPrint('[OAUTH-HANDLER] Calling backend to complete OAuth flow...');
      final result = await _oauthService.handleOAuthCallback(
        provider: provider,
        code: code,
        state: state,
      );

      final message =
          result['message'] as String? ?? 'Successfully connected to $provider';

      debugPrint('[OAUTH-HANDLER] OAuth success: $message');
      onOAuthComplete?.call(provider, true, message);
    } catch (e) {
      debugPrint('[OAUTH-HANDLER] OAuth callback error: $e');
      onOAuthComplete?.call(provider, false, e.toString());
    }
  }

  void dispose() {}
}
