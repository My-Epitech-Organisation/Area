/**
 * Utility functions for AREA management
 */

import type { Action, Reaction } from '../types/api';

/**
 * Find an action by its name
 */
export function findActionByName(actions: Action[], name: string): Action | undefined {
  return actions.find((action) => action.name === name);
}

/**
 * Find a reaction by its name
 */
export function findReactionByName(reactions: Reaction[], name: string): Reaction | undefined {
  return reactions.find((reaction) => reaction.name === name);
}

/**
 * Format action/reaction name for display
 * Example: "timer_daily" -> "Timer Daily"
 */
export function formatActionName(name: string): string {
  return name
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Generate a default area name from action and reaction
 */
export function generateAreaName(actionName: string, reactionName: string): string {
  return `${formatActionName(actionName)} → ${formatActionName(reactionName)}`;
}
