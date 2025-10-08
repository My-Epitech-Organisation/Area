import 'package:flutter/material.dart';

class ActionConfigCard extends StatelessWidget {
  final String? selectedAction;
  final ValueChanged<String?> onChanged;

  const ActionConfigCard({
    super.key,
    required this.selectedAction,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.bolt, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Action Configuration',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Semantics(
              label: 'Action selection',
              hint: 'Select what action the automation should perform',
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                initialValue: selectedAction,
                decoration: InputDecoration(
                  labelText: 'Action',
                  hintText:
                      'Choose what the automation should do when triggered',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  prefixIcon: const Icon(Icons.call_to_action),
                  helperText: 'Select the action your automation will perform',
                ),
                items: ['Send message', 'Create task', 'Notify']
                    .map(
                      (action) => DropdownMenuItem(
                        value: action,
                        child: Row(
                          children: [
                            Icon(
                              _getActionIcon(action),
                              size: 18,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 8),
                            Text(action),
                          ],
                        ),
                      ),
                    )
                    .toList(),
                onChanged: onChanged,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please select an action';
                  }
                  return null;
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getActionIcon(String action) {
    switch (action) {
      case 'Send message':
        return Icons.send;
      case 'Create task':
        return Icons.task;
      case 'Notify':
        return Icons.notifications;
      default:
        return Icons.call_to_action;
    }
  }
}
