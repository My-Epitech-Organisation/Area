import 'package:flutter/material.dart';
import 'service_action_selector_card.dart';

class TriggerConfigCard extends StatelessWidget {
  final String? selectedService;
  final String? selectedAction;
  final ValueChanged<String?> onServiceChanged;
  final ValueChanged<String?> onActionChanged;

  const TriggerConfigCard({
    super.key,
    required this.selectedService,
    required this.selectedAction,
    required this.onServiceChanged,
    required this.onActionChanged,
  });

  @override
  Widget build(BuildContext context) {
    return ServiceActionSelectorCard(
      title: 'Trigger Configuration',
      titleIcon: Icons.play_arrow,
      selectorType: SelectorType.trigger,
      selectedService: selectedService,
      selectedAction: selectedAction,
      onServiceChanged: onServiceChanged,
      onActionChanged: onActionChanged,
    );
  }
}
