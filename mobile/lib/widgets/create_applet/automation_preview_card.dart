import 'package:flutter/material.dart';
import '../../utils/service_icons.dart';

/// Visual preview card showing the configured automation flow
class AutomationPreviewCard extends StatelessWidget {
  final String? triggerServiceName;
  final String? triggerActionName;
  final Map<String, dynamic> actionConfig;
  final String? reactionServiceName;
  final String? reactionActionName;
  final Map<String, dynamic> reactionConfig;

  const AutomationPreviewCard({
    super.key,
    this.triggerServiceName,
    this.triggerActionName,
    this.actionConfig = const {},
    this.reactionServiceName,
    this.reactionActionName,
    this.reactionConfig = const {},
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Don't show if nothing is configured
    if (triggerServiceName == null && reactionServiceName == null) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              theme.colorScheme.primaryContainer.withValues(alpha: 0.3),
              theme.colorScheme.secondaryContainer.withValues(alpha: 0.3),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.preview,
                    color: theme.colorScheme.primary,
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Automation Preview',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Visual flow diagram
              Row(
                children: [
                  // Trigger side
                  Expanded(child: _buildTriggerSection(context)),

                  // Arrow
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Icon(
                      Icons.arrow_forward,
                      size: 32,
                      color: theme.colorScheme.primary,
                    ),
                  ),

                  // Reaction side
                  Expanded(child: _buildReactionSection(context)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTriggerSection(BuildContext context) {
    final theme = Theme.of(context);

    if (triggerServiceName == null) {
      return _buildEmptySection(
        context,
        'Select trigger',
        Icons.play_circle_outline,
      );
    }

    return Column(
      children: [
        // Service icon and name
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              Icon(
                ServiceIcons.getServiceIcon(triggerServiceName!),
                size: 32,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 8),
              Text(
                _formatServiceName(triggerServiceName!),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),

        const SizedBox(height: 8),

        // Action name
        if (triggerActionName != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              _formatActionName(triggerActionName!),
              style: theme.textTheme.bodySmall,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),

        // Config summary
        if (actionConfig.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: _buildConfigSummary(context, actionConfig),
          ),
      ],
    );
  }

  Widget _buildReactionSection(BuildContext context) {
    final theme = Theme.of(context);

    if (reactionServiceName == null) {
      return _buildEmptySection(context, 'Select action', Icons.flash_on);
    }

    return Column(
      children: [
        // Service icon and name
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              Icon(
                ServiceIcons.getServiceIcon(reactionServiceName!),
                size: 32,
                color: theme.colorScheme.secondary,
              ),
              const SizedBox(height: 8),
              Text(
                _formatServiceName(reactionServiceName!),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),

        const SizedBox(height: 8),

        // Reaction name
        if (reactionActionName != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: theme.colorScheme.secondaryContainer,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              _formatActionName(reactionActionName!),
              style: theme.textTheme.bodySmall,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),

        // Config summary
        if (reactionConfig.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: _buildConfigSummary(context, reactionConfig),
          ),
      ],
    );
  }

  Widget _buildEmptySection(BuildContext context, String text, IconData icon) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withValues(alpha: 0.3),
          width: 2,
          style: BorderStyle.solid,
        ),
      ),
      child: Column(
        children: [
          Icon(icon, size: 32, color: theme.colorScheme.outline),
          const SizedBox(height: 8),
          Text(
            text,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
              fontStyle: FontStyle.italic,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildConfigSummary(
    BuildContext context,
    Map<String, dynamic> config,
  ) {
    final theme = Theme.of(context);

    // Show only first 2 config items
    final entries = config.entries.take(2).toList();

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ...entries.map((entry) {
            final value = entry.value.toString();
            final displayValue = value.length > 20
                ? '${value.substring(0, 20)}...'
                : value;

            return Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Row(
                children: [
                  Icon(
                    Icons.check_circle,
                    size: 12,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      '${_formatFieldName(entry.key)}: $displayValue',
                      style: theme.textTheme.bodySmall?.copyWith(fontSize: 10),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            );
          }),
          if (config.length > 2)
            Text(
              '+${config.length - 2} more',
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 10,
                fontStyle: FontStyle.italic,
                color: theme.colorScheme.outline,
              ),
            ),
        ],
      ),
    );
  }

  String _formatServiceName(String name) {
    // Convert service_name to Service Name
    return name
        .split('_')
        .map((word) {
          return word.isEmpty ? '' : word[0].toUpperCase() + word.substring(1);
        })
        .join(' ');
  }

  String _formatActionName(String name) {
    // Convert action_name to Action Name
    return name
        .split('_')
        .map((word) {
          return word.isEmpty ? '' : word[0].toUpperCase() + word.substring(1);
        })
        .join(' ');
  }

  String _formatFieldName(String name) {
    // Convert field_name to Field Name
    return name
        .split('_')
        .map((word) {
          return word.isEmpty ? '' : word[0].toUpperCase() + word.substring(1);
        })
        .join(' ');
  }
}
