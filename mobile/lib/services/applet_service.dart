import 'package:flutter/foundation.dart';
import '../models/applet.dart';
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

    final applets = _httpClient.parseResponse<List<Applet>>(
      response,
      (data) =>
          (data as List<dynamic>).map((json) => Applet.fromJson(json)).toList(),
    );

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

    final applet = _httpClient.parseResponse<Applet>(
      response,
      (data) {
        try {
          return Applet.fromJson(data);
        } catch (e, stackTrace) {
          debugPrint('❌ ERROR parsing Applet from JSON: $e');
          debugPrint('📊 Raw data: $data');
          debugPrint('📚 Stack trace: $stackTrace');
          rethrow;
        }
      },
    );

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

  /// Get applets by user ID
  Future<List<Applet>> getAppletsByUser(int userId) async {
    final response = await _httpClient.get(
      ApiConfig.userAutomationsUrl(userId.toString()),
    );

    return _httpClient.parseResponse<List<Applet>>(
      response,
      (data) =>
          (data as List<dynamic>).map((json) => Applet.fromJson(json)).toList(),
    );
  }

  /// Get applet execution logs
  Future<List<Map<String, dynamic>>> getAppletLogs(
    int appletId, {
    int limit = 50,
  }) async {
    final response = await _httpClient.get(
      ApiConfig.appletLogsUrl(appletId, limit: limit),
    );

    return _httpClient.parseResponse<List<Map<String, dynamic>>>(
      response,
      (data) => (data as List<dynamic>)
          .map((item) => item as Map<String, dynamic>)
          .toList(),
    );
  }

  /// Clear all applet-related cache
  void clearCache() {
    _cache.remove(_cacheKeyPrefix);
  }
}
