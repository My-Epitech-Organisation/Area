import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';
import '../models/service.dart';

/// Service responsible for service catalog (services, actions, reactions)
class ServiceCatalogService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final ServiceCatalogService _instance = ServiceCatalogService._internal();
  factory ServiceCatalogService() => _instance;
  ServiceCatalogService._internal();

  /// Get all available services from about.json
  Future<List<Service>> getAvailableServices({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'services';

    if (!forceRefresh) {
      final cached = _cache.get<List<Service>>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(ApiConfig.aboutUrl);

    final aboutData = _httpClient.parseResponse<Map<String, dynamic>>(
      response,
      (data) => data as Map<String, dynamic>,
    );

    final serverData = aboutData['server'] as Map<String, dynamic>?;
    if (serverData == null) {
      throw Exception('Invalid about.json format: missing server data');
    }

    final servicesData = serverData['services'] as List<dynamic>?;
    if (servicesData == null) {
      throw Exception('Invalid about.json format: missing services data');
    }

    final services = servicesData
        .map((item) => Service.fromJson(item as Map<String, dynamic>))
        .toList();

    _cache.set(cacheKey, services);
    return services;
  }

  /// Clear all service catalog cache
  void clearCache() {
    _cache.clearByPattern('services');
  }
}
