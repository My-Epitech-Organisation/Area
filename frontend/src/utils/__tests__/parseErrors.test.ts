/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** parseErrors tests
 */

import { describe, it, expect } from 'vitest';
import { parseErrors } from '../parseErrors';

describe('parseErrors', () => {
  it('should return default message for null input', () => {
    const result = parseErrors(null);
    expect(result).toEqual({ message: 'An error occurred' });
  });

  it('should return default message for undefined input', () => {
    const result = parseErrors(undefined);
    expect(result).toEqual({ message: 'An error occurred' });
  });

  it('should handle string input', () => {
    const result = parseErrors('Something went wrong');
    expect(result).toEqual({ message: 'Something went wrong' });
  });

  it('should extract detail from error object', () => {
    const result = parseErrors({ detail: 'Authentication failed' });
    expect(result).toEqual({ message: 'Authentication failed' });
  });

  it('should handle detail with non-string value', () => {
    const result = parseErrors({ detail: 404 });
    expect(result).toEqual({ message: '404' });
  });

  it('should parse object with array values', () => {
    const result = parseErrors({
      email: ['This field is required.', 'Enter a valid email address.'],
      password: ['This field is required.'],
    });

    expect(result.message).toBe(
      'email: This field is required. Enter a valid email address. — password: This field is required.'
    );
    expect(result.fields).toEqual({
      email: ['This field is required.', 'Enter a valid email address.'],
      password: ['This field is required.'],
    });
  });

  it('should parse object with string values', () => {
    const result = parseErrors({
      username: 'This username is already taken.',
      email: 'Invalid email format.',
    });

    expect(result.message).toContain('username: This username is already taken.');
    expect(result.message).toContain('email: Invalid email format.');
    expect(result.fields).toEqual({
      username: ['This username is already taken.'],
      email: ['Invalid email format.'],
    });
  });

  it('should handle mixed array and string values', () => {
    const result = parseErrors({
      field1: ['Error 1', 'Error 2'],
      field2: 'Single error',
    });

    expect(result.message).toContain('field1: Error 1 Error 2');
    expect(result.message).toContain('field2: Single error');
    expect(result.fields).toEqual({
      field1: ['Error 1', 'Error 2'],
      field2: ['Single error'],
    });
  });

  it('should handle empty object', () => {
    const result = parseErrors({});
    expect(result.message).toBe('');
    expect(result.fields).toEqual({});
  });

  it('should handle nested objects gracefully', () => {
    const result = parseErrors({
      nested: { inner: 'value' },
    });

    expect(result.message).toBeDefined();
  });

  it('should convert numbers in arrays to strings', () => {
    const result = parseErrors({
      code: [404, 500],
    });

    expect(result.fields?.code).toEqual(['404', '500']);
    expect(result.message).toContain('code: 404 500');
  });

  it('should handle boolean error value', () => {
    const result = parseErrors({
      isValid: 'false',
    });

    expect(result.message).toContain('isValid');
    expect(result.message).toContain('false');
  });

  it('should preserve field separator in message', () => {
    const result = parseErrors({
      field1: 'error1',
      field2: 'error2',
      field3: 'error3',
    });

    const separatorCount = (result.message.match(/—/g) || []).length;
    expect(separatorCount).toBe(2); // Two separators for three fields
  });
});
