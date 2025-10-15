import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';

/// Service responsible for automation statistics
class AutomationStatsService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final AutomationStatsService _instance =
      AutomationStatsService._internal();
  factory AutomationStatsService() => _instance;
  AutomationStatsService._internal();

  /// Get areas statistics
  Future<Map<String, dynamic>> getAreasStats({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'areas_stats';

    if (!forceRefresh) {
      final cached = _cache.get<Map<String, dynamic>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(
      '${ApiConfig.baseUrl}/api/areas/stats/',
    );

    final stats = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    _cache.set(cacheKey, stats);
    return stats;
  }

  /// Get executions statistics
  Future<Map<String, dynamic>> getExecutionsStats({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'executions_stats';

    if (!forceRefresh) {
      final cached = _cache.get<Map<String, dynamic>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(
      '${ApiConfig.baseUrl}/api/executions/stats/',
    );

    final stats = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    _cache.set(cacheKey, stats);
    return stats;
  }
}
