import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/applet.dart';

class ApiService {
  static const String baseUrl = 'https://your-area-backend.com/api'; // Replace with your actual backend URL
  static const int maxRetries = 3;
  static const Duration timeout = Duration(seconds: 30);

  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Cache management
  final Map<String, dynamic> _cache = {};
  final Map<String, DateTime> _cacheTimestamps = {};

  // Auth token management
  String? _authToken;
  Future<String?> get authToken async {
    if (_authToken == null) {
      final prefs = await SharedPreferences.getInstance();
      _authToken = prefs.getString('auth_token');
    }
    return _authToken;
  }

  Future<void> setAuthToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  Future<void> clearAuthToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // HTTP headers with auth
  Future<Map<String, String>> get _headers async {
    final token = await authToken;
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Retry logic with exponential backoff
  Future<http.Response> _retryRequest(Future<http.Response> Function() request) async {
    int attempt = 0;
    while (attempt < maxRetries) {
      try {
        final response = await request().timeout(timeout);
        if (response.statusCode != 429 && response.statusCode < 500) {
          return response;
        }
      } catch (e) {
        if (attempt == maxRetries - 1) rethrow;
      }

      attempt++;
      await Future.delayed(Duration(seconds: attempt * 2)); // Exponential backoff
    }
    throw Exception('Max retries exceeded');
  }

  // Cache helper
  dynamic _getCached(String key) {
    if (_cache.containsKey(key)) {
      final timestamp = _cacheTimestamps[key];
      if (timestamp != null && DateTime.now().difference(timestamp).inMinutes < 5) {
        return _cache[key];
      } else {
        _cache.remove(key);
        _cacheTimestamps.remove(key);
      }
    }
    return null;
  }

  void _setCache(String key, dynamic data) {
    _cache[key] = data;
    _cacheTimestamps[key] = DateTime.now();
  }

  // Fetch the list of applets with caching
  Future<List<Applet>> fetchApplets({bool forceRefresh = false}) async {
    const cacheKey = 'applets';

    if (!forceRefresh) {
      final cached = _getCached(cacheKey);
      if (cached != null) return cached as List<Applet>;
    }

    final response = await _retryRequest(() =>
      http.get(Uri.parse('$baseUrl/applets'), headers: await _headers)
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      final applets = data.map((json) => Applet.fromJson(json)).toList();
      _setCache(cacheKey, applets);
      return applets;
    } else if (response.statusCode == 401) {
      await clearAuthToken();
      throw Exception('Authentication required');
    } else {
      throw Exception('Failed to load applets: ${response.statusCode}');
    }
  }

  // Create new applet
  Future<Applet> createApplet({
    required String name,
    required String description,
    required String triggerService,
    required String actionService,
    required Map<String, dynamic> triggerConfig,
    required Map<String, dynamic> actionConfig,
  }) async {
    final response = await _retryRequest(() =>
      http.post(
        Uri.parse('$baseUrl/applets'),
        headers: await _headers,
        body: json.encode({
          'name': name,
          'description': description,
          'trigger_service': triggerService,
          'action_service': actionService,
          'trigger_config': triggerConfig,
          'action_config': actionConfig,
        }),
      )
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      // Clear cache to force refresh
      _cache.remove('applets');
      return Applet.fromJson(data);
    } else {
      throw Exception('Failed to create applet: ${response.statusCode}');
    }
  }

  // Update applet
  Future<Applet> updateApplet(int id, {
    String? name,
    String? description,
    bool? isActive,
    Map<String, dynamic>? triggerConfig,
    Map<String, dynamic>? actionConfig,
  }) async {
    final updateData = {
      if (name != null) 'name': name,
      if (description != null) 'description': description,
      if (isActive != null) 'is_active': isActive,
      if (triggerConfig != null) 'trigger_config': triggerConfig,
      if (actionConfig != null) 'action_config': actionConfig,
    };

    final response = await _retryRequest(() =>
      http.patch(
        Uri.parse('$baseUrl/applets/$id'),
        headers: await _headers,
        body: json.encode(updateData),
      )
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _cache.remove('applets'); // Clear cache
      return Applet.fromJson(data);
    } else {
      throw Exception('Failed to update applet: ${response.statusCode}');
    }
  }

  // Delete applet
  Future<void> deleteApplet(int id) async {
    final response = await _retryRequest(() =>
      http.delete(Uri.parse('$baseUrl/applets/$id'), headers: await _headers)
    );

    if (response.statusCode == 204) {
      _cache.remove('applets'); // Clear cache
    } else {
      throw Exception('Failed to delete applet: ${response.statusCode}');
    }
  }

  // Toggle applet active state
  Future<Applet> toggleApplet(int id) async {
    final response = await _retryRequest(() =>
      http.post(
        Uri.parse('$baseUrl/applets/$id/toggle'),
        headers: await _headers,
      )
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _cache.remove('applets'); // Clear cache
      return Applet.fromJson(data);
    } else {
      throw Exception('Failed to toggle applet: ${response.statusCode}');
    }
  }

  // Get available services
  Future<List<Map<String, dynamic>>> getAvailableServices() async {
    const cacheKey = 'services';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as List<Map<String, dynamic>>;

    final response = await _retryRequest(() =>
      http.get(Uri.parse('$baseUrl/services'), headers: await _headers)
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      final services = data.map((item) => item as Map<String, dynamic>).toList();
      _setCache(cacheKey, services);
      return services;
    } else {
      throw Exception('Failed to load services: ${response.statusCode}');
    }
  }

  // Login
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _retryRequest(() =>
      http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      )
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['token'] != null) {
        await setAuthToken(data['token']);
      }
      return data;
    } else {
      throw Exception('Login failed: ${response.statusCode}');
    }
  }

  // Register
  Future<Map<String, dynamic>> register(String email, String password, String name) async {
    final response = await _retryRequest(() =>
      http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'name': name,
        }),
      )
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      if (data['token'] != null) {
        await setAuthToken(data['token']);
      }
      return data;
    } else {
      throw Exception('Registration failed: ${response.statusCode}');
    }
  }

  // Get user profile
  Future<Map<String, dynamic>> getUserProfile() async {
    const cacheKey = 'user_profile';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as Map<String, dynamic>;

    final response = await _retryRequest(() =>
      http.get(Uri.parse('$baseUrl/auth/profile'), headers: await _headers)
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _setCache(cacheKey, data);
      return data;
    } else {
      throw Exception('Failed to load profile: ${response.statusCode}');
    }
  }

  // Get applet execution logs
  Future<List<Map<String, dynamic>>> getAppletLogs(int appletId, {int limit = 50}) async {
    final response = await _retryRequest(() =>
      http.get(
        Uri.parse('$baseUrl/applets/$appletId/logs?limit=$limit'),
        headers: await _headers,
      )
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      return data.map((item) => item as Map<String, dynamic>).toList();
    } else {
      throw Exception('Failed to load logs: ${response.statusCode}');
    }
  }

  // Get statistics
  Future<Map<String, dynamic>> getStatistics() async {
    const cacheKey = 'statistics';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as Map<String, dynamic>;

    final response = await _retryRequest(() =>
      http.get(Uri.parse('$baseUrl/statistics'), headers: await _headers)
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _setCache(cacheKey, data);
      return data;
    } else {
      throw Exception('Failed to load statistics: ${response.statusCode}');
    }
  }
}