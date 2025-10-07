import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/service_token.dart';
import 'token_service.dart';

/// Custom exception for OAuth errors
class OAuthException implements Exception {
  final String message;
  final int? statusCode;

  OAuthException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Service responsible for OAuth2 operations
class OAuthService {
  final TokenService _tokenService = TokenService();

  // Singleton pattern
  static final OAuthService _instance = OAuthService._internal();
  factory OAuthService() => _instance;
  OAuthService._internal();

  // ============================================
  // OAUTH2 INITIATION
  // ============================================

  /// Initiate OAuth2 flow for a provider
  /// Returns the authorization URL to open in browser
  Future<OAuthInitiateResponse> initiateOAuth(String provider) async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.get(
        Uri.parse(ApiConfig.oauthInitiateUrl(provider)),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return OAuthInitiateResponse.fromJson(data);
      }

      final errorMessage = _parseErrorResponse(response);
      throw OAuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to initiate OAuth: ${e.toString()}');
    }
  }

  // ============================================
  // OAUTH2 CALLBACK HANDLING
  // ============================================

  /// Handle OAuth2 callback with code and state
  Future<Map<String, dynamic>> handleOAuthCallback({
    required String provider,
    required String code,
    required String state,
  }) async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.get(
        Uri.parse(
          ApiConfig.oauthCallbackUrl(
            provider,
            code: code,
            state: state,
          ),
        ),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }

      final errorMessage = _parseErrorResponse(response);
      throw OAuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to complete OAuth: ${e.toString()}');
    }
  }

  // ============================================
  // SERVICE MANAGEMENT
  // ============================================

  /// Get list of connected services
  Future<ServiceConnectionList> getConnectedServices() async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.get(
        Uri.parse(ApiConfig.servicesUrl),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ServiceConnectionList.fromJson(data);
      }

      final errorMessage = _parseErrorResponse(response);
      throw OAuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to fetch services: ${e.toString()}');
    }
  }

  /// Disconnect a service
  Future<Map<String, dynamic>> disconnectService(String provider) async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.delete(
        Uri.parse(ApiConfig.serviceDisconnectUrl(provider)),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }

      final errorMessage = _parseErrorResponse(response);
      throw OAuthException(
        errorMessage,
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to disconnect service: ${e.toString()}');
    }
  }

  /// Check if a specific service is connected
  Future<bool> isServiceConnected(String provider) async {
    try {
      final services = await getConnectedServices();
      return services.connectedServices
          .any((s) => s.serviceName.toLowerCase() == provider.toLowerCase());
    } catch (e) {
      return false;
    }
  }

  /// Get token info for a specific service
  Future<ServiceToken?> getServiceToken(String provider) async {
    try {
      final services = await getConnectedServices();
      final matchingServices = services.connectedServices
          .where((s) => s.serviceName.toLowerCase() == provider.toLowerCase());
      return matchingServices.isNotEmpty ? matchingServices.first : null;
    } catch (e) {
      return null;
    }
  }

  // ============================================
  // HELPER METHODS
  // ============================================

  /// Parse error response from API
  String _parseErrorResponse(http.Response response) {
    try {
      final data = json.decode(response.body);

      if (data is Map<String, dynamic>) {
        // Try to get error message from various possible fields
        if (data.containsKey('message')) {
          return data['message'] as String;
        }
        if (data.containsKey('error')) {
          final error = data['error'];
          if (error is String) return error;
          if (error is Map && error.containsKey('message')) {
            return error['message'] as String;
          }
        }
        if (data.containsKey('detail')) {
          return data['detail'] as String;
        }

        // If it's a map of field errors, combine them
        final errors = <String>[];
        data.forEach((key, value) {
          if (value is List) {
            errors.add('$key: ${value.join(", ")}');
          } else if (value is String) {
            errors.add('$key: $value');
          }
        });

        if (errors.isNotEmpty) {
          return errors.join('\n');
        }
      }

      return 'Request failed with status ${response.statusCode}';
    } catch (e) {
      return 'Request failed with status ${response.statusCode}';
    }
  }

}
