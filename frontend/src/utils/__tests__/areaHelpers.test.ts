/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** areaHelpers tests
 */

import { describe, it, expect } from 'vitest';
import {
  findActionByName,
  findReactionByName,
  formatActionName,
  generateAreaName,
} from '../areaHelpers';
import type { Action, Reaction } from '../../types/api';

describe('areaHelpers', () => {
  describe('findActionByName', () => {
    it('should find an action by its name', () => {
      const actions: Action[] = [
        {
          id: 1,
          service: 1,
          name: 'timer_daily',
          description: 'Trigger daily',
          config_schema: { type: 'object', properties: {} },
        },
        {
          id: 2,
          service: 1,
          name: 'email_received',
          description: 'When email is received',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      const result = findActionByName(actions, 'timer_daily');
      expect(result).toBeDefined();
      expect(result?.name).toBe('timer_daily');
    });

    it('should return undefined if action is not found', () => {
      const actions: Action[] = [
        {
          id: 1,
          service: 1,
          name: 'timer_daily',
          description: 'Trigger daily',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      const result = findActionByName(actions, 'non_existent');
      expect(result).toBeUndefined();
    });

    it('should handle empty actions array', () => {
      const result = findActionByName([], 'timer_daily');
      expect(result).toBeUndefined();
    });
  });

  describe('findReactionByName', () => {
    it('should find a reaction by its name', () => {
      const reactions: Reaction[] = [
        {
          id: 1,
          service: 1,
          name: 'send_email',
          description: 'Send an email',
          config_schema: { type: 'object', properties: {} },
        },
        {
          id: 2,
          service: 1,
          name: 'send_sms',
          description: 'Send SMS',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      const result = findReactionByName(reactions, 'send_email');
      expect(result).toBeDefined();
      expect(result?.name).toBe('send_email');
    });

    it('should return undefined if reaction is not found', () => {
      const reactions: Reaction[] = [
        {
          id: 1,
          service: 1,
          name: 'send_email',
          description: 'Send an email',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      const result = findReactionByName(reactions, 'non_existent');
      expect(result).toBeUndefined();
    });

    it('should handle empty reactions array', () => {
      const result = findReactionByName([], 'send_email');
      expect(result).toBeUndefined();
    });
  });

  describe('formatActionName', () => {
    it('should format action name with underscores', () => {
      expect(formatActionName('timer_daily')).toBe('Timer Daily');
    });

    it('should format action name with multiple underscores', () => {
      expect(formatActionName('send_email_notification')).toBe('Send Email Notification');
    });

    it('should handle single word', () => {
      expect(formatActionName('timer')).toBe('Timer');
    });

    it('should handle empty string', () => {
      expect(formatActionName('')).toBe('');
    });

    it('should capitalize first letter of each word', () => {
      expect(formatActionName('test_action_name')).toBe('Test Action Name');
    });
  });

  describe('generateAreaName', () => {
    it('should generate area name from action and reaction', () => {
      const result = generateAreaName('timer_daily', 'send_email');
      expect(result).toBe('Timer Daily → Send Email');
    });

    it('should format both action and reaction names', () => {
      const result = generateAreaName('github_push', 'slack_notification');
      expect(result).toBe('Github Push → Slack Notification');
    });

    it('should handle single-word names', () => {
      const result = generateAreaName('timer', 'email');
      expect(result).toBe('Timer → Email');
    });

    it('should include arrow separator', () => {
      const result = generateAreaName('action', 'reaction');
      expect(result).toContain('→');
    });
  });
});
