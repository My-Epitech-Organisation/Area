import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/service_catalog_provider.dart';
import '../../utils/service_icons.dart';

enum SelectorType { trigger, action }

/// Generic card for selecting a service and then an action/reaction from that service
class ServiceActionSelectorCard extends StatelessWidget {
  final String title;
  final IconData titleIcon;
  final SelectorType selectorType;
  final String? selectedService;
  final String? selectedAction;
  final ValueChanged<String?> onServiceChanged;
  final ValueChanged<String?> onActionChanged;

  const ServiceActionSelectorCard({
    super.key,
    required this.title,
    required this.titleIcon,
    required this.selectorType,
    required this.selectedService,
    required this.selectedAction,
    required this.onServiceChanged,
    required this.onActionChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<ServiceCatalogProvider>(
      builder: (context, serviceProvider, child) {
        // Filter services based on selector type
        final filteredServices = serviceProvider.services
            .where(
              (service) => selectorType == SelectorType.trigger
                  ? service.actions.isNotEmpty
                  : service.reactions.isNotEmpty,
            )
            .toList();

        // Get labels and icons based on selector type
        final serviceLabel = selectorType == SelectorType.trigger
            ? 'Trigger Service'
            : 'Action Service';
        final serviceHint = selectorType == SelectorType.trigger
            ? 'Choose the triggering service'
            : 'Choose the executing service';
        final serviceHelperText = selectorType == SelectorType.trigger
            ? 'Select the service that will trigger your automation'
            : 'Select the service that will execute the action';
        final serviceIcon = selectorType == SelectorType.trigger
            ? Icons.sensors
            : Icons.call_to_action;

        final actionLabel = selectorType == SelectorType.trigger
            ? 'Action Trigger'
            : 'Reaction';
        final actionHint = selectorType == SelectorType.trigger
            ? 'Choose the triggering action'
            : 'Choose the action to perform';
        final actionHelperText = selectorType == SelectorType.trigger
            ? 'Select the action that will trigger your automation'
            : 'Select the action that your automation should perform';
        final actionIcon = selectorType == SelectorType.trigger
            ? Icons.play_circle_outline
            : Icons.flash_on;

        final serviceValidatorMessage = selectorType == SelectorType.trigger
            ? 'Please select a trigger service'
            : 'Please select an action service';
        final actionValidatorMessage = selectorType == SelectorType.trigger
            ? 'Please select a trigger action'
            : 'Please select a reaction';

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
                      titleIcon,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Service Selection
                Semantics(
                  label: '$title service selection',
                  hint: serviceHelperText,
                  child: DropdownButtonFormField<String>(
                    isExpanded: true,
                    initialValue: selectedService,
                    decoration: InputDecoration(
                      labelText: serviceLabel,
                      hintText: serviceHint,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      prefixIcon: Icon(serviceIcon),
                      helperText: serviceHelperText,
                    ),
                    items: filteredServices.map((service) {
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
                        return serviceValidatorMessage;
                      }
                      return null;
                    },
                  ),
                ),

                const SizedBox(height: 16),

                // Action/Reaction Selection - Only show when service is selected
                if (selectedService != null)
                  Semantics(
                    label: '$title action selection',
                    hint: actionHelperText,
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      initialValue: selectedAction,
                      decoration: InputDecoration(
                        labelText: actionLabel,
                        hintText: actionHint,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        prefixIcon: Icon(actionIcon),
                        helperText: actionHelperText,
                      ),
                      items:
                          (selectorType == SelectorType.trigger
                              ? serviceProvider
                                    .getActionsForService(selectedService!)
                                    ?.map((action) {
                                      return DropdownMenuItem(
                                        value: action.name,
                                        child: Text(action.displayName),
                                      );
                                    })
                                    .toList()
                              : serviceProvider
                                    .getReactionsForService(selectedService!)
                                    ?.map((reaction) {
                                      return DropdownMenuItem(
                                        value: reaction.name,
                                        child: Text(reaction.displayName),
                                      );
                                    })
                                    .toList()) ??
                          [],
                      onChanged: onActionChanged,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return actionValidatorMessage;
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
