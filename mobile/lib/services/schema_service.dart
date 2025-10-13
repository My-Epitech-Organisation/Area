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

  // Hardcoded schemas for known actions (fallback when API endpoints don't exist)
  static const Map<String, Map<String, dynamic>> _actionSchemas = {
    'timer_weekly': {
      'type': 'object',
      'properties': {
        'day_of_week': {
          'type': 'string',
          'enum': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
          'description': 'Day of the week for the timer'
        }
      },
      'required': ['day_of_week']
    },
    'timer_daily': {
      'type': 'object',
      'properties': {
        'hour': {
          'type': 'integer',
          'minimum': 0,
          'maximum': 23,
          'description': 'Hour of the day (0-23)'
        },
        'minute': {
          'type': 'integer',
          'minimum': 0,
          'maximum': 59,
          'description': 'Minute of the hour (0-59)'
        }
      },
      'required': ['hour', 'minute']
    },
    'github_new_issue': {
      'type': 'object',
      'properties': {
        'repository': {
          'type': 'string',
          'description': 'GitHub repository in format owner/repo'
        }
      },
      'required': ['repository']
    }
  };

  static const Map<String, Map<String, dynamic>> _reactionSchemas = {
    'github_create_issue': {
      'type': 'object',
      'properties': {
        'repository': {
          'type': 'string',
          'description': 'GitHub repository in format owner/repo'
        },
        'title': {
          'type': 'string',
          'description': 'Issue title'
        },
        'body': {
          'type': 'string',
          'description': 'Issue body'
        }
      },
      'required': ['repository', 'title']
    },
    'webhook_post': {
      'type': 'object',
      'properties': {
        'url': {
          'type': 'string',
          'description': 'Webhook URL'
        },
        'method': {
          'type': 'string',
          'enum': ['POST', 'PUT', 'PATCH'],
          'default': 'POST'
        }
      },
      'required': ['url']
    },
    'send_email': {
      'type': 'object',
      'properties': {
        'to': {
          'type': 'string',
          'description': 'Recipient email address'
        },
        'subject': {
          'type': 'string',
          'description': 'Email subject'
        },
        'body': {
          'type': 'string',
          'description': 'Email body'
        }
      },
      'required': ['to', 'subject', 'body']
    }
  };

  /// Get action configuration schema
  Future<Map<String, dynamic>?> getActionSchema(String actionName) async {
    final cacheKey = 'action_schema_$actionName';

    // Check cache first
    final cached = _cache.get<Map<String, dynamic>>(cacheKey);
    if (cached != null) return cached;

    // Check hardcoded schemas first
    if (_actionSchemas.containsKey(actionName)) {
      final schema = _actionSchemas[actionName]!;
      _cache.set(cacheKey, schema);
      return schema;
    }

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
      // If schema endpoint doesn't exist, return null (will use basic form)
      return null;
    }
  }

  /// Get reaction configuration schema
  Future<Map<String, dynamic>?> getReactionSchema(String reactionName) async {
    final cacheKey = 'reaction_schema_$reactionName';

    // Check cache first
    final cached = _cache.get<Map<String, dynamic>>(cacheKey);
    if (cached != null) return cached;

    // Check hardcoded schemas first
    if (_reactionSchemas.containsKey(reactionName)) {
      final schema = _reactionSchemas[reactionName]!;
      _cache.set(cacheKey, schema);
      return schema;
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
      // If schema endpoint doesn't exist, return null (will use basic form)
      return null;
    }
  }

  /// Clear all schema cache
  void clearCache() {
    _cache.clearByPattern('action_schema_');
    _cache.clearByPattern('reaction_schema_');
  }
}