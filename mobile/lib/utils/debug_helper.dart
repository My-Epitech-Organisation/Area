import 'dart:io';
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';

class DebugHelper {
  static void printConfiguration() {
    if (kDebugMode) {
      print('\n=== AREA App Debug Info ===');
      print('Platform: ${Platform.operatingSystem}');
      print('Base URL: ${ApiConfig.baseUrl}');
      print('Login URL: ${ApiConfig.loginUrl}');
      print('Register URL: ${ApiConfig.registerUrl}');
      print('Profile URL: ${ApiConfig.profileUrl}');
      print('Is Android: ${Platform.isAndroid}');
      print('Is iOS: ${Platform.isIOS}');
      print('Debug mode: ${ApiConfig.isDebug}');
      print('Timeout: ${ApiConfig.timeout.inSeconds}s');
      print('Max retries: ${ApiConfig.maxRetries}');
      print('===========================\n');
    }
  }

  static void printAuthStatus(bool isAuthenticated, String? error) {
    if (kDebugMode) {
      print('\n=== Auth Status ===');
      print('Authenticated: $isAuthenticated');
      if (error != null) {
        print('Error: $error');
      }
      print('==================\n');
    }
  }

  static void printApiCall(String method, String url, {String? body, int? statusCode, String? response}) {
    if (kDebugMode) {
      print('\n=== API Call ===');
      print('$method $url');
      if (body != null) {
        print('Body: $body');
      }
      if (statusCode != null) {
        print('Status: $statusCode');
      }
      if (response != null) {
        print('Response: ${response.length > 200 ? '${response.substring(0, 200)}...' : response}');
      }
      print('================\n');
    }
  }
}