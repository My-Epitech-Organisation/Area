class ServiceData {
  final int id;
  final String name;
  final String description;
  final String status;

  ServiceData({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
  });

  factory ServiceData.fromJson(Map<String, dynamic> json) {
    return ServiceData(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      status: json['status'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'status': status,
    };
  }
}

class ActionData {
  final int id;
  final String name;
  final String description;
  final ServiceData service;

  ActionData({
    required this.id,
    required this.name,
    required this.description,
    required this.service,
  });

  factory ActionData.fromJson(Map<String, dynamic> json) {
    return ActionData(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      service: ServiceData.fromJson(json['service']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'service': service.toJson(),
    };
  }
}

class ReactionData {
  final int id;
  final String name;
  final String description;
  final ServiceData service;

  ReactionData({
    required this.id,
    required this.name,
    required this.description,
    required this.service,
  });

  factory ReactionData.fromJson(Map<String, dynamic> json) {
    return ReactionData(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      service: ServiceData.fromJson(json['service']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'service': service.toJson(),
    };
  }
}

class Applet {
  final int id;
  final String name;
  final String description;
  final ActionData action;
  final ReactionData reaction;
  final Map<String, dynamic> actionConfig;
  final Map<String, dynamic> reactionConfig;
  final String status; // "active", "disabled", "paused"
  final DateTime createdAt;

  Applet({
    required this.id,
    required this.name,
    required this.description,
    required this.action,
    required this.reaction,
    required this.actionConfig,
    required this.reactionConfig,
    required this.status,
    required this.createdAt,
  });

  // Factory to create from JSON (backend format)
  factory Applet.fromJson(Map<String, dynamic> json) {
    return Applet(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      action: ActionData.fromJson(json['action']),
      reaction: ReactionData.fromJson(json['reaction']),
      actionConfig: json['action_config'] ?? {},
      reactionConfig: json['reaction_config'] ?? {},
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  // Convert to JSON for backend
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'action': action.toJson(),
      'reaction': reaction.toJson(),
      'action_config': actionConfig,
      'reaction_config': reactionConfig,
      'status': status,
      'created_at': createdAt.toIso8601String(),
    };
  }

  // Computed properties for backward compatibility
  String get triggerService => action.service.name;
  String get actionService => reaction.service.name;
  bool get isActive => status == 'active';

  // Create from old format (for migration)
  factory Applet.fromOldFormat({
    required int id,
    required String name,
    required String description,
    required String triggerService,
    required String actionService,
    required bool isActive,
  }) {
    // Mock data for migration - in real app, this would fetch from API
    final mockAction = ActionData(
      id: 1,
      name: 'Mock Trigger',
      description: 'Mock trigger for migration',
      service: ServiceData(
        id: 1,
        name: triggerService,
        description: 'Mock service',
        status: 'active',
      ),
    );

    final mockReaction = ReactionData(
      id: 1,
      name: 'Mock Action',
      description: 'Mock action for migration',
      service: ServiceData(
        id: 2,
        name: actionService,
        description: 'Mock service',
        status: 'active',
      ),
    );

    return Applet(
      id: id,
      name: name,
      description: description,
      action: mockAction,
      reaction: mockReaction,
      actionConfig: {},
      reactionConfig: {},
      status: isActive ? 'active' : 'disabled',
      createdAt: DateTime.now(),
    );
  }
}