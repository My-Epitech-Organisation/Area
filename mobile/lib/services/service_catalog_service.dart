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

    // Get services from about.json endpoint
    final servicesResponse = await _httpClient.get(ApiConfig.aboutUrl);
    final servicesData = _httpClient.parseResponse<List<dynamic>>(
      servicesResponse,
      (data) {
        // Extract services from server.services
        if (data is Map && data.containsKey('server')) {
          final server = data['server'] as Map<String, dynamic>;
          if (server.containsKey('services')) {
            return server['services'] as List<dynamic>;
          }
        }
        throw Exception('Unexpected about.json response format: $data');
      },
    );

    // Get real actions from API
    final actionsResponse = await _httpClient.get(ApiConfig.actionsUrl);
    final actionsData = _httpClient.parseResponse<List<dynamic>>(
      actionsResponse,
      (data) {
        // API returns paginated response: {"results": [...]}
        if (data is Map && data.containsKey('results')) {
          return data['results'] as List<dynamic>;
        }
        return data as List<dynamic>;
      },
    );

    // Get real reactions from API
    final reactionsResponse = await _httpClient.get(ApiConfig.reactionsUrl);
    final reactionsData = _httpClient.parseResponse<List<dynamic>>(
      reactionsResponse,
      (data) {
        // API returns paginated response: {"results": [...]}
        if (data is Map && data.containsKey('results')) {
          return data['results'] as List<dynamic>;
        }
        return data as List<dynamic>;
      },
    );

    // Group actions and reactions by service_id
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
    final serviceNameToId = <String, int>{};
    for (final action in actionsData) {
      final serviceName = action['service_name'] as String;
      final serviceId = action['service_id'] as int;
      serviceNameToId[serviceName] = serviceId;
    }
    for (final reaction in reactionsData) {
      final serviceName = reaction['service_name'] as String;
      final serviceId = reaction['service_id'] as int;
      serviceNameToId[serviceName] = serviceId;
    }

    final services = servicesData.map((serviceJson) {
      final serviceName = serviceJson['name'] as String;
      final serviceId = serviceNameToId[serviceName] ?? 0;
      return Service(
        id: serviceId,
        name: serviceName,
        requiresOAuth: (serviceJson['requires_oauth'] as bool?) ?? false,
        logo: (serviceJson['logo'] as String?),
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
