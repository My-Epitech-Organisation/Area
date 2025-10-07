import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/service_token.dart';

void main() {
  group('ServiceToken Model Tests', () {
    test('Should create ServiceToken from JSON', () {
      final json = {
        'service_name': 'google',
        'created_at': '2025-01-06T10:00:00Z',
        'expires_at': '2025-01-06T11:00:00Z',
        'is_expired': false,
        'expires_in_minutes': 60,
        'has_refresh_token': true,
      };

      final token = ServiceToken.fromJson(json);

      expect(token.serviceName, 'google');
      expect(token.isExpired, false);
      expect(token.expiresInMinutes, 60);
      expect(token.hasRefreshToken, true);
    });

    test('Should handle null expires_at', () {
      final json = {
        'service_name': 'github',
        'created_at': '2025-01-06T10:00:00Z',
        'expires_at': null,
        'is_expired': false,
        'expires_in_minutes': null,
        'has_refresh_token': false,
      };

      final token = ServiceToken.fromJson(json);

      expect(token.serviceName, 'github');
      expect(token.expiresAt, null);
      expect(token.expiresInMinutes, null);
    });

    test('Should get correct display name', () {
      final googleToken = ServiceToken(
        serviceName: 'google',
        createdAt: DateTime.now(),
        isExpired: false,
        hasRefreshToken: true,
      );

      expect(googleToken.displayName, 'Google');
    });

    test('Should get correct status text for expired token', () {
      final expiredToken = ServiceToken(
        serviceName: 'google',
        createdAt: DateTime.now(),
        isExpired: true,
        hasRefreshToken: true,
      );

      expect(expiredToken.statusText, 'Expiré');
    });

    test('Should get correct status text for token with expiration', () {
      final token = ServiceToken(
        serviceName: 'google',
        createdAt: DateTime.now(),
        expiresInMinutes: 30,
        isExpired: false,
        hasRefreshToken: true,
      );

      expect(token.statusText, 'Expire dans 30 min');
    });

    test('Should get correct status text for long-lived token', () {
      final token = ServiceToken(
        serviceName: 'github',
        createdAt: DateTime.now(),
        expiresInMinutes: null,
        isExpired: false,
        hasRefreshToken: false,
      );

      expect(token.statusText, 'Connecté');
    });
  });

  group('ServiceConnectionList Model Tests', () {
    test('Should create ServiceConnectionList from JSON', () {
      final json = {
        'connected_services': [
          {
            'service_name': 'google',
            'created_at': '2025-01-06T10:00:00Z',
            'expires_at': '2025-01-06T11:00:00Z',
            'is_expired': false,
            'expires_in_minutes': 60,
            'has_refresh_token': true,
          },
        ],
        'available_providers': ['google', 'github'],
        'total_connected': 1,
      };

      final list = ServiceConnectionList.fromJson(json);

      expect(list.connectedServices.length, 1);
      expect(list.availableProviders.length, 2);
      expect(list.totalConnected, 1);
    });

    test('Should get unconnected providers', () {
      final json = {
        'connected_services': [
          {
            'service_name': 'google',
            'created_at': '2025-01-06T10:00:00Z',
            'expires_at': null,
            'is_expired': false,
            'expires_in_minutes': null,
            'has_refresh_token': true,
          },
        ],
        'available_providers': ['google', 'github', 'linkedin'],
        'total_connected': 1,
      };

      final list = ServiceConnectionList.fromJson(json);
      final unconnected = list.unconnectedProviders;

      expect(unconnected.length, 2);
      expect(unconnected.contains('github'), true);
      expect(unconnected.contains('linkedin'), true);
      expect(unconnected.contains('google'), false);
    });
  });

  group('OAuthInitiateResponse Model Tests', () {
    test('Should create OAuthInitiateResponse from JSON', () {
      final json = {
        'redirect_url': 'https://accounts.google.com/o/oauth2/auth',
        'state': 'abc123xyz',
        'provider': 'google',
        'expires_in': 600,
      };

      final response = OAuthInitiateResponse.fromJson(json);

      expect(response.redirectUrl, 'https://accounts.google.com/o/oauth2/auth');
      expect(response.state, 'abc123xyz');
      expect(response.provider, 'google');
      expect(response.expiresIn, 600);
    });

    test('Should use default expires_in if not provided', () {
      final json = {
        'redirect_url': 'https://github.com/login/oauth/authorize',
        'state': 'xyz789',
        'provider': 'github',
      };

      final response = OAuthInitiateResponse.fromJson(json);

      expect(response.expiresIn, 600);
    });
  });
}
