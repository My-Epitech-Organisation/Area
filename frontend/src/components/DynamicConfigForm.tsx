import React from 'react';
import type { JSONSchema, JSONSchemaProperty } from '../types/api';

interface DynamicConfigFormProps {
  schema: JSONSchema;
  values: Record<string, unknown>;
  onChange: (values: Record<string, unknown>) => void;
  title?: string;
}

/**
 * DynamicConfigForm is a dynamic form component that generates input fields based on a provided JSON Schema.
 * It renders appropriate input elements for each property in the schema and manages their values.
 *
 * @param {DynamicConfigFormProps} props - The props for the component, including schema, values, onChange, and optional title.
 */

export const DynamicConfigForm: React.FC<DynamicConfigFormProps> = ({
  schema,
  values,
  onChange,
  title,
}) => {
  if (!schema || !schema.properties || Object.keys(schema.properties).length === 0) {
    return null;
  }

  const handleFieldChange = (fieldName: string, value: unknown) => {
    onChange({
      ...values,
      [fieldName]: value,
    });
  };

  const renderField = (fieldName: string, property: JSONSchemaProperty) => {
    const isRequired = schema.required?.includes(fieldName) || false;

    // Render based on type
    switch (property.type) {
      case 'integer':
      case 'number': {
        const numberValue =
          typeof values[fieldName] === 'number'
            ? (values[fieldName] as number)
            : typeof property.default === 'number'
              ? property.default
              : '';

        return (
          <div key={fieldName} className="mb-4">
            <label htmlFor={fieldName} className="form-label">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-required ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-theme-muted mb-1">{property.description}</p>
            )}
            <input
              id={fieldName}
              type="number"
              value={numberValue}
              onChange={(e) => {
                const val =
                  property.type === 'integer'
                    ? parseInt(e.target.value, 10)
                    : parseFloat(e.target.value);
                handleFieldChange(fieldName, isNaN(val) ? '' : val);
              }}
              min={property.minimum}
              max={property.maximum}
              required={isRequired}
              className="form-input"
              placeholder={property.description}
            />
          </div>
        );
      }

      case 'boolean': {
        const boolValue =
          typeof values[fieldName] === 'boolean'
            ? (values[fieldName] as boolean)
            : typeof property.default === 'boolean'
              ? property.default
              : false;

        return (
          <div key={fieldName} className="mb-4 flex items-center">
            <input
              type="checkbox"
              id={fieldName}
              checked={boolValue}
              onChange={(e) => handleFieldChange(fieldName, e.target.checked)}
              className="h-4 w-4 text-theme-accent focus:ring-theme-accent border-theme-secondary rounded bg-theme-tertiary"
            />
            <label htmlFor={fieldName} className="ml-2 block text-sm text-theme-secondary">
              {formatFieldName(fieldName)}
              {property.description && (
                <span className="text-xs text-theme-muted ml-2">({property.description})</span>
              )}
            </label>
          </div>
        );
      }

      case 'string': {
        if (property.enum && property.enum.length > 0) {
          const stringValue =
            typeof values[fieldName] === 'string'
              ? (values[fieldName] as string)
              : typeof property.default === 'string'
                ? property.default
                : '';

          return (
            <div key={fieldName} className="mb-4">
              <label htmlFor={fieldName} className="form-label">
                {formatFieldName(fieldName)}
                {isRequired && <span className="text-required ml-1">*</span>}
              </label>
              {property.description && (
                <p className="text-xs text-theme-muted mb-1">{property.description}</p>
              )}
              <select
                id={fieldName}
                value={stringValue}
                onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                required={isRequired}
                className="form-select"
              >
                <option value="">Select {formatFieldName(fieldName)}</option>
                {property.enum.map((enumOption) => {
                  const optionValue =
                    typeof enumOption === 'string' || typeof enumOption === 'number'
                      ? enumOption
                      : String(enumOption);

                  return (
                    <option
                      key={String(optionValue)}
                      value={String(optionValue)}
                      className="text-theme-primary bg-theme-primary"
                    >
                      {String(optionValue)}
                    </option>
                  );
                })}
              </select>
            </div>
          );
        }

        const stringValue =
          typeof values[fieldName] === 'string'
            ? (values[fieldName] as string)
            : typeof property.default === 'string'
              ? property.default
              : '';

        return (
          <div key={fieldName} className="mb-4">
            <label htmlFor={fieldName} className="form-label">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-required ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-theme-muted mb-1">{property.description}</p>
            )}
            <input
              id={fieldName}
              type={
                property.format === 'email' ? 'email' : property.format === 'uri' ? 'url' : 'text'
              }
              value={stringValue}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              required={isRequired}
              minLength={property.minLength}
              maxLength={property.maxLength}
              pattern={property.pattern}
              className="form-input"
              placeholder={property.description}
            />
          </div>
        );
      }

      case 'text': {
        // Handle text type (for multiline text like email body)
        const textValue =
          typeof values[fieldName] === 'string'
            ? (values[fieldName] as string)
            : typeof property.default === 'string'
              ? property.default
              : '';

        return (
          <div key={fieldName} className="mb-4">
            <label htmlFor={fieldName} className="form-label">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-required ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-theme-muted mb-1">{property.description}</p>
            )}
            <textarea
              id={fieldName}
              value={textValue}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              required={isRequired}
              rows={4}
              className="form-input"
              placeholder={property.placeholder || property.description}
            />
          </div>
        );
      }

      case 'array': {
        const arrayValue = Array.isArray(values[fieldName])
          ? (values[fieldName] as unknown[])
          : Array.isArray(property.default)
            ? property.default
            : [];

        return (
          <div key={fieldName} className="mb-4">
            <label htmlFor={fieldName} className="form-label">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-required ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-theme-muted mb-1">{property.description}</p>
            )}
            <input
              id={fieldName}
              type="text"
              value={arrayValue.join(', ')}
              onChange={(e) => {
                const arr = e.target.value
                  .split(',')
                  .map((s) => s.trim())
                  .filter(Boolean);
                handleFieldChange(fieldName, arr);
              }}
              required={isRequired}
              className="form-input"
              placeholder="Enter comma-separated values"
            />
          </div>
        );
      }

      case 'object': {
        const objectValue =
          typeof values[fieldName] === 'object' &&
          values[fieldName] !== null &&
          !Array.isArray(values[fieldName])
            ? (values[fieldName] as Record<string, unknown>)
            : typeof property.default === 'object' &&
                property.default !== null &&
                !Array.isArray(property.default)
              ? property.default
              : {};

        return (
          <div key={fieldName} className="mb-4">
            <label htmlFor={fieldName} className="form-label">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-required ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-theme-muted mb-1">{property.description}</p>
            )}
            <textarea
              id={fieldName}
              value={JSON.stringify(objectValue, null, 2)}
              onChange={(e) => {
                try {
                  const obj = JSON.parse(e.target.value);
                  handleFieldChange(fieldName, obj);
                } catch {
                  console.error('Invalid JSON, please correct it.');
                }
              }}
              required={isRequired}
              rows={4}
              className="form-input font-mono text-sm"
              placeholder='{"key": "value"}'
            />
          </div>
        );
      }

      default: {
        return null;
      }
    }
  };

  const formatFieldName = (name: string): string => {
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  /**
   * Sort fields in a smart order:
   * 1. Required fields first (in the order they appear in schema.required)
   * 2. Optional fields after
   * This ensures consistent, predictable form layout
   */
  const getSortedFields = (): Array<[string, JSONSchemaProperty]> => {
    const entries = Object.entries(schema.properties);
    const required = schema.required || [];

    // Separate required and optional fields
    const requiredFields = required
      .filter((fieldName) => schema.properties[fieldName])
      .map(
        (fieldName) => [fieldName, schema.properties[fieldName]] as [string, JSONSchemaProperty]
      );

    const optionalFields = entries.filter(([fieldName]) => !required.includes(fieldName));

    return [...requiredFields, ...optionalFields];
  };

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-gray-600">
      {title && <h3 className="text-sm font-semibold text-white mb-3">{title}</h3>}
      <div className="space-y-2">
        {getSortedFields().map(([fieldName, property]) => renderField(fieldName, property))}
      </div>
    </div>
  );
};
