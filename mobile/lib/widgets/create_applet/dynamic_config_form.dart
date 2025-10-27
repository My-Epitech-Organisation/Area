import 'package:flutter/material.dart';
import 'config_field_widgets.dart';
import 'date_time_picker_widget.dart';
import 'time_picker_widget.dart';

/// Model representing a configuration field
class ConfigField {
  final String name;
  final String label;
  final String type;
  final String? description;
  final dynamic defaultValue;
  final bool required;
  final List<String>? enumValues;
  final Map<String, dynamic>? validation;

  ConfigField({
    required this.name,
    required this.label,
    required this.type,
    this.description,
    this.defaultValue,
    this.required = false,
    this.enumValues,
    this.validation,
  });

  factory ConfigField.fromSchemaProperty(
    String name,
    Map<String, dynamic> property,
  ) {
    final type = property['type'] as String? ?? 'string';
    final description = property['description'] as String?;
    final defaultValue = property['default'];
    final required = property['required'] as bool? ?? false;

    List<String>? enumValues;
    if (property['enum'] != null) {
      enumValues = (property['enum'] as List<dynamic>).cast<String>();
    }

    return ConfigField(
      name: name,
      label: _formatLabel(name),
      type: type,
      description: description,
      defaultValue: defaultValue,
      required: required,
      enumValues: enumValues,
      validation: property,
    );
  }

  static String _formatLabel(String name) {
    return name
        .split('_')
        .map(
          (word) => word.isEmpty
              ? ''
              : '${word[0].toUpperCase()}${word.substring(1)}',
        )
        .join(' ');
  }
}

/// Dynamic configuration form based on JSON schema
class DynamicConfigForm extends StatefulWidget {
  final String actionName;
  final String reactionName;
  final Map<String, dynamic>? actionConfigSchema;
  final Map<String, dynamic>? reactionConfigSchema;
  final Map<String, dynamic> initialActionConfig;
  final Map<String, dynamic> initialReactionConfig;
  final ValueChanged<Map<String, dynamic>> onActionConfigChanged;
  final ValueChanged<Map<String, dynamic>> onReactionConfigChanged;
  final ValueChanged<bool Function()>? onValidationChanged;

  const DynamicConfigForm({
    super.key,
    required this.actionName,
    required this.reactionName,
    this.actionConfigSchema,
    this.reactionConfigSchema,
    required this.initialActionConfig,
    required this.initialReactionConfig,
    required this.onActionConfigChanged,
    required this.onReactionConfigChanged,
    this.onValidationChanged,
  });

  @override
  State<DynamicConfigForm> createState() => _DynamicConfigFormState();
}

class _DynamicConfigFormState extends State<DynamicConfigForm> {
  final _formKey = GlobalKey<FormState>();

  Map<String, dynamic> _actionConfig = {};
  Map<String, dynamic> _reactionConfig = {};

