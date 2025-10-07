import 'package:flutter/material.dart';

/// Widget de carte pour la configuration du déclencheur (trigger)
/// Permet de sélectionner le service qui déclenchera l'automation
class TriggerConfigCard extends StatelessWidget {
  final String? selectedTrigger;
  final ValueChanged<String?> onChanged;

  const TriggerConfigCard({
    super.key,
    required this.selectedTrigger,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.play_arrow,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Trigger Configuration',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Semantics(
              label: 'Trigger service selection',
              hint: 'Select which service will trigger the automation',
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                value: selectedTrigger,
                decoration: InputDecoration(
                  labelText: 'Trigger Service',
                  hintText: 'Choose the service that will start the automation',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  prefixIcon: const Icon(Icons.sensors),
                  helperText: 'Select the service that will trigger your automation',
                ),
                items: ['Gmail', 'Discord', 'GitHub', 'Timer']
                    .map(
                      (service) => DropdownMenuItem(
                        value: service,
                        child: Row(
                          children: [
                            Icon(
                              _getServiceIcon(service),
                              size: 18,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 8),
                            Text(service),
                          ],
                        ),
                      ),
                    )
                    .toList(),
                onChanged: onChanged,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please select a trigger service';
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

  IconData _getServiceIcon(String service) {
    switch (service) {
      case 'Gmail':
        return Icons.email;
      case 'Discord':
        return Icons.chat;
      case 'GitHub':
        return Icons.code;
      case 'Timer':
        return Icons.schedule;
      default:
        return Icons.sensors;
    }
  }
}
