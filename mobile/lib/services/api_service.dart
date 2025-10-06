import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/applet.dart';
import '../config/api_config.dart';

class ApiService {
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final Map<String, dynamic> _cache = {};
  final Map<String, DateTime> _cacheTimestamps = {};

  String? _authToken;
  String? _refreshToken;

  Future<String?> get authToken async {
    if (_authToken == null) {
      final prefs = await SharedPreferences.getInstance();
      _authToken = prefs.getString('auth_token');
    }
    return _authToken;
  }

  Future<String?> get refreshToken async {
    if (_refreshToken == null) {
      final prefs = await SharedPreferences.getInstance();
      _refreshToken = prefs.getString('refresh_token');
    }
    return _refreshToken;
  }

  Future<void> setAuthToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  Future<void> setRefreshToken(String token) async {
    _refreshToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('refresh_token', token);
  }

  Future<void> clearAuthToken() async {
    _authToken = null;
    _refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('refresh_token');
  }

  Future<Map<String, String>> get _headers async {
    final token = await authToken;
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<bool> refreshAccessToken() async {
    final refresh = await refreshToken;
    if (refresh == null) return false;

    try {
      final response = await http.post(
        Uri.parse(ApiConfig.refreshUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh': refresh}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['access'] != null) {
          await setAuthToken(data['access']);
          return true;
        }
      }
    } catch (e) {}
    return false;
  }

  dynamic _getCached(String key) {
    if (_cache.containsKey(key)) {
      final timestamp = _cacheTimestamps[key];
      if (timestamp != null &&
          DateTime.now().difference(timestamp).inMinutes < 5) {
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

  Future<http.Response> _retryRequest(
    Future<http.Response> Function() request, {
    bool isRetry = false,
  }) async {
    int attempt = 0;
    while (attempt < ApiConfig.maxRetries) {
      try {
        final response = await request().timeout(ApiConfig.timeout);

        if (response.statusCode == 401 && !isRetry) {
          final refreshed = await refreshAccessToken();
          if (refreshed) {
            return await _retryRequest(request, isRetry: true);
          }
        }

        if (response.statusCode != 429 && response.statusCode < 500) {
          return response;
        }
      } catch (e) {
        if (attempt == ApiConfig.maxRetries - 1) rethrow;
      }

      attempt++;
      await Future.delayed(Duration(seconds: attempt * 2));
    }
    throw Exception('Max retries exceeded');
  }

  Future<List<Applet>> fetchApplets({bool forceRefresh = false}) async {
    const cacheKey = 'applets';

    if (!forceRefresh) {
      final cached = _getCached(cacheKey);
      if (cached != null) return cached as List<Applet>;
    }

    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.automationsUrl),
        headers: await _headers,
      ),
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

  // Create new area (applet) - adapted for backend
  Future<Applet> createApplet({
    required String name,
    required String description,
    required int actionId,
    required int reactionId,
    required Map<String, dynamic> actionConfig,
    required Map<String, dynamic> reactionConfig,
  }) async {
    final response = await _retryRequest(
      () async => http.post(
        Uri.parse(ApiConfig.automationsUrl),
        headers: await _headers,
        body: json.encode({
          'name': name,
          'description': description,
          'action': actionId,
          'reaction': reactionId,
          'action_config': actionConfig,
          'reaction_config': reactionConfig,
        }),
      ),
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

  // Update area (applet) - adapted for backend
  Future<Applet> updateApplet(
    int id, {
    String? name,
    String? description,
    String? status, // "active", "disabled", "paused"
    Map<String, dynamic>? actionConfig,
    Map<String, dynamic>? reactionConfig,
  }) async {
    final updateData = {
      if (name != null) 'name': name,
      if (description != null) 'description': description,
      if (status != null) 'status': status,
      if (actionConfig != null) 'action_config': actionConfig,
      if (reactionConfig != null) 'reaction_config': reactionConfig,
    };

    final response = await _retryRequest(
      () async => http.patch(
        Uri.parse(ApiConfig.automationUrl(id)),
        headers: await _headers,
        body: json.encode(updateData),
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _cache.remove('applets'); // Clear cache
      return Applet.fromJson(data);
    } else {
      throw Exception('Failed to update applet: ${response.statusCode}');
    }
  }

  // Delete area (applet) - adapted for backend
  Future<void> deleteApplet(int id) async {
    final response = await _retryRequest(
      () async => http.delete(
        Uri.parse(ApiConfig.automationUrl(id)),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 204) {
      _cache.remove('applets'); // Clear cache
    } else {
      throw Exception('Failed to delete applet: ${response.statusCode}');
    }
  }

  // Toggle area active state - adapted for backend
  Future<Applet> toggleApplet(int id) async {
    final response = await _retryRequest(
      () async => http.post(
        Uri.parse(ApiConfig.automationToggleUrl(id)),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _cache.remove('applets'); // Clear cache
      return Applet.fromJson(data);
    } else {
      throw Exception('Failed to toggle applet: ${response.statusCode}');
    }
  }

  // Get available services - new backend endpoint
  Future<List<Map<String, dynamic>>> getAvailableServices() async {
    const cacheKey = 'services';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as List<Map<String, dynamic>>;

    final response = await _retryRequest(
      () async =>
          http.get(Uri.parse(ApiConfig.servicesUrl), headers: await _headers),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      final services = data
          .map((item) => item as Map<String, dynamic>)
          .toList();
      _setCache(cacheKey, services);
      return services;
    } else {
      throw Exception('Failed to load services: ${response.statusCode}');
    }
  }

  // Get actions for a specific service
  Future<List<Map<String, dynamic>>> getServiceActions(int serviceId) async {
    final cacheKey = 'actions_$serviceId';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as List<Map<String, dynamic>>;

    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.serviceActionsUrl(serviceId)),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      final actions = data.map((item) => item as Map<String, dynamic>).toList();
      _setCache(cacheKey, actions);
      return actions;
    } else {
      throw Exception('Failed to load actions: ${response.statusCode}');
    }
  }

  // Get reactions for a specific service
  Future<List<Map<String, dynamic>>> getServiceReactions(int serviceId) async {
    final cacheKey = 'reactions_$serviceId';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as List<Map<String, dynamic>>;

    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.serviceReactionsUrl(serviceId)),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      final reactions = data
          .map((item) => item as Map<String, dynamic>)
          .toList();
      _setCache(cacheKey, reactions);
      return reactions;
    } else {
      throw Exception('Failed to load reactions: ${response.statusCode}');
    }
  }

  // Login - adapted for backend
  Future<Map<String, dynamic>> login(String email, String password) async {
    ApiConfig.debugPrint('Attempting login for: $email');
    ApiConfig.debugPrint('Login URL: ${ApiConfig.loginUrl}');
    // Accept either email or username in the same field; backend handles both

    final response = await _retryRequest(
      () async => http.post(
        Uri.parse(ApiConfig.loginUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          // The backend custom serializer will interpret this as username OR email
          'username': email,
          'password': password,
        }),
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['access'] != null) {
        await setAuthToken(data['access']);
      }
      if (data['refresh'] != null) {
        await setRefreshToken(data['refresh']);
      }
      return data;
    } else {
      String msg = 'Login failed: ${response.statusCode}';
      try {
        final err = json.decode(response.body);
        if (err is Map && err['detail'] != null) {
          msg = 'Login failed: ' + err['detail'];
        }
      } catch (_) {}
      throw Exception(msg);
    }
  }

  // Register - adapted for backend
  Future<Map<String, dynamic>> register(
    String email,
    String password,
    String name,
  ) async {
    ApiConfig.debugPrint('Attempting registration for: $email');
    ApiConfig.debugPrint('Register URL: ${ApiConfig.registerUrl}');

    final response = await _retryRequest(
      () async => http.post(
        Uri.parse(ApiConfig.registerUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': email, // Use email as username for simplicity
          'email': email,
          'password': password,
          'password2': password, // Backend expects password2 for confirmation
          'first_name': name,
        }),
      ),
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      // Note: Registration might not return tokens immediately
      // User might need to verify email first
      return data;
    } else {
      String errorMessage = 'Registration failed';
      try {
        final errorData = json.decode(response.body);
        if (errorData is Map<String, dynamic>) {
          final errors = <String>[];
          errorData.forEach((key, value) {
            if (value is List) {
              errors.addAll(value.map((e) => '$key: $e'));
            } else {
              errors.add('$key: $value');
            }
          });
          errorMessage = errors.join(', ');
        }
      } catch (e) {
        errorMessage = 'Registration failed: ${response.statusCode}';
      }
      throw Exception(errorMessage);
    }
  }

  // Get user profile - adapted for backend
  Future<Map<String, dynamic>> getUserProfile() async {
    const cacheKey = 'user_profile';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as Map<String, dynamic>;

    final response = await _retryRequest(
      () async =>
          http.get(Uri.parse(ApiConfig.profileUrl), headers: await _headers),
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
  Future<List<Map<String, dynamic>>> getAppletLogs(
    int appletId, {
    int limit = 50,
  }) async {
    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.appletLogsUrl(appletId, limit: limit)),
        headers: await _headers,
      ),
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

    final response = await _retryRequest(
      () async =>
          http.get(Uri.parse(ApiConfig.statisticsUrl), headers: await _headers),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _setCache(cacheKey, data);
      return data;
    } else {
      throw Exception('Failed to load statistics: ${response.statusCode}');
    }
  }

  // Get user statistics - new backend endpoint
  Future<Map<String, dynamic>> getUserStatistics() async {
    const cacheKey = 'user_stats';

    final cached = _getCached(cacheKey);
    if (cached != null) return cached as Map<String, dynamic>;

    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.userStatisticsUrl),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 200) {
      final stats = json.decode(response.body) as Map<String, dynamic>;
      _setCache(cacheKey, stats);
      return stats;
    } else {
      throw Exception('Failed to load user statistics: ${response.statusCode}');
    }
  }

  // Get applets by user ID - new backend endpoint
  Future<List<Applet>> getAppletsByUser(int userId) async {
    final response = await _retryRequest(
      () async => http.get(
        Uri.parse(ApiConfig.userAutomationsUrl(userId.toString())),
        headers: await _headers,
      ),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List<dynamic>;
      return data
          .map((item) => Applet.fromJson(item as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception('Failed to load user applets: ${response.statusCode}');
    }
  }
}
