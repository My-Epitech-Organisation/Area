import 'package:flutter/foundation.dart';

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
    try {
      return ServiceData(
        id: json['id'] ?? 0,
        name: json['name'] ?? 'Unknown Service',
        description: json['description'] ?? 'Service loaded from backend',
        status: json['status'] ?? 'active',
      );
    } catch (e, stackTrace) {
      debugPrint('❌ ERROR in ServiceData.fromJson: $e');
      debugPrint('📊 JSON data: $json');
      debugPrint('📚 Stack trace: $stackTrace');
      rethrow;
    }
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

  factory ActionData.fromJson(dynamic json) {
    // Handle both formats: full object or just ID
    if (json is Map<String, dynamic>) {
      try {
        ServiceData serviceData;
        if (json['service'] != null) {
          serviceData = ServiceData.fromJson(json['service']);
        } else if (json['service_id'] != null || json['service_name'] != null) {
          serviceData = ServiceData(
            id: json['service_id'] ?? 0,
            name: json['service_name'] ?? 'Unknown Service',
            description: 'Service loaded from backend',
            status: 'active',
          );
        } else {
          serviceData = ServiceData(
            id: 0,
            name: 'Unknown Service',
            description: 'Service loaded from backend',
            status: 'active',
          );
        }

        return ActionData(
          id: json['id'],
          name: json['name'] ?? 'Unknown Action',
          description: json['description'] ?? 'Action loaded from backend',
          service: serviceData,
        );
      } catch (e) {
        debugPrint('[APPLETS] ❌ Parse error: $e');
        debugPrint('[APPLETS] Action JSON: $json');
        rethrow;
      }
    } else if (json is int) {
      // Backend returns just the ID - create minimal object
      return ActionData(
        id: json,
        name: 'Unknown Action',
        description: 'Action loaded from backend',
        service: ServiceData(
          id: 0,
          name: 'Unknown Service',
          description: 'Service loaded from backend',
          status: 'active',
        ),
      );
    } else {
      debugPrint(
        '[APPLETS] ❌ Invalid action format: $json (type: ${json.runtimeType})',
      );
      throw FormatException('Invalid action data format: $json');
    }
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

  factory ReactionData.fromJson(dynamic json) {
    // Handle both formats: full object or just ID
    if (json is Map<String, dynamic>) {
      try {
        ServiceData serviceData;
        if (json['service'] != null) {
          serviceData = ServiceData.fromJson(json['service']);
        } else if (json['service_id'] != null || json['service_name'] != null) {
          serviceData = ServiceData(
            id: json['service_id'] ?? 0,
            name: json['service_name'] ?? 'Unknown Service',
            description: 'Service loaded from backend',
            status: 'active',
          );
        } else {
          serviceData = ServiceData(
            id: 0,
            name: 'Unknown Service',
            description: 'Service loaded from backend',
            status: 'active',
          );
        }

        return ReactionData(
          id: json['id'],
          name: json['name'] ?? 'Unknown Reaction',
          description: json['description'] ?? 'Reaction loaded from backend',
          service: serviceData,
        );
      } catch (e) {
        debugPrint('[APPLETS] ❌ Parse error: $e');
        debugPrint('[APPLETS] Reaction JSON: $json');
        rethrow;
      }
    } else if (json is int) {
      // Backend returns just the ID - create minimal object
      return ReactionData(
        id: json,
        name: 'Unknown Reaction',
        description: 'Reaction loaded from backend',
        service: ServiceData(
          id: 0,
          name: 'Unknown Service',
          description: 'Service loaded from backend',
          status: 'active',
        ),
      );
    } else {
      debugPrint(
        '❌ ERROR: Invalid reaction data format: $json (type: ${json.runtimeType})',
      );
      throw FormatException('Invalid reaction data format: $json');
    }
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
  final ActionData action;
  final ReactionData reaction;
  final Map<String, dynamic> actionConfig;
  final Map<String, dynamic> reactionConfig;
  final String status; // "active", "disabled", "paused"
  final DateTime createdAt;

  Applet({
    required this.id,
    required this.name,
    required this.action,
    required this.reaction,
    required this.actionConfig,
    required this.reactionConfig,
    required this.status,
    required this.createdAt,
  });

  // Factory to create from JSON (backend format)
  factory Applet.fromJson(Map<String, dynamic> json) {
    try {
      final actionData = json['action_detail'] ?? json['action'];
      final reactionData = json['reaction_detail'] ?? json['reaction'];

      return Applet(
        id: json['id'],
        name: json['name'] ?? '',
        action: ActionData.fromJson(actionData),
        reaction: ReactionData.fromJson(reactionData),
        actionConfig: json['action_config'] ?? {},
        reactionConfig: json['reaction_config'] ?? {},
        status: json['status'] ?? 'active',
        createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String(),
        ),
      );
    } catch (e, stackTrace) {
      debugPrint('[APPLETS] ❌ Parse error: $e');
      debugPrint('[APPLETS] JSON: $json');
      debugPrint('📚 Stack trace: $stackTrace');
      rethrow;
    }
  }

  // Convert to JSON for backend
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
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

  /// Create a copy of this applet with enriched action/reaction data
  /// This is useful when the backend returns only IDs and we need to enrich with service data
  Applet copyWithEnrichedData({
    required String? actionName,
    required String? actionDescription,
    required String? actionServiceName,
    required String? reactionName,
    required String? reactionDescription,
    required String? reactionServiceName,
  }) {
    final enrichedAction = ActionData(
      id: action.id,
      name: actionName ?? action.name,
      description: actionDescription ?? action.description,
      service: ServiceData(
        id: action.service.id,
        name: actionServiceName ?? action.service.name,
        description: action.service.description,
        status: action.service.status,
      ),
    );

    final enrichedReaction = ReactionData(
      id: reaction.id,
      name: reactionName ?? reaction.name,
      description: reactionDescription ?? reaction.description,
      service: ServiceData(
        id: reaction.service.id,
        name: reactionServiceName ?? reaction.service.name,
        description: reaction.service.description,
        status: reaction.service.status,
      ),
    );

    return Applet(
      id: id,
      name: name,
      action: enrichedAction,
      reaction: enrichedReaction,
      actionConfig: actionConfig,
      reactionConfig: reactionConfig,
      status: status,
      createdAt: createdAt,
    );
  }
}
