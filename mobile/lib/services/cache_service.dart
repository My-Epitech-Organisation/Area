/// Service responsible for caching data with time-based invalidation
class CacheService {
  final Map<String, dynamic> _cache = {};
  final Map<String, DateTime> _cacheTimestamps = {};
  int _defaultCacheDurationMinutes = 5;

  // Singleton pattern
  static final CacheService _instance = CacheService._internal();
  factory CacheService({int cacheDurationMinutes = 5}) {
    _instance._defaultCacheDurationMinutes = cacheDurationMinutes;
    return _instance;
  }
  CacheService._internal();

  /// Get cached data if still valid
  T? get<T>(String key, {int? cacheDurationMinutes}) {
    if (!_cache.containsKey(key)) {
      return null;
    }

    final timestamp = _cacheTimestamps[key];
    if (timestamp == null) {
      remove(key);
      return null;
    }

    final duration = cacheDurationMinutes ?? _defaultCacheDurationMinutes;
    final isExpired = DateTime.now().difference(timestamp).inMinutes >= duration;

    if (isExpired) {
      remove(key);
      return null;
    }

    return _cache[key] as T?;
  }

  /// Set data in cache
  void set(String key, dynamic data) {
    _cache[key] = data;
    _cacheTimestamps[key] = DateTime.now();
  }

  /// Remove specific key from cache
  void remove(String key) {
    _cache.remove(key);
    _cacheTimestamps.remove(key);
  }

  /// Clear all cache
  void clearAll() {
    _cache.clear();
    _cacheTimestamps.clear();
  }

  /// Clear cache by pattern (e.g., all keys starting with 'user_')
  void clearByPattern(String pattern) {
    final keysToRemove = _cache.keys
        .where((key) => key.contains(pattern))
        .toList();

    for (final key in keysToRemove) {
      remove(key);
    }
  }

  /// Check if key exists and is valid
  bool has(String key) {
    return get<dynamic>(key) != null;
  }
}
