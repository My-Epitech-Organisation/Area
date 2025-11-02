import 'package:flutter/material.dart';
import 'service_action_selector_card.dart';

class ActionConfigCard extends StatelessWidget {
  final String? selectedService;
  final String? selectedReaction;
  final String? selectedTriggerAction; // For reaction filtering
  final ValueChanged<String?> onServiceChanged;
  final ValueChanged<String?> onReactionChanged;

  const ActionConfigCard({
    super.key,
    required this.selectedService,
    required this.selectedReaction,
    required this.onServiceChanged,
    required this.onReactionChanged,
    this.selectedTriggerAction,
  });

  @override
  Widget build(BuildContext context) {
    return ServiceActionSelectorCard(
      title: 'Action Configuration',
      titleIcon: Icons.bolt,
      selectorType: SelectorType.action,
      selectedService: selectedService,
      selectedAction: selectedReaction,
      selectedTriggerAction: selectedTriggerAction,
      onServiceChanged: onServiceChanged,
      onActionChanged: onReactionChanged,
    );
  }
}
