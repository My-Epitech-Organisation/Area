import 'package:flutter/material.dart';
import 'dynamic_config_form.dart';

class ConfigStepCard extends StatefulWidget {
  final String selectedActionName;
  final String selectedReactionName;
  final Map<String, dynamic> actionConfig;
  final Map<String, dynamic> reactionConfig;
  final ValueChanged<Map<String, dynamic>> onActionConfigChanged;
  final ValueChanged<Map<String, dynamic>> onReactionConfigChanged;
  final ValueChanged<bool Function()>? onValidationChanged;

  const ConfigStepCard({
    super.key,
    required this.selectedActionName,
    required this.selectedReactionName,
    required this.actionConfig,
    required this.reactionConfig,
    required this.onActionConfigChanged,
    required this.onReactionConfigChanged,
    this.onValidationChanged,
  });

  @override
  State<ConfigStepCard> createState() => _ConfigStepCardState();
}

class _ConfigStepCardState extends State<ConfigStepCard> {
  bool Function()? _validateForm;

  @override
  void initState() {
    super.initState();
    // Provide validation function to parent
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.onValidationChanged?.call(() => validate());
    });
  }

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
                Icon(
                  Icons.settings,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Configuration',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Configure the parameters for your automation',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            DynamicConfigForm(
              actionName: widget.selectedActionName,
              reactionName: widget.selectedReactionName,
              initialActionConfig: widget.actionConfig,
              initialReactionConfig: widget.reactionConfig,
              onActionConfigChanged: widget.onActionConfigChanged,
              onReactionConfigChanged: widget.onReactionConfigChanged,
              onValidationChanged: (validateFunction) {
                setState(() {
                  _validateForm = validateFunction;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  bool validate() {
    return _validateForm?.call() ?? false;
  }
}
