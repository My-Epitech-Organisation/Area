import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';

/// Service responsible for service catalog (services, actions, reactions)
class ServiceCatalogService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final ServiceCatalogService _instance = ServiceCatalogService._internal();
  factory ServiceCatalogService() => _instance;
  ServiceCatalogService._internal();

  /// Get all available services
  Future<List<Map<String, dynamic>>> getAvailableServices({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'services';

    if (!forceRefresh) {
      final cached = _cache.get<List<Map<String, dynamic>>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.servicesUrl);

    final services = _httpClient.parseResponse<List<Map<String, dynamic>>>(
      response,
      (data) => (data as List<dynamic>)
          .map((item) => item as Map<String, dynamic>)
          .toList(),
    );

    _cache.set(cacheKey, services);
    return services;
  }

  /// Get actions for a specific service
  Future<List<Map<String, dynamic>>> getServiceActions(
    int serviceId, {
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'actions_$serviceId';

    if (!forceRefresh) {
      final cached = _cache.get<List<Map<String, dynamic>>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(
      ApiConfig.serviceActionsUrl(serviceId),
    );

    final actions = _httpClient.parseResponse<List<Map<String, dynamic>>>(
      response,
      (data) => (data as List<dynamic>)
          .map((item) => item as Map<String, dynamic>)
          .toList(),
    );

    _cache.set(cacheKey, actions);
    return actions;
  }

  /// Get reactions for a specific service
  Future<List<Map<String, dynamic>>> getServiceReactions(
    int serviceId, {
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'reactions_$serviceId';

    if (!forceRefresh) {
      final cached = _cache.get<List<Map<String, dynamic>>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(
      ApiConfig.serviceReactionsUrl(serviceId),
    );

    final reactions = _httpClient.parseResponse<List<Map<String, dynamic>>>(
      response,
      (data) => (data as List<dynamic>)
          .map((item) => item as Map<String, dynamic>)
          .toList(),
    );

    _cache.set(cacheKey, reactions);
    return reactions;
  }

  /// Clear all service catalog cache
  void clearCache() {
    _cache.clearByPattern('services');
    _cache.clearByPattern('actions_');
    _cache.clearByPattern('reactions_');
  }
}
