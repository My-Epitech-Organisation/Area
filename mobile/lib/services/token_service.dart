import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Service responsible for token storage and management
class TokenService {
  static const String _authTokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  // Singleton pattern
  static final TokenService _instance = TokenService._internal();
  factory TokenService() => _instance;
  TokenService._internal();

  String? _authToken;
  String? _refreshToken;

  /// Get the current auth token from memory or storage
  Future<String?> getAuthToken() async {
    _authToken ??= await _secureStorage.read(key: _authTokenKey);
    return _authToken;
  }

  /// Get the current refresh token from memory or storage
  Future<String?> getRefreshToken() async {
    _refreshToken ??= await _secureStorage.read(key: _refreshTokenKey);
    return _refreshToken;
  }

  /// Save auth token to memory and storage
  Future<void> setAuthToken(String token) async {
    _authToken = token;
    await _secureStorage.write(key: _authTokenKey, value: token);
  }

  /// Save refresh token to memory and storage
  Future<void> setRefreshToken(String token) async {
    _refreshToken = token;
    await _secureStorage.write(key: _refreshTokenKey, value: token);
  }

  /// Save both tokens at once
  Future<void> setTokens({
    required String authToken,
    required String refreshToken,
  }) async {
    await Future.wait([setAuthToken(authToken), setRefreshToken(refreshToken)]);
  }

  /// Clear all tokens from memory and storage
  Future<void> clearTokens() async {
    _authToken = null;
    _refreshToken = null;
    await Future.wait([
      _secureStorage.delete(key: _authTokenKey),
      _secureStorage.delete(key: _refreshTokenKey),
    ]);
  }

  /// Check if user has valid tokens
  Future<bool> hasValidTokens() async {
    final authToken = await getAuthToken();
    return authToken != null && authToken.isNotEmpty;
  }
}
