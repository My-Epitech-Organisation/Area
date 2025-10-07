import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import 'token_service.dart';

/// Exception thrown when HTTP request fails
class HttpException implements Exception {
  final String message;
  final int? statusCode;

  HttpException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Service responsible for HTTP communication with retry and authentication
class HttpClientService {
  final TokenService _tokenService = TokenService();

  // Singleton pattern
  static final HttpClientService _instance = HttpClientService._internal();
  factory HttpClientService() => _instance;
  HttpClientService._internal();

  /// Get headers with authentication token
  Future<Map<String, String>> _getHeaders() async {
    final token = await _tokenService.getAuthToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  /// Refresh access token using refresh token
  Future<bool> refreshAccessToken() async {
    final refreshToken = await _tokenService.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse(ApiConfig.refreshUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['access'] != null) {
          await _tokenService.setAuthToken(data['access']);
          return true;
        }
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  /// Execute HTTP request with retry logic
  Future<http.Response> _retryRequest(
    Future<http.Response> Function() request, {
    bool isRetry = false,
  }) async {
    int attempt = 0;
    while (attempt < ApiConfig.maxRetries) {
      try {
        final response = await request().timeout(ApiConfig.timeout);

        // Handle 401 Unauthorized - try to refresh token
        if (response.statusCode == 401 && !isRetry) {
          final refreshed = await refreshAccessToken();
          if (refreshed) {
            return await _retryRequest(request, isRetry: true);
          }
        }

        // Don't retry on client errors (except 429) or successful responses
        if (response.statusCode != 429 && response.statusCode < 500) {
          return response;
        }
      } catch (e) {
        if (attempt == ApiConfig.maxRetries - 1) rethrow;
      }

      attempt++;
      await Future.delayed(Duration(seconds: attempt * 2));
    }
    throw HttpException('Max retries exceeded');
  }

  /// Perform GET request
  Future<http.Response> get(
    String url, {
    Map<String, String>? additionalHeaders,
  }) async {
    return await _retryRequest(
      () async {
        final headers = await _getHeaders();
        if (additionalHeaders != null) {
          headers.addAll(additionalHeaders);
        }
        return http.get(Uri.parse(url), headers: headers);
      },
    );
  }

  /// Perform POST request
  Future<http.Response> post(
    String url, {
    Map<String, dynamic>? body,
    Map<String, String>? additionalHeaders,
  }) async {
    return await _retryRequest(
      () async {
        final headers = await _getHeaders();
        if (additionalHeaders != null) {
          headers.addAll(additionalHeaders);
        }
        return http.post(
          Uri.parse(url),
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
      },
    );
  }

  /// Perform PATCH request
  Future<http.Response> patch(
    String url, {
    Map<String, dynamic>? body,
    Map<String, String>? additionalHeaders,
  }) async {
    return await _retryRequest(
      () async {
        final headers = await _getHeaders();
        if (additionalHeaders != null) {
          headers.addAll(additionalHeaders);
        }
        return http.patch(
          Uri.parse(url),
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
      },
    );
  }

  /// Perform DELETE request
  Future<http.Response> delete(
    String url, {
    Map<String, String>? additionalHeaders,
  }) async {
    return await _retryRequest(
      () async {
        final headers = await _getHeaders();
        if (additionalHeaders != null) {
          headers.addAll(additionalHeaders);
        }
        return http.delete(Uri.parse(url), headers: headers);
      },
    );
  }

  /// Parse response and throw exception if error
  T parseResponse<T>(http.Response response, T Function(dynamic) parser) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = json.decode(response.body);
      return parser(data);
    }

    if (response.statusCode == 401) {
      throw HttpException('Authentication required', statusCode: 401);
    }

    throw HttpException(
      'Request failed: ${response.statusCode}',
      statusCode: response.statusCode,
    );
  }
}
