import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/service_catalog_provider.dart';
import '../../utils/service_icons.dart';

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
    return Consumer<ServiceCatalogProvider>(
      builder: (context, serviceProvider, child) {
        // Filter services that have actions (triggers)
        final triggerServices = serviceProvider.services
            .where((service) => service.actions.isNotEmpty)
            .toList();

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

                // Service Selection
                Semantics(
                  label: 'Trigger service selection',
                  hint: 'Select the service that will trigger the automation',
                  child: DropdownButtonFormField<String>(
                    isExpanded: true,
                    initialValue: selectedService,
                    decoration: InputDecoration(
                      labelText: 'Trigger Service',
                      hintText: 'Choose the triggering service',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      prefixIcon: const Icon(Icons.sensors),
                      helperText:
                          'Select the service that will trigger your automation',
                    ),
                    items: triggerServices.map((service) {
                      return DropdownMenuItem(
                        value: service.name,
                        child: Row(
                          children: [
                            Icon(
                              ServiceIcons.getServiceIcon(service.name),
                              size: 18,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 8),
                            Text(service.displayName),
                          ],
                        ),
                      );
                    }).toList(),
                    onChanged: onServiceChanged,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please select a trigger service';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 16),

                // Action Selection - Only show when service is selected
                if (selectedService != null)
                  Semantics(
                    label: 'Trigger action selection',
                    hint: 'Select the action that will trigger the automation',
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      initialValue: selectedAction,
                      decoration: InputDecoration(
                        labelText: 'Action Trigger',
                        hintText: 'Choose the triggering action',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        prefixIcon: const Icon(Icons.play_circle_outline),
                        helperText:
                            'Select the action that will trigger your automation',
                      ),
                      items:
                          serviceProvider
                              .getActionsForService(selectedService!)
                              ?.map((action) {
                                return DropdownMenuItem(
                                  value: action.name,
                                  child: Text(action.displayName),
                                );
                              })
                              .toList() ??
                          [],
                      onChanged: onActionChanged,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please select a trigger action';
                        }
                        return null;
                      },
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}
