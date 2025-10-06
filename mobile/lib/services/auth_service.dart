import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import 'token_service.dart';
import 'cache_service.dart';

/// Custom exception for authentication errors
class AuthException implements Exception {
  final String message;
  final int? statusCode;

  AuthException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Service responsible for authentication operations
class AuthService {
  final TokenService _tokenService = TokenService();
  final CacheService _cache = CacheService();
  final GoogleSignIn _googleSignIn = GoogleSignIn.instance;

  bool _isGoogleSignInInitialized = false;

  // Singleton pattern
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  // ============================================
  // EMAIL/PASSWORD AUTHENTICATION
  // ============================================

  /// Login with email and password
  Future<Map<String, dynamic>> loginWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final payload = <String, String>{
        'username': email,
        'password': password,
      };

      if (email.contains('@')) {
        payload['email'] = email;
      }

      final response = await http.post(
        Uri.parse(ApiConfig.loginUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(payload),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storeTokensFromResponse(data);
        return data;
      }

      final errorMessage = _parseErrorResponse(response);
      throw AuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Connection error: ${e.toString()}');
    }
  }

  /// Register with email and password
  Future<Map<String, dynamic>> registerWithEmail({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.registerUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'email': email,
          'password': password,
          'password2': confirmPassword,
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storeTokensFromResponse(data);
        return data;
      }

      final errorMessage = _parseErrorResponse(response);
      throw AuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Registration error: ${e.toString()}');
    }
  }

  // ============================================
  // GOOGLE AUTHENTICATION
  // ============================================

  /// Initialize Google Sign-In
  Future<void> _ensureGoogleSignInInitialized() async {
    if (!_isGoogleSignInInitialized) {
      await _googleSignIn.initialize();
      _isGoogleSignInInitialized = true;
    }
  }

  /// Login with Google account
  Future<Map<String, dynamic>?> loginWithGoogle() async {
    try {
      await _ensureGoogleSignInInitialized();

      final GoogleSignInAccount account = await _googleSignIn.authenticate(
        scopeHint: <String>['email'],
      );

      final GoogleSignInAuthentication auth = account.authentication;
      final String? idToken = auth.idToken;

      if (idToken == null) {
        throw AuthException('No Google ID token received');
      }

      final response = await http.post(
        Uri.parse(ApiConfig.googleLoginUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'id_token': idToken}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storeTokensFromResponse(data);
        return data;
      }

      final errorMessage = _parseErrorResponse(response);
      throw AuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      if (e is AuthException) rethrow;
      throw AuthException('Google sign-in error: ${e.toString()}');
    }
  }

  /// Sign out from Google
  Future<void> signOutGoogle() async {
    await _ensureGoogleSignInInitialized();
    await _googleSignIn.signOut();
  }

  // ============================================
  // LOGOUT
  // ============================================

  /// Logout user and clear all data
  Future<void> logout() async {
    await _tokenService.clearTokens();
    _cache.clearAll();

    try {
      await signOutGoogle();
    } catch (_) {
      // Ignore Google sign-out errors
    }
  }

  // ============================================
  // TOKEN MANAGEMENT
  // ============================================

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    return await _tokenService.hasValidTokens();
  }

  /// Get current auth token
  Future<String?> getAuthToken() async {
    return await _tokenService.getAuthToken();
  }

  // ============================================
  // HELPER METHODS
  // ============================================

  /// Store tokens from API response
  Future<void> _storeTokensFromResponse(Map<String, dynamic> response) async {
    final accessToken = response['access'] ?? response['token'];
    final refreshToken = response['refresh'];

    if (accessToken != null && refreshToken != null) {
      await _tokenService.setTokens(
        authToken: accessToken,
        refreshToken: refreshToken,
      );
    } else if (accessToken != null) {
      await _tokenService.setAuthToken(accessToken);
    }
  }

  /// Parse error response from API
  String _parseErrorResponse(http.Response response) {
    try {
      final errorData = json.decode(response.body);

      // Format: {"detail": "message"}
      if (errorData is Map && errorData['detail'] != null) {
        return errorData['detail'].toString();
      }

      // Format: {"field": ["error1", "error2"]}
      if (errorData is Map<String, dynamic>) {
        final errors = <String>[];
        errorData.forEach((key, value) {
          if (value is List && value.isNotEmpty) {
            final cleanError = _cleanErrorMessage(key, value.first.toString());
            errors.add(cleanError);
          } else if (value is String) {
            final cleanError = _cleanErrorMessage(key, value);
            errors.add(cleanError);
          }
        });

        if (errors.isNotEmpty) {
          return errors.join('\n');
        }
      }
    } catch (_) {
      // Ignore parsing errors
    }

    return 'An error occurred (${response.statusCode})';
  }

  /// Clean and make error messages user-friendly
  String _cleanErrorMessage(String field, String message) {
    final Map<String, Map<String, String>> friendlyMessages = {
      'username': {
        'A user with that username already exists.':
            'This email is already registered. Please login instead.',
        'already exists': 'This email is already registered.',
      },
      'email': {
        'Enter a valid email address.': 'Please enter a valid email address.',
        'already exists': 'This email is already registered.',
      },
      'password': {
        'This password is too short.': 'Password must be at least 8 characters.',
        'This password is too common.': 'Please choose a stronger password.',
      },
    };

    if (friendlyMessages.containsKey(field)) {
      for (var entry in friendlyMessages[field]!.entries) {
        if (message.contains(entry.key)) {
          return entry.value;
        }
      }
    }

    return message;
  }
}
