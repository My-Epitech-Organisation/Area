import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/service_catalog_provider.dart';
import '../../providers/connected_services_provider.dart';
import '../../utils/service_icons.dart';
import '../../config/service_provider_config.dart';

enum SelectorType { trigger, action }

/// Generic card for selecting a service and then an action/reaction from that service
class ServiceActionSelectorCard extends StatefulWidget {
  final String title;
  final IconData titleIcon;
  final SelectorType selectorType;
  final String? selectedService;
  final String? selectedAction;
  final ValueChanged<String?> onServiceChanged;
  final ValueChanged<String?> onActionChanged;
  final bool filterByConnectedServices;

  const ServiceActionSelectorCard({
    super.key,
    required this.title,
    required this.titleIcon,
    required this.selectorType,
    required this.selectedService,
    required this.selectedAction,
    required this.onServiceChanged,
    required this.onActionChanged,
    this.filterByConnectedServices = true,
  });

  @override
  State<ServiceActionSelectorCard> createState() =>
      _ServiceActionSelectorCardState();
}

class _ServiceActionSelectorCardState extends State<ServiceActionSelectorCard> {
  bool _showOnlyConnected = true;

  @override
  Widget build(BuildContext context) {
    return Consumer2<ServiceCatalogProvider, ConnectedServicesProvider>(
      builder: (context, serviceProvider, connectedProvider, child) {
        // Filter services based on selector type
        var filteredServices = serviceProvider.services
            .where(
              (service) => widget.selectorType == SelectorType.trigger
                  ? service.actions.isNotEmpty
                  : service.reactions.isNotEmpty,
            )
            .toList();

        // Further filter by connected services if enabled
        if (widget.filterByConnectedServices && _showOnlyConnected) {
          filteredServices = filteredServices.where((service) {
            // Services that don't require OAuth are always available
            if (!ServiceProviderConfig.requiresOAuth(service.name)) {
              return true;
            }
            // OAuth services must be connected
            return connectedProvider.isServiceConnected(service.name);
          }).toList();
        }

        // Get labels and icons based on selector type
        final serviceLabel = widget.selectorType == SelectorType.trigger
            ? 'Trigger Service'
            : 'Action Service';
        final serviceHint = widget.selectorType == SelectorType.trigger
            ? 'Choose the triggering service'
            : 'Choose the executing service';
        final serviceHelperText = widget.selectorType == SelectorType.trigger
            ? 'Select the service that will trigger your automation'
            : 'Select the service that will execute the action';
        final serviceIcon = widget.selectorType == SelectorType.trigger
            ? Icons.sensors
            : Icons.call_to_action;

        final actionLabel = widget.selectorType == SelectorType.trigger
            ? 'Action Trigger'
            : 'Reaction';
        final actionHint = widget.selectorType == SelectorType.trigger
            ? 'Choose the triggering action'
            : 'Choose the action to perform';
        final actionHelperText = widget.selectorType == SelectorType.trigger
            ? 'Select the action that will trigger your automation'
            : 'Select the action that your automation should perform';
        final actionIcon = widget.selectorType == SelectorType.trigger
            ? Icons.play_circle_outline
            : Icons.flash_on;

        final serviceValidatorMessage =
            widget.selectorType == SelectorType.trigger
            ? 'Please select a trigger service'
            : 'Please select an action service';
        final actionValidatorMessage =
            widget.selectorType == SelectorType.trigger
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
                      widget.titleIcon,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        widget.title,
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w600),
                      ),
                    ),
                    // Toggle for filtering by connected services
                    if (widget.filterByConnectedServices)
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Connected only',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                          Switch(
                            value: _showOnlyConnected,
                            onChanged: (value) {
                              setState(() {
                                _showOnlyConnected = value;
                              });
                            },
                            activeThumbColor: Theme.of(
                              context,
                            ).colorScheme.primary,
                          ),
                        ],
                      ),
                  ],
                ),

                // Info banner when filter is on but no services match
                if (widget.filterByConnectedServices &&
                    _showOnlyConnected &&
                    filteredServices.isEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 12, bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.warning_amber_rounded,
                          color: Theme.of(context).colorScheme.error,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'No connected services available. Please connect a service or turn off the filter.',
                            style: Theme.of(context).textTheme.bodySmall
                                ?.copyWith(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onErrorContainer,
                                ),
                          ),
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 16),

                // Service Selection
                Semantics(
                  label: '${widget.title} service selection',
                  hint: serviceHelperText,
                  child: DropdownButtonFormField<String>(
                    isExpanded: true,
                    initialValue: widget.selectedService,
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
                      final isConnected = connectedProvider.isServiceConnected(
                        service.name,
                      );
                      final requiresOAuth = ServiceProviderConfig.requiresOAuth(
                        service.name,
                      );

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
                            Expanded(child: Text(service.displayName)),
                            if (requiresOAuth && isConnected)
                              Icon(
                                Icons.check_circle,
                                size: 16,
                                color: Colors.green,
                              ),
                          ],
                        ),
                      );
                    }).toList(),
                    onChanged: widget.onServiceChanged,
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
                if (widget.selectedService != null)
                  Semantics(
                    label: '${widget.title} action selection',
                    hint: actionHelperText,
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      initialValue: widget.selectedAction,
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
                          (widget.selectorType == SelectorType.trigger
                              ? serviceProvider
                                    .getActionsForService(
                                      widget.selectedService!,
                                    )
                                    ?.map((action) {
                                      return DropdownMenuItem(
                                        value: action.name,
                                        child: Text(action.displayName),
                                      );
                                    })
                                    .toList()
                              : serviceProvider
                                    .getReactionsForService(
                                      widget.selectedService!,
                                    )
                                    ?.map((reaction) {
                                      return DropdownMenuItem(
                                        value: reaction.name,
                                        child: Text(reaction.displayName),
                                      );
                                    })
                                    .toList()) ??
                          [],
                      onChanged: widget.onActionChanged,
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