  @override
  void initState() {
    super.initState();
    _actionConfig = Map.from(widget.initialActionConfig);
    _reactionConfig = Map.from(widget.initialReactionConfig);

    // Defer validation function callback to after frame build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.onValidationChanged != null) {
        widget.onValidationChanged!(
          () => _formKey.currentState?.validate() ?? false,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Form(
        key: _formKey,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Action configuration
              if (widget.actionConfigSchema != null &&
                  widget.actionConfigSchema!.isNotEmpty)
                _buildSection(
                  context,
                  'Action Configuration',
                  widget.actionConfigSchema!,
                  _actionConfig,
                  widget.onActionConfigChanged,
                ),
              const SizedBox(height: 24),

              // Reaction configuration
              if (widget.reactionConfigSchema != null &&
                  widget.reactionConfigSchema!.isNotEmpty)
                _buildSection(
                  context,
                  'Reaction Configuration',
                  widget.reactionConfigSchema!,
                  _reactionConfig,
                  widget.onReactionConfigChanged,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    Map<String, dynamic> schema,
    Map<String, dynamic> config,
    ValueChanged<Map<String, dynamic>> onConfigChanged,
  ) {
    final properties = schema['properties'] as Map<String, dynamic>? ?? {};
    if (properties.isEmpty) return const SizedBox.shrink();

    final fields = properties.entries.map((e) {
      return ConfigField.fromSchemaProperty(e.key, e.value);
    }).toList();

    // Detect and combine hour/minute pairs
    final processedFields = <ConfigField>[];
    final processedNames = <String>{};

    for (final field in fields) {
      if (processedNames.contains(field.name)) continue;

      final fieldNameLower = field.name.toLowerCase();

      // Check if this is an hour field and if there's a corresponding minute field
      if (fieldNameLower.contains('hour')) {
        // Find corresponding minute field
        ConfigField? minuteField;
        try {
          final hourBase = fieldNameLower.replaceAll(RegExp(r'hour|_'), '');
          minuteField = fields.firstWhere((f) {
            final mName = f.name.toLowerCase();
            final minuteBase = mName.replaceAll(RegExp(r'minute|_'), '');
            return mName.contains('minute') && hourBase == minuteBase;
          });
        } catch (_) {
          minuteField = null;
        }

        if (minuteField != null) {
          // Add a combined time field marker
          processedNames.add(field.name);
          processedNames.add(minuteField.name);
          processedFields.add(field);
          processedFields.add(minuteField);
        } else {
          processedFields.add(field);
        }
      } else if (!fieldNameLower.contains('minute')) {
        processedFields.add(field);
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 16),
        ...processedFields.asMap().entries.map((entry) {
          final idx = entry.key;
          final field = entry.value;
          final nextField = idx + 1 < processedFields.length
              ? processedFields[idx + 1]
              : null;

          // Check if this is a combined hour/minute pair
          if (field.name.toLowerCase().contains('hour') &&
              nextField != null &&
              nextField.name.toLowerCase().contains('minute')) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildCombinedTimeField(
                field,
                nextField,
                config,
                onConfigChanged,
              ),
            );
          } else if (field.name.toLowerCase().contains('minute') &&
              idx > 0 &&
              processedFields[idx - 1].name.toLowerCase().contains('hour')) {
            // Skip this minute field as it's already handled by the hour field
            return const SizedBox.shrink();
          } else {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildField(field, config, onConfigChanged),
            );
          }
        }),
      ],
    );
  }

  Widget _buildField(
    ConfigField field,
    Map<String, dynamic> config,
    ValueChanged<Map<String, dynamic>> onConfigChanged,
  ) {
    final value = config[field.name] ?? field.defaultValue ?? '';

    return _buildFieldWidget(field, value, (newValue) {
      config[field.name] = newValue;
      onConfigChanged(config);
    });
  }

  Widget _buildCombinedTimeField(
    ConfigField hourField,
    ConfigField minuteField,
    Map<String, dynamic> config,
    ValueChanged<Map<String, dynamic>> onConfigChanged,
  ) {
    final hourValue = config[hourField.name] ?? hourField.defaultValue ?? 0;
    final minuteValue =
        config[minuteField.name] ?? minuteField.defaultValue ?? 0;

    final initialHour = hourValue is int
        ? hourValue
        : int.tryParse(hourValue.toString()) ?? 0;
    final initialMinute = minuteValue is int
        ? minuteValue
        : int.tryParse(minuteValue.toString()) ?? 0;

    return TimePickerField(
      label: 'Time',
      initialHour: initialHour.clamp(0, 23),
      initialMinute: initialMinute.clamp(0, 59),
      required: hourField.required || minuteField.required,
      onChanged: (hour, minute) {
        config[hourField.name] = hour;
        config[minuteField.name] = minute;
        onConfigChanged(config);
      },
    );
  }

  Widget _buildFieldWidget(
    ConfigField field,
    dynamic value,
    ValueChanged<dynamic> onChanged,
  ) {
    final fieldNameLower = field.name.toLowerCase();
    final fieldTypeLower = field.type.toLowerCase();

    // Specialized widgets
    if (fieldNameLower.contains('hour')) {
      return HourPickerWidget(
        label: field.label,
        description: field.description,
        initialValue: value is int ? value : int.tryParse(value.toString()),
        required: field.required,
        onChanged: onChanged,
      );
    }

    if (fieldNameLower.contains('minute')) {
      return MinutePickerWidget(
        label: field.label,
        description: field.description,
        initialValue: value is int ? value : int.tryParse(value.toString()),
        required: field.required,
        onChanged: onChanged,
      );
    }

    if (fieldNameLower.contains('timezone')) {
      return TimezoneField(
        label: field.label,
        value: value.toString(),
        required: field.required,
        onChanged: onChanged,
      );
    }

    // Check for datetime type from JSON schema (ISO 8601 dates)
    if (fieldTypeLower == 'datetime') {
      return DateTimePickerWidget(
        label: field.label,
        description: field.description,
        initialValue: value.toString(),
        required: field.required,
        onChanged: onChanged,
      );
    }

    if (fieldNameLower.contains('date') && fieldNameLower.contains('time')) {
      return DateTimePickerWidget(
        label: field.label,
        description: field.description,
        initialValue: value.toString(),
        required: field.required,
        onChanged: onChanged,
      );
    }

    if (fieldNameLower.contains('date')) {
      return DateField(
        label: field.label,
        value: value.toString(),
        required: field.required,
        onChanged: onChanged,
      );
    }

    // Enum dropdown
    if (field.enumValues != null && field.enumValues!.isNotEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${field.label}${field.required ? ' *' : ''}',
            style: Theme.of(context).textTheme.labelSmall,
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            initialValue: value.toString(),
            decoration: const InputDecoration(border: OutlineInputBorder()),
            items: field.enumValues!.map((val) {
              return DropdownMenuItem(value: val, child: Text(val));
            }).toList(),
            onChanged: (val) {
              if (val != null) onChanged(val);
            },
            validator: field.required
                ? (val) => val == null ? '${field.label} is required' : null
                : null,
          ),
        ],
      );
    }

    // Default text field
    return TextFormField(
      initialValue: value.toString(),
      decoration: InputDecoration(
        labelText: '${field.label}${field.required ? ' *' : ''}',
        border: const OutlineInputBorder(),
        helperText: field.description,
      ),
      keyboardType: fieldTypeLower == 'number'
          ? TextInputType.number
          : TextInputType.text,
      onChanged: onChanged,
      validator: field.required
          ? (val) => val?.isEmpty ?? true ? '${field.label} is required' : null
          : null,
    );
  }
}
