/// Model representing a service from the about.json endpoint
class Service {
  final String name;
  final List<ServiceAction> actions;
  final List<ServiceReaction> reactions;

  Service({
    required this.name,
    required this.actions,
    required this.reactions,
  });

  factory Service.fromJson(Map<String, dynamic> json) {
    return Service(
      name: (json['name'] as String?)?.trim() ?? '',
      actions: (json['actions'] as List<dynamic>?)
          ?.map((action) => ServiceAction.fromJson(action as Map<String, dynamic>))
          .toList() ?? [],
      reactions: (json['reactions'] as List<dynamic>?)
          ?.map((reaction) => ServiceReaction.fromJson(reaction as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'actions': actions.map((action) => action.toJson()).toList(),
      'reactions': reactions.map((reaction) => reaction.toJson()).toList(),
    };
  }

  /// Get display name with proper capitalization
  String get displayName {
    if (name.isEmpty) return 'Unknown Service';
    return name.split('_').map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  /// Get service icon path (placeholder for now)
  String get iconPath => 'assets/icons/${name.toLowerCase()}.png';
}

/// Model representing an action
class ServiceAction {
  final String name;
  final String description;

  ServiceAction({
    required this.name,
    required this.description,
  });

  factory ServiceAction.fromJson(Map<String, dynamic> json) {
    return ServiceAction(
      name: (json['name'] as String?)?.trim() ?? '',
      description: (json['description'] as String?)?.trim() ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'description': description,
    };
  }

  /// Get display name with proper formatting
  String get displayName {
    if (name.isEmpty) return 'Unknown Action';
    return name.split('_').map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }
}

/// Model representing a reaction
class ServiceReaction {
  final String name;
  final String description;

  ServiceReaction({
    required this.name,
    required this.description,
  });

  factory ServiceReaction.fromJson(Map<String, dynamic> json) {
    return ServiceReaction(
      name: (json['name'] as String?)?.trim() ?? '',
      description: (json['description'] as String?)?.trim() ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'description': description,
    };
  }

  /// Get display name with proper formatting
  String get displayName {
    if (name.isEmpty) return 'Unknown Reaction';
    return name.split('_').map((word) {
      if (word.isEmpty) return '';
      return word[0].toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }
}