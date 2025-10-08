import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/service_catalog_provider.dart';
import '../../utils/service_icons.dart';

class ActionConfigCard extends StatelessWidget {
  final String? selectedService;
  final String? selectedReaction;
  final ValueChanged<String?> onServiceChanged;
  final ValueChanged<String?> onReactionChanged;

  const ActionConfigCard({
    super.key,
    required this.selectedService,
    required this.selectedReaction,
    required this.onServiceChanged,
    required this.onReactionChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<ServiceCatalogProvider>(
      builder: (context, serviceProvider, child) {
        // Filter services that have reactions (actions)
        final actionServices = serviceProvider.services
            .where((service) => service.reactions.isNotEmpty)
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
                      Icons.bolt,
                      color: Theme.of(context).colorScheme.primary,
                    ),
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

                // Service Selection
                Semantics(
                  label: 'Action service selection',
                  hint: 'Select the service that will execute the action',
                  child: DropdownButtonFormField<String>(
                    isExpanded: true,
                    initialValue: selectedService,
                    decoration: InputDecoration(
                      labelText: 'Action Service',
                      hintText: 'Choose the executing service',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      prefixIcon: const Icon(Icons.call_to_action),
                      helperText:
                          'Select the service that will execute the action',
                    ),
                    items: actionServices.map((service) {
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
                        return 'Please select an action service';
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 16),

                // Reaction Selection - Only show when service is selected
                if (selectedService != null)
                  Semantics(
                    label: 'Reaction selection',
                    hint:
                        'Select the action that the automation should perform',
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      initialValue: selectedReaction,
                      decoration: InputDecoration(
                        labelText: 'Reaction',
                        hintText: 'Choose the action to perform',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        prefixIcon: const Icon(Icons.flash_on),
                        helperText:
                            'Select the action that your automation should perform',
                      ),
                      items:
                          serviceProvider
                              .getReactionsForService(selectedService!)
                              ?.map((reaction) {
                                return DropdownMenuItem(
                                  value: reaction.name,
                                  child: Text(reaction.displayName),
                                );
                              })
                              .toList() ??
                          [],
                      onChanged: onReactionChanged,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please select a reaction';
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
