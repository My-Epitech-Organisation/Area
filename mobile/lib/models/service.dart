/// Model representing a service from the about.json endpoint
class Service {
  final int id;
  final String name;
  final bool requiresOAuth;
  final String? logo;
  final List<ServiceAction> actions;
  final List<ServiceReaction> reactions;

  Service({
    required this.id,
    required this.name,
    required this.requiresOAuth,
    this.logo,
    required this.actions,
    required this.reactions,
  });

  factory Service.fromJson(Map<String, dynamic> json) {
    return Service(
      id: json['id'] as int? ?? 0,
      name: (json['name'] as String?)?.trim() ?? '',
      requiresOAuth: (json['requires_oauth'] as bool?) ?? false,
      logo: (json['logo'] as String?),
      actions:
          (json['actions'] as List<dynamic>?)
              ?.map(
                (action) =>
                    ServiceAction.fromJson(action as Map<String, dynamic>),
              )
              .toList() ??
          [],
      reactions:
          (json['reactions'] as List<dynamic>?)
              ?.map(
                (reaction) =>
                    ServiceReaction.fromJson(reaction as Map<String, dynamic>),
              )
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'requires_oauth': requiresOAuth,
      'logo': logo,
      'actions': actions.map((action) => action.toJson()).toList(),
      'reactions': reactions.map((reaction) => reaction.toJson()).toList(),
    };
  }

  /// Get display name with proper capitalization
  String get displayName {
    if (name.isEmpty) return 'Unknown Service';

    return name
        .split('_')
        .map((word) {
          if (word.isEmpty) return '';
          return word[0].toUpperCase() + word.substring(1).toLowerCase();
        })
        .join(' ');
  }

  /// Get service icon path (placeholder for now)
  String get iconPath => 'assets/icons/${name.toLowerCase()}.png';
}

/// Model representing an action
class ServiceAction {
  final int id;
  final String name;
  final String description;
  final Map<String, dynamic>? configSchema;

  ServiceAction({
    required this.id,
    required this.name,
    required this.description,
    this.configSchema,
  });

  factory ServiceAction.fromJson(Map<String, dynamic> json) {
    return ServiceAction(
      id: json['id'] as int? ?? 0,
      name: (json['name'] as String?)?.trim() ?? '',
      description: (json['description'] as String?)?.trim() ?? '',
      configSchema: json['config_schema'] is Map<String, dynamic>
          ? json['config_schema'] as Map<String, dynamic>
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'config_schema': configSchema,
    };
  }

  /// Get display name with proper formatting
  String get displayName {
    if (name.isEmpty) return 'Unknown Action';
    return name
        .split('_')
        .map((word) {
          if (word.isEmpty) return '';
          return word[0].toUpperCase() + word.substring(1).toLowerCase();
        })
        .join(' ');
  }
}

/// Model representing a reaction
class ServiceReaction {
  final int id;
  final String name;
  final String description;
  final Map<String, dynamic>? configSchema;

  ServiceReaction({
    required this.id,
    required this.name,
    required this.description,
    this.configSchema,
  });

  factory ServiceReaction.fromJson(Map<String, dynamic> json) {
    return ServiceReaction(
      id: json['id'] as int? ?? 0,
      name: (json['name'] as String?)?.trim() ?? '',
      description: (json['description'] as String?)?.trim() ?? '',
      configSchema: json['config_schema'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'config_schema': configSchema,
    };
  }

  /// Get display name with proper formatting
  String get displayName {
    if (name.isEmpty) return 'Unknown Reaction';
    return name
        .split('_')
        .map((word) {
          if (word.isEmpty) return '';
          return word[0].toUpperCase() + word.substring(1).toLowerCase();
        })
        .join(' ');
  }
}
