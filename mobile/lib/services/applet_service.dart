import 'package:flutter/foundation.dart';
import '../models/applet.dart';
import '../models/execution.dart';
import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';

/// Service responsible for applet (automation) management
class AppletService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  static const String _cacheKeyPrefix = 'applets';

  // Singleton pattern
  static final AppletService _instance = AppletService._internal();
  factory AppletService() => _instance;
  AppletService._internal();

  /// Fetch all applets with optional cache
  Future<List<Applet>> fetchApplets({bool forceRefresh = false}) async {
    const cacheKey = _cacheKeyPrefix;

    if (!forceRefresh) {
      final cached = _cache.get<List<Applet>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.automationsUrl);

    final applets = _httpClient.parseResponse<List<Applet>>(response, (data) {
      // API returns paginated response: {"results": [...]}
      if (data is Map && data.containsKey('results')) {
        final results = data['results'] as List<dynamic>;
        return results.map((json) => Applet.fromJson(json)).toList();
      }
      // Fallback: if data is already a list, use it directly
      if (data is List) {
        return data.map((json) => Applet.fromJson(json)).toList();
      }
      throw Exception('Unexpected automations API response format: $data');
    });

    _cache.set(cacheKey, applets);
    return applets;
  }

  /// Create a new applet
  Future<Applet> createApplet({
    required String description,
    required int actionId,
    required int reactionId,
    required Map<String, dynamic> actionConfig,
    required Map<String, dynamic> reactionConfig,
  }) async {
    final response = await _httpClient.post(
      ApiConfig.automationsUrl,
      body: {
        'name': description,
        'action': actionId,
        'reaction': reactionId,
        'action_config': actionConfig,
        'reaction_config': reactionConfig,
      },
    );

    final applet = _httpClient.parseResponse<Applet>(response, (data) {
      try {
        return Applet.fromJson(data);
      } catch (e, stackTrace) {
        debugPrint('❌ ERROR parsing Applet from JSON: $e');
        debugPrint('📊 Raw data: $data');
        debugPrint('📚 Stack trace: $stackTrace');
        rethrow;
      }
    });

    // Clear cache to force refresh
    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  /// Update an existing applet
  Future<Applet> updateApplet(
    int id, {
    String? name,
    String? description,
    String? status,
    Map<String, dynamic>? actionConfig,
    Map<String, dynamic>? reactionConfig,
  }) async {
    final updateData = <String, dynamic>{};

    if (name != null) updateData['name'] = name;
    if (description != null) updateData['description'] = description;
    if (status != null) updateData['status'] = status;
    if (actionConfig != null) updateData['action_config'] = actionConfig;
    if (reactionConfig != null) updateData['reaction_config'] = reactionConfig;

    final response = await _httpClient.patch(
      ApiConfig.automationUrl(id),
      body: updateData,
    );

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) => Applet.fromJson(data),
    );

    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  /// Delete an applet
  Future<void> deleteApplet(int id) async {
    final response = await _httpClient.delete(ApiConfig.automationUrl(id));

    if (response.statusCode == 204) {
      _cache.remove(_cacheKeyPrefix);
    } else {
      throw Exception('Failed to delete applet: ${response.statusCode}');
    }
  }

  /// Toggle applet active/inactive state
  Future<Applet> toggleApplet(int id) async {
    final response = await _httpClient.post(ApiConfig.automationToggleUrl(id));

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) => Applet.fromJson(data),
    );

    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  Future<Applet> duplicateApplet(int id, String newName) async {
    final response = await _httpClient.post(
      ApiConfig.automationDuplicateUrl(id),
      body: {'name': newName},
    );

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) => Applet.fromJson(data),
    );

    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  /// Get automations (applets) by user ID
  Future<List<Applet>> getAppletsByUser(int userId) async {
    final response = await _httpClient.get(
      ApiConfig.userAutomationsUrl(userId.toString()),
    );

    return _httpClient.parseResponse<List<Applet>>(response, (data) {
      // API returns paginated response: {"results": [...]}
      if (data is Map && data.containsKey('results')) {
        final results = data['results'] as List<dynamic>;
        return results.map((json) => Applet.fromJson(json)).toList();
      }
      // Fallback: if data is already a list, use it directly
      if (data is List) {
        return data.map((json) => Applet.fromJson(json)).toList();
      }
      throw Exception('Unexpected user automations API response format: $data');
    });
  }

  Future<List<Execution>> getAppletExecutions(
    int areaId, {
    int limit = 50,
  }) async {
    final response = await _httpClient.get(
      ApiConfig.appletExecutionsUrl(areaId, limit: limit),
    );

    return _httpClient.parseResponse<List<Execution>>(response, (data) {
      if (data is Map && data.containsKey('results')) {
        final results = data['results'] as List<dynamic>;
        return results.map((json) => Execution.fromJson(json)).toList();
      }
      if (data is List) {
        return data.map((json) => Execution.fromJson(json)).toList();
      }
      throw Exception('Unexpected executions API response format: $data');
    });
  }

  Future<Applet> pauseApplet(int id) async {
    final response = await _httpClient.post(ApiConfig.automationPauseUrl(id));

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) => Applet.fromJson(data),
    );

    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  Future<Applet> resumeApplet(int id) async {
    final response = await _httpClient.post(ApiConfig.automationResumeUrl(id));

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) => Applet.fromJson(data),
    );

    _cache.remove(_cacheKeyPrefix);
    return applet;
  }

  /// Clear all applet-related cache
  void clearCache() {
    _cache.remove(_cacheKeyPrefix);
  }
}
