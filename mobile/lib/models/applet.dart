class Applet {
  final int id;
  final String name;
  final String description;
  final String triggerService;
  final String actionService;
  final bool isActive;

  Applet({
    required this.id,
    required this.name,
    required this.description,
    required this.triggerService,
    required this.actionService,
    required this.isActive,
  });

  // Factory to create from JSON
  factory Applet.fromJson(Map<String, dynamic> json) {
    return Applet(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      triggerService: json['trigger_service'],
      actionService: json['action_service'],
      isActive: json['is_active'],
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'trigger_service': triggerService,
      'action_service': actionService,
      'is_active': isActive,
    };
  }
}