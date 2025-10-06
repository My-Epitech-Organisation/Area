import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';

class ConnectivityTester {
  static Future<bool> testConnection() async {
    try {
      ApiConfig.debugPrint('Testing connection to: ${ApiConfig.baseUrl}');

      final response = await http
          .get(
            Uri.parse('${ApiConfig.baseUrl}/auth/register/'),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 5));

      ApiConfig.debugPrint('Connection test result: ${response.statusCode}');

      return response.statusCode == 405 || response.statusCode == 200;
    } catch (e) {
      ApiConfig.debugPrint('Connection test failed: $e');
      return false;
    }
  }

  static Future<Map<String, dynamic>> testAuth() async {
    try {
      ApiConfig.debugPrint('Testing auth with: ${ApiConfig.loginUrl}');

      final response = await http
          .post(
            Uri.parse(ApiConfig.loginUrl),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'username': 'test_connection',
              'password': 'invalid',
            }),
          )
          .timeout(const Duration(seconds: 10));

      ApiConfig.debugPrint('Auth test result: ${response.statusCode}');

      return {
        'success': response.statusCode == 401 || response.statusCode == 200,
        'statusCode': response.statusCode,
        'message': response.statusCode == 401
            ? 'Server responds correctly (invalid credentials)'
            : response.statusCode == 200
            ? 'Server responds correctly'
            : 'Unexpected status: ${response.statusCode}',
        'body': response.body.length > 200
            ? '${response.body.substring(0, 200)}...'
            : response.body,
      };
    } catch (e) {
      ApiConfig.debugPrint('Auth test failed: $e');
      return {
        'success': false,
        'error': e.toString(),
        'message': 'Connection failed: $e',
      };
    }
  }
}
