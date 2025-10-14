import 'package:flutter/material.dart';
import '../../services/schema_service.dart';

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
  final Map<String, dynamic> initialActionConfig;
  final Map<String, dynamic> initialReactionConfig;
  final ValueChanged<Map<String, dynamic>> onActionConfigChanged;
  final ValueChanged<Map<String, dynamic>> onReactionConfigChanged;
  final ValueChanged<bool Function()>? onValidationChanged;

  const DynamicConfigForm({
    super.key,
    required this.actionName,
    required this.reactionName,
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
  final _schemaService = SchemaService();
  final _formKey = GlobalKey<FormState>();

  Map<String, dynamic> _actionConfig = {};
  Map<String, dynamic> _reactionConfig = {};

  Map<String, dynamic>? _actionSchema;
  Map<String, dynamic>? _reactionSchema;

  bool _loadingSchemas = true;

  @override
  void initState() {
    super.initState();
    _actionConfig = Map.from(widget.initialActionConfig);
    _reactionConfig = Map.from(widget.initialReactionConfig);
    // Provide validation function to parent
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.onValidationChanged?.call(() => validate());
    });
    _loadSchemas();
  }

  Future<void> _loadSchemas() async {
    try {
      final actionSchema = await _schemaService.getActionSchema(
        widget.actionName,
      );
      final reactionSchema = await _schemaService.getReactionSchema(
        widget.reactionName,
      );

      setState(() {
        _actionSchema = actionSchema;
        _reactionSchema = reactionSchema;
        _loadingSchemas = false;
      });
    } catch (e) {
      setState(() {
        _loadingSchemas = false;
      });
    }
  }

  List<ConfigField> _parseSchemaFields(Map<String, dynamic>? schema) {
    if (schema == null) return [];

    final properties = schema['properties'] as Map<String, dynamic>? ?? {};
    final required = schema['required'] as List<dynamic>? ?? [];

    return properties.entries.map((entry) {
      final property = Map<String, dynamic>.from(
        entry.value as Map<String, dynamic>,
      );
      property['required'] = required.contains(
        entry.key,
      ); // Check if field name is in required list
      return ConfigField.fromSchemaProperty(entry.key, property);
    }).toList();
  }

  Widget _buildConfigSection({
    required String title,
    required List<ConfigField> fields,
    required Map<String, dynamic> config,
    required ValueChanged<Map<String, dynamic>> onChanged,
  }) {
    if (fields.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'No configuration required for $title',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontStyle: FontStyle.italic,
              color: Colors.grey,
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            ...fields.map(
              (field) => _buildFieldWidget(field, config, onChanged),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFieldWidget(
    ConfigField field,
    Map<String, dynamic> config,
    ValueChanged<Map<String, dynamic>> onChanged,
  ) {
    final currentValue = config[field.name] ?? field.defaultValue ?? '';

    switch (field.type) {
      case 'string':
        if (field.enumValues != null && field.enumValues!.isNotEmpty) {
          // Dropdown for enum values
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: DropdownButtonFormField<String>(
              initialValue: currentValue.isNotEmpty ? currentValue : null,
              decoration: InputDecoration(
                labelText: field.label + (field.required ? ' *' : ''),
                hintText: field.description,
                border: const OutlineInputBorder(),
              ),
              items: field.enumValues!.map((value) {
                return DropdownMenuItem(value: value, child: Text(value));
              }).toList(),
              onChanged: (value) {
                config[field.name] = value ?? '';
                onChanged(config);
              },
              validator: field.required
                  ? (value) =>
                        value == null || value.isEmpty ? 'Required field' : null
                  : null,
            ),
          );
        } else {
          // Text field for strings
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: TextFormField(
              initialValue: currentValue,
              decoration: InputDecoration(
                labelText: field.label + (field.required ? ' *' : ''),
                hintText: field.description,
                border: const OutlineInputBorder(),
              ),
              onChanged: (value) {
                config[field.name] = value;
                onChanged(config);
              },
              validator: field.required
                  ? (value) =>
                        value == null || value.isEmpty ? 'Required field' : null
                  : null,
            ),
          );
        }

      case 'integer':
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: TextFormField(
            initialValue: currentValue.toString(),
            decoration: InputDecoration(
              labelText: field.label + (field.required ? ' *' : ''),
              hintText: field.description,
              border: const OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
            onChanged: (value) {
              final intValue = int.tryParse(value);
              if (intValue != null) {
                config[field.name] = intValue;
                onChanged(config);
              }
            },
            validator: (value) {
              if (field.required && (value == null || value.isEmpty)) {
                return 'Required field';
              }
              if (value != null && value.isNotEmpty) {
                final intValue = int.tryParse(value);
                if (intValue == null) return 'Must be a number';
              }
              return null;
            },
          ),
        );

      case 'boolean':
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: CheckboxListTile(
            title: Text(field.label + (field.required ? ' *' : '')),
            subtitle: field.description != null
                ? Text(field.description!)
                : null,
            value: currentValue is bool ? currentValue : false,
            onChanged: (value) {
              config[field.name] = value ?? false;
              onChanged(config);
            },
          ),
        );

      case 'array':
        // For now, treat arrays as text fields with comma-separated values
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: TextFormField(
            initialValue: currentValue is List
                ? currentValue.join(', ')
                : currentValue.toString(),
            decoration: InputDecoration(
              labelText: field.label + (field.required ? ' *' : ''),
              hintText: field.description ?? 'Comma-separated values',
              border: const OutlineInputBorder(),
            ),
            onChanged: (value) {
              // Split by comma and trim whitespace
              final arrayValue = value
                  .split(',')
                  .map((s) => s.trim())
                  .where((s) => s.isNotEmpty)
                  .toList();
              config[field.name] = arrayValue;
              onChanged(config);
            },
            validator: field.required
                ? (value) =>
                      value == null || value.isEmpty ? 'Required field' : null
                : null,
          ),
        );

      default:
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: TextFormField(
            initialValue: currentValue.toString(),
            decoration: InputDecoration(
              labelText: field.label + (field.required ? ' *' : ''),
              hintText: field.description,
              border: const OutlineInputBorder(),
            ),
            onChanged: (value) {
              config[field.name] = value;
              onChanged(config);
            },
            validator: field.required
                ? (value) =>
                      value == null || value.isEmpty ? 'Required field' : null
                : null,
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingSchemas) {
      return const Center(child: CircularProgressIndicator());
    }

    final actionFields = _parseSchemaFields(_actionSchema);
    final reactionFields = _parseSchemaFields(_reactionSchema);

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildConfigSection(
            title: 'Action Configuration',
            fields: actionFields,
            config: _actionConfig,
            onChanged: (config) {
              setState(() {
                _actionConfig = config;
              });
              widget.onActionConfigChanged(config);
            },
          ),
          const SizedBox(height: 16),
          _buildConfigSection(
            title: 'Reaction Configuration',
            fields: reactionFields,
            config: _reactionConfig,
            onChanged: (config) {
              setState(() {
                _reactionConfig = config;
              });
              widget.onReactionConfigChanged(config);
            },
          ),
        ],
      ),
    );
  }

  bool validate() {
    return _formKey.currentState?.validate() ?? false;
  }
}
