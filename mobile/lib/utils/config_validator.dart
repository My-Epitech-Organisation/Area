/// Validator for action and reaction configurations against their schemas
class ConfigValidator {
  /// Validates configuration against a JSON schema
  static ValidationResult validate({
    required Map<String, dynamic>? schema,
    required Map<String, dynamic> config,
    required String configName,
  }) {
    if (schema == null || schema.isEmpty) {
      return ValidationResult(isValid: true, missingFields: []);
    }

    final requiredFields = (schema['required'] as List?)?.cast<String>() ?? [];
    final properties = (schema['properties'] as Map<String, dynamic>?) ?? {};

    final missingFields = <String>[];
    final validationErrors = <String>[];

    for (final fieldName in requiredFields) {
      final fieldValue = config[fieldName];
      final fieldSchema = properties[fieldName] as Map<String, dynamic>?;

      // Check if field is missing or empty
      if (fieldValue == null ||
          (fieldValue is String && fieldValue.isEmpty) ||
          (fieldValue is List && (fieldValue as List).isEmpty)) {
        missingFields.add(fieldName);

        // Provide specific error messages
        if (fieldSchema != null) {
          final description =
              fieldSchema['description'] as String? ?? 'This field is required';
          validationErrors.add('$fieldName: $description');
        } else {
          validationErrors.add('$fieldName: This field is required');
        }
      }
    }

    return ValidationResult(
      isValid: missingFields.isEmpty,
      missingFields: missingFields,
      errors: validationErrors,
    );
  }
}

class ValidationResult {
  final bool isValid;
  final List<String> missingFields;
  final List<String> errors;

  ValidationResult({
    required this.isValid,
    required this.missingFields,
    this.errors = const [],
  });

  String get errorMessage {
    if (isValid) return '';
    if (errors.isNotEmpty) return errors.join('\n');
    return 'Missing fields: ${missingFields.join(", ")}';
  }
}
