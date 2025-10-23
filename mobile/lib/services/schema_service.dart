import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';

/// Service responsible for configuration schemas management
class SchemaService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final SchemaService _instance = SchemaService._internal();
  factory SchemaService() => _instance;
  SchemaService._internal();

  Future<Map<String, dynamic>?> getActionSchema(String actionName) async {
    final cacheKey = 'action_schema_$actionName';

    final cached = _cache.get<Map<String, dynamic>>(cacheKey);
    if (cached != null) return cached;

    try {
      final response = await _httpClient.get(
        '${ApiConfig.schemasUrl}actions/$actionName/',
      );

      final schema = _httpClient.parseResponse<Map<String, dynamic>>(
        response,
        (data) => data as Map<String, dynamic>,
      );

      _cache.set(cacheKey, schema);
      return schema;
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> getReactionSchema(String reactionName) async {
    final cacheKey = 'reaction_schema_$reactionName';

    final cached = _cache.get<Map<String, dynamic>>(cacheKey);
    if (cached != null) {
      return cached;
    }

    try {
      final response = await _httpClient.get(
        '${ApiConfig.schemasUrl}reactions/$reactionName/',
      );

      final schema = _httpClient.parseResponse<Map<String, dynamic>>(
        response,
        (data) => data as Map<String, dynamic>,
      );

      _cache.set(cacheKey, schema);
      return schema;
    } catch (e) {
      return null;
    }
  }

  void clearCache() {
    _cache.clearByPattern('action_schema_');
    _cache.clearByPattern('reaction_schema_');
  }
}
