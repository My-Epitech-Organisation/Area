import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';

/// Service responsible for user profile and statistics
class UserService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final UserService _instance = UserService._internal();
  factory UserService() => _instance;
  UserService._internal();

  /// Get user profile
  Future<Map<String, dynamic>> getUserProfile({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'user_profile';

    if (!forceRefresh) {
      final cached = _cache.get<Map<String, dynamic>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.profileUrl);

    final profile = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    _cache.set(cacheKey, profile);
    return profile;
  }

  /// Get user statistics
  Future<Map<String, dynamic>> getUserStatistics({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'user_stats';

    if (!forceRefresh) {
      final cached = _cache.get<Map<String, dynamic>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.userStatisticsUrl);

    final stats = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    _cache.set(cacheKey, stats);
    return stats;
  }

  /// Get general statistics
  Future<Map<String, dynamic>> getStatistics({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'statistics';

    if (!forceRefresh) {
      final cached = _cache.get<Map<String, dynamic>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.statisticsUrl);

    final stats = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    _cache.set(cacheKey, stats);
    return stats;
  }

  /// Clear all user-related cache
  void clearCache() {
    _cache.clearByPattern('user_');
    _cache.remove('statistics');
  }
}
