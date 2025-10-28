import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/service_token.dart';
import '../models/connection_history.dart';
import '../utils/service_token_mapper.dart';
import 'token_service.dart';

class OAuthException implements Exception {
  final String message;
  final int? statusCode;

  OAuthException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

class OAuthService {
  final TokenService _tokenService = TokenService();

  static final OAuthService _instance = OAuthService._internal();
  factory OAuthService() => _instance;
  OAuthService._internal();

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
      throw OAuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to initiate OAuth: ${e.toString()}');
    }
  }

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

      final callbackUrl = ApiConfig.oauthCallbackUrl(
        provider,
        code: code,
        state: state,
      );
      debugPrint('[OAUTH] Making callback request to: $callbackUrl');

      try {
        final response = await http
            .get(
              Uri.parse(callbackUrl),
              headers: {
                'Authorization': 'Bearer $token',
                'Content-Type': 'application/json',
              },
            )
            .timeout(const Duration(seconds: 15));

        debugPrint('[OAUTH] Got response status: ${response.statusCode}');

        if (response.statusCode == 302 || response.statusCode == 301) {
          debugPrint('[OAUTH] Got redirect (302/301) - treating as success');
          return {
            'message': 'Successfully connected to $provider',
            'provider': provider,
          };
        }

        if (response.statusCode == 200) {
          return json.decode(response.body);
        }

        final errorMessage = _parseErrorResponse(response);
        throw OAuthException(errorMessage, statusCode: response.statusCode);
      } on SocketException catch (e) {
        if (e.message.contains('Connection refused') ||
            e.message.contains('localhost')) {
          debugPrint(
            '[OAUTH] Got connection refused (expected from redirect attempt) - treating as success',
          );
          return {
            'message': 'Successfully connected to $provider',
            'provider': provider,
          };
        }
        rethrow;
      }
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to complete OAuth: ${e.toString()}');
    }
  }

  Future<ServiceConnectionList> getConnectedServices() async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.get(
        Uri.parse(ApiConfig.connectedServicesUrl),
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
      throw OAuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to fetch services: ${e.toString()}');
    }
  }

  Future<ConnectionHistoryList> getConnectionHistory({int limit = 20}) async {
    try {
      final token = await _tokenService.getAuthToken();
      if (token == null) {
        throw OAuthException('User not authenticated');
      }

      final response = await http.get(
        Uri.parse('${ApiConfig.connectionHistoryUrl}?limit=$limit'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ConnectionHistoryList.fromJson(data);
      }

      final errorMessage = _parseErrorResponse(response);
      throw OAuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException(
        'Failed to fetch connection history: ${e.toString()}',
      );
    }
  }

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
      throw OAuthException(errorMessage, statusCode: response.statusCode);
    } catch (e) {
      if (e is OAuthException) rethrow;
      throw OAuthException('Failed to disconnect service: ${e.toString()}');
    }
  }

  Future<bool> isServiceConnected(String provider) async {
    try {
      final services = await getConnectedServices();
      final tokenName = ServiceTokenMapper.resolveTokenService(provider);
      return services.connectedServices.any(
        (s) => s.serviceName.toLowerCase() == tokenName.toLowerCase(),
      );
    } catch (e) {
      return false;
    }
  }

  Future<ServiceToken?> getServiceToken(String provider) async {
    try {
      final services = await getConnectedServices();
      final tokenName = ServiceTokenMapper.resolveTokenService(provider);
      final matchingServices = services.connectedServices.where(
        (s) => s.serviceName.toLowerCase() == tokenName.toLowerCase(),
      );
      return matchingServices.isNotEmpty ? matchingServices.first : null;
    } catch (e) {
      return null;
    }
  }

  String _parseErrorResponse(http.Response response) {
    try {
      final data = json.decode(response.body);

      if (data is Map<String, dynamic>) {
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
