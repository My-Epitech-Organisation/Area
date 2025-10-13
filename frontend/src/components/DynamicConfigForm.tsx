import React from 'react';
import type { JSONSchema, JSONSchemaProperty } from '../types/api';

interface DynamicConfigFormProps {
  schema: JSONSchema;
  values: Record<string, any>;
  onChange: (values: Record<string, any>) => void;
  title?: string;
}

/**
 * Dynamic form component that generates input fields based on JSON Schema
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

  const handleFieldChange = (fieldName: string, value: any) => {
    onChange({
      ...values,
      [fieldName]: value,
    });
  };

  const renderField = (fieldName: string, property: JSONSchemaProperty) => {
    const isRequired = schema.required?.includes(fieldName) || false;
    const currentValue = values[fieldName] ?? property.default ?? '';

    // Render based on type
    switch (property.type) {
      case 'integer':
      case 'number':
        return (
          <div key={fieldName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-gray-500 mb-1">{property.description}</p>
            )}
            <input
              type="number"
              value={currentValue}
              onChange={(e) => {
                const val = property.type === 'integer'
                  ? parseInt(e.target.value, 10)
                  : parseFloat(e.target.value);
                handleFieldChange(fieldName, isNaN(val) ? '' : val);
              }}
              min={property.minimum}
              max={property.maximum}
              required={isRequired}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={property.description}
            />
          </div>
        );

      case 'boolean':
        return (
          <div key={fieldName} className="mb-4 flex items-center">
            <input
              type="checkbox"
              id={fieldName}
              checked={currentValue || false}
              onChange={(e) => handleFieldChange(fieldName, e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor={fieldName} className="ml-2 block text-sm text-gray-700">
              {formatFieldName(fieldName)}
              {property.description && (
                <span className="text-xs text-gray-500 ml-2">({property.description})</span>
              )}
            </label>
          </div>
        );

      case 'string':
        // Handle enum as select
        if (property.enum && property.enum.length > 0) {
          return (
            <div key={fieldName} className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {formatFieldName(fieldName)}
                {isRequired && <span className="text-red-500 ml-1">*</span>}
              </label>
              {property.description && (
                <p className="text-xs text-gray-500 mb-1">{property.description}</p>
              )}
              <select
                value={currentValue}
                onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                required={isRequired}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select {formatFieldName(fieldName)}</option>
                {property.enum.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          );
        }

        // Handle regular string input
        return (
          <div key={fieldName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-gray-500 mb-1">{property.description}</p>
            )}
            <input
              type={property.format === 'email' ? 'email' : property.format === 'uri' ? 'url' : 'text'}
              value={currentValue}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              required={isRequired}
              minLength={property.minLength}
              maxLength={property.maxLength}
              pattern={property.pattern}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={property.description}
            />
          </div>
        );

      case 'array':
        return (
          <div key={fieldName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-gray-500 mb-1">{property.description}</p>
            )}
            <input
              type="text"
              value={Array.isArray(currentValue) ? currentValue.join(', ') : ''}
              onChange={(e) => {
                const arr = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                handleFieldChange(fieldName, arr);
              }}
              required={isRequired}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter comma-separated values"
            />
          </div>
        );

      case 'object':
        return (
          <div key={fieldName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {formatFieldName(fieldName)}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            {property.description && (
              <p className="text-xs text-gray-500 mb-1">{property.description}</p>
            )}
            <textarea
              value={typeof currentValue === 'object' ? JSON.stringify(currentValue, null, 2) : '{}'}
              onChange={(e) => {
                try {
                  const obj = JSON.parse(e.target.value);
                  handleFieldChange(fieldName, obj);
                } catch {
                  // Invalid JSON, don't update
                }
              }}
              required={isRequired}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder='{"key": "value"}'
            />
          </div>
        );

      default:
        return null;
    }
  };

  const formatFieldName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
      {title && (
        <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      )}
      <div className="space-y-2">
        {Object.entries(schema.properties).map(([fieldName, property]) =>
          renderField(fieldName, property)
        )}
      </div>
    </div>
  );
};
