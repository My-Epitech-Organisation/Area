import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DynamicConfigForm } from '../DynamicConfigForm';

describe('DynamicConfigForm Component', () => {
  const mockOnChange = vi.fn();

  describe('Rendering', () => {
    it('should return null when schema is undefined', () => {
      const { container } = render(
        <DynamicConfigForm
          schema={undefined as any}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should return null when schema properties is empty', () => {
      const { container } = render(
        <DynamicConfigForm
          schema={{ type: 'object' as const, properties: {} }}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should render form with schema properties', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          testField: {
            type: 'string' as const,
            description: 'Test field',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByLabelText(/testfield/i)).toBeInTheDocument();
    });

    it('should render optional title', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          field1: { type: 'string' as const },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
          title="Test Configuration"
        />
      );

      expect(screen.getByText('Test Configuration')).toBeInTheDocument();
    });
  });

  describe('String Fields', () => {
    it('should render string input field', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          username: {
            type: 'string' as const,
            description: 'Enter username',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/username/i) as HTMLInputElement;
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
    });

    it('should handle string input change', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          email: {
            type: 'string' as const,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/email/i);
      fireEvent.change(input, { target: { value: 'test@example.com' } });

      expect(mockOnChange).toHaveBeenCalledWith({ email: 'test@example.com' });
    });

    it('should show required indicator for required string fields', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          name: {
            type: 'string' as const,
          },
        },
        required: ['name'],
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('*')).toBeInTheDocument();
    });
  });

  describe('Number Fields', () => {
    it('should render number input field', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          age: {
            type: 'number' as const,
            description: 'Enter age',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/age/i) as HTMLInputElement;
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'number');
    });

    it('should handle number input change', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          count: {
            type: 'number' as const,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/count/i);
      fireEvent.change(input, { target: { value: '42' } });

      expect(mockOnChange).toHaveBeenCalledWith({ count: 42 });
    });

    it('should render integer input field', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          quantity: {
            type: 'integer' as const,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/quantity/i);
      expect(input).toBeInTheDocument();
    });

    it('should handle minimum and maximum values', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          rating: {
            type: 'number' as const,
            minimum: 1,
            maximum: 5,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/rating/i) as HTMLInputElement;
      expect(input).toHaveAttribute('min', '1');
      expect(input).toHaveAttribute('max', '5');
    });
  });

  describe('Boolean Fields', () => {
    it('should render checkbox for boolean field', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          isActive: {
            type: 'boolean' as const,
            description: 'Activate feature',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const checkbox = screen.getByRole('checkbox', { name: /isactive/i });
      expect(checkbox).toBeInTheDocument();
    });

    it('should handle boolean checkbox change', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          enabled: {
            type: 'boolean' as const,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      expect(mockOnChange).toHaveBeenCalledWith({ enabled: true });
    });

    it('should use default boolean value', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          verified: {
            type: 'boolean' as const,
            default: true,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      expect(checkbox.checked).toBe(true);
    });
  });

  describe('Default Values', () => {
    it('should use default string value', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          username: {
            type: 'string' as const,
            default: 'defaultuser',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/username/i) as HTMLInputElement;
      expect(input.value).toBe('defaultuser');
    });

    it('should use default number value', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          port: {
            type: 'number' as const,
            default: 8080,
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/port/i) as HTMLInputElement;
      expect(input.value).toBe('8080');
    });

    it('should prefer provided values over defaults', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          name: {
            type: 'string' as const,
            default: 'default',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{ name: 'customvalue' }}
          onChange={mockOnChange}
        />
      );

      const input = screen.getByLabelText(/name/i) as HTMLInputElement;
      expect(input.value).toBe('customvalue');
    });
  });

  describe('Multiple Fields', () => {
    it('should render multiple fields of different types', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          name: { type: 'string' as const },
          age: { type: 'number' as const },
          active: { type: 'boolean' as const },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
    });

    it('should handle changes to different fields independently', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          field1: { type: 'string' as const },
          field2: { type: 'string' as const },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const input1 = screen.getByLabelText(/field1/i);
      const input2 = screen.getByLabelText(/field2/i);

      fireEvent.change(input1, { target: { value: 'value1' } });
      expect(mockOnChange).toHaveBeenCalledWith({ field1: 'value1' });

      fireEvent.change(input2, { target: { value: 'value2' } });
      expect(mockOnChange).toHaveBeenCalledWith({ field2: 'value2' });
    });
  });

  describe('Field Descriptions', () => {
    it('should display field description', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          apiKey: {
            type: 'string' as const,
            description: 'Enter your API key',
          },
        },
      };

      render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('Enter your API key')).toBeInTheDocument();
    });

    it('should handle fields without description', () => {
      const schema = {
        type: 'object' as const,
        properties: {
          field: {
            type: 'string' as const,
          },
        },
      };

      const { container } = render(
        <DynamicConfigForm
          schema={schema}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(container).toBeInTheDocument();
    });
  });
});
