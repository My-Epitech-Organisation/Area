import '../config/api_config.dart';
import 'http_client_service.dart';
import 'cache_service.dart';
import '../models/service.dart';

/// Service responsible for service catalog (services, actions, reactions)
class ServiceCatalogService {
  final HttpClientService _httpClient = HttpClientService();
  final CacheService _cache = CacheService();

  // Singleton pattern
  static final ServiceCatalogService _instance =
      ServiceCatalogService._internal();
  factory ServiceCatalogService() => _instance;
  ServiceCatalogService._internal();

  /// Get all available services from API
  Future<List<Service>> getAvailableServices({
    bool forceRefresh = false,
  }) async {
    const cacheKey = 'services';

    if (!forceRefresh) {
      final cached = _cache.get<List<Service>>(cacheKey);
      if (cached != null) return cached;
    }

    // Get services
    final servicesResponse = await _httpClient.get(ApiConfig.servicesUrl);
    final servicesData = _httpClient.parseResponse<List<dynamic>>(
      servicesResponse,
      (data) => data as List<dynamic>,
    );

    // Get all actions
    final actionsResponse = await _httpClient.get(ApiConfig.actionsUrl);
    final actionsData = _httpClient.parseResponse<List<dynamic>>(
      actionsResponse,
      (data) => data as List<dynamic>,
    );

    // Get all reactions
    final reactionsResponse = await _httpClient.get(ApiConfig.reactionsUrl);
    final reactionsData = _httpClient.parseResponse<List<dynamic>>(
      reactionsResponse,
      (data) => data as List<dynamic>,
    );

    // Group actions and reactions by service
    final actionsByService = <int, List<ServiceAction>>{};
    final reactionsByService = <int, List<ServiceReaction>>{};

    for (final actionJson in actionsData) {
      final action = ServiceAction.fromJson(actionJson);
      final serviceId = actionJson['service_id'] as int;
      actionsByService.putIfAbsent(serviceId, () => []).add(action);
    }

    for (final reactionJson in reactionsData) {
      final reaction = ServiceReaction.fromJson(reactionJson);
      final serviceId = reactionJson['service_id'] as int;
      reactionsByService.putIfAbsent(serviceId, () => []).add(reaction);
    }

    // Create services with their actions and reactions
    final services = servicesData.map((serviceJson) {
      final serviceId = serviceJson['id'] as int;
      return Service(
        id: serviceId,
        name: serviceJson['name'] as String,
        actions: actionsByService[serviceId] ?? [],
        reactions: reactionsByService[serviceId] ?? [],
      );
    }).toList();

    _cache.set(cacheKey, services);
    return services;
  }

  /// Clear all service catalog cache
  void clearCache() {
    _cache.clearByPattern('services');
  }
}
