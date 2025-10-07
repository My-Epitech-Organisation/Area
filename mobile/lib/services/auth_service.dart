import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import '../config/google_signin_config.dart';
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

  // Google Sign-In singleton instance
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
  // GOOGLE AUTHENTICATION
  // ============================================

  /// Enable debug logs for Google Sign-In (set to false in production)
  static const bool _enableGoogleSignInDebugLogs = true;

  void _logDebug(String message) {
    if (_enableGoogleSignInDebugLogs && kDebugMode) {
      debugPrint(message);
    }
  }

  /// Initialize Google Sign-In with Web Client ID
  /// 
  /// This method initializes the Google Sign-In instance with the Web Client ID
  /// from GoogleSignInConfig. This is required before calling authenticate().
  /// 
  /// The Web Client ID must match the one configured in the backend to ensure
  /// the ID token can be verified.
  Future<void> _ensureGoogleSignInInitialized() async {
    if (!_isGoogleSignInInitialized) {
      _logDebug('🔧 Initializing Google Sign-In...');
      _logDebug('📋 Web Client ID: ${GoogleSignInConfig.webClientId}');
      
      await _googleSignIn.initialize(
        serverClientId: GoogleSignInConfig.webClientId,
      );
      
      _isGoogleSignInInitialized = true;
      _logDebug('✅ Google Sign-In initialized successfully');
    }
  }

  /// Login with Google account
  /// 
  /// Flow:
  /// 1. Initialize Google Sign-In with Web Client ID
  /// 2. Authenticate user with Google (opens Google Sign-In UI)
  /// 3. Receive ID token from Google
  /// 4. Send ID token to backend at /auth/google-login/
  /// 5. Backend verifies token and returns JWT tokens
  /// 6. Store JWT tokens locally
  /// 
  /// Returns user data with tokens if successful, null otherwise
  Future<Map<String, dynamic>?> loginWithGoogle() async {
    try {
      _logDebug('🚀 Starting Google Sign-In...');
      await _ensureGoogleSignInInitialized();

      _logDebug('🔐 Authenticating with Google...');
      final GoogleSignInAccount account = await _googleSignIn.authenticate(
        scopeHint: <String>['email'],
      );

      _logDebug('✅ Google authentication successful');
      _logDebug('📧 Account email: ${account.email}');
      
      final GoogleSignInAuthentication auth = account.authentication;
      final String? idToken = auth.idToken;

      if (idToken == null) {
        throw AuthException('No Google ID token received');
      }

      _logDebug('🎫 ID Token received, sending to backend...');
      final response = await http.post(
        Uri.parse(ApiConfig.googleLoginUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'id_token': idToken}),
      );

      _logDebug('📡 Backend response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storeTokensFromResponse(data);
        _logDebug('✅ Login successful!');
        return data;
      }

      final errorMessage = _parseErrorResponse(response);
      _logDebug('❌ Backend error: $errorMessage');
      throw AuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      _logDebug('❌ Google sign-in error: $e');
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
  // PASSWORD RESET
  // ============================================

  /// Request password reset email
  Future<Map<String, dynamic>> requestPasswordReset({
    required String email,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.forgotPasswordUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
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

  /// Reset password with token/code
  Future<Map<String, dynamic>> resetPassword({
    required String token,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.resetPasswordUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'token': token,
          'new_password': newPassword,
          'confirm_password': confirmPassword,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
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
      'email': {
        'A user with that email already exists.':
            'This email is already registered. Please login instead.',
        'already exists': 'This email is already registered.',
        'Enter a valid email address.': 'Please enter a valid email address.',
      },
      'username': {
        // Username is just a display name (non-unique), so no "already exists" error expected
        'This field may not be blank.': 'Please enter a display name.',
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
