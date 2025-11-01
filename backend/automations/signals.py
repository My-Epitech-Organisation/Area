##
## EPITECH PROJECT, 2025
## Area
## File description:
## Django signals for automatic webhook management
##

"""
Django signals for automatic webhook management.

This module handles automatic creation and deletion of webhooks
when Areas are created, updated, or deleted.

Currently supported services:
- Notion: Auto-creates webhooks for real-time event notifications
"""

import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .helpers.notion_helper import auto_create_notion_webhook, auto_delete_notion_webhook
from .models import Area

logger = logging.getLogger(__name__)


# Track previous state for detecting config changes
_area_previous_state = {}


@receiver(pre_save, sender=Area)
def track_area_changes(sender, instance, **kwargs):
    """
    Track Area state before save to detect configuration changes.
    
    This allows us to detect when action_config changes and recreate
    webhooks accordingly.
    """
    if instance.pk:
        try:
            old_instance = Area.objects.get(pk=instance.pk)
            _area_previous_state[instance.pk] = {
                'action_config': old_instance.action_config,
                'action': old_instance.action,
            }
        except Area.DoesNotExist:
            pass


@receiver(post_save, sender=Area)
def handle_area_saved(sender, instance, created, **kwargs):
    """
    Auto-create or update Notion webhook when Area is created or updated.
    
    Workflow:
    1. Check if Area uses Notion service
    2. If newly created: Create webhook
    3. If updated and config changed: Recreate webhook
    4. Log success/failure
    
    Note: Webhook creation failure won't prevent Area creation.
    Area will fall back to polling mode if webhook fails.
    """
    # Only handle Notion areas
    if instance.action.service.name.lower() != 'notion':
        return
    
    try:
        if created:
            # New Area created - create webhook
            logger.info(f"Creating Notion webhook for new Area {instance.id}")
            success = auto_create_notion_webhook(instance, instance.owner)
            
            if success:
                logger.info(f"✅ Auto-created Notion webhook for Area {instance.id} ({instance.name})")
            else:
                logger.warning(f"⚠️ Failed to auto-create Notion webhook for Area {instance.id}, falling back to polling")
        
        else:
            # Area updated - check if config changed
            previous = _area_previous_state.get(instance.pk, {})
            old_config = previous.get('action_config', {})
            new_config = instance.action_config or {}
            
            # Check if relevant config changed
            config_changed = (
                old_config.get('page_id') != new_config.get('page_id') or
                old_config.get('database_id') != new_config.get('database_id')
            )
            
            if config_changed:
                logger.info(f"Notion config changed for Area {instance.id}, recreating webhook")
                
                # Delete old webhook(s)
                auto_delete_notion_webhook(instance)
                
                # Create new webhook with updated config
                success = auto_create_notion_webhook(instance, instance.owner)
                
                if success:
                    logger.info(f"✅ Recreated Notion webhook for Area {instance.id}")
                else:
                    logger.warning(f"⚠️ Failed to recreate Notion webhook for Area {instance.id}")
            
            # Clean up tracking
            if instance.pk in _area_previous_state:
                del _area_previous_state[instance.pk]
    
    except Exception as e:
        logger.error(f"Error in handle_area_saved for Area {instance.id}: {e}", exc_info=True)


@receiver(post_delete, sender=Area)
def handle_area_deleted(sender, instance, **kwargs):
    """
    Auto-delete Notion webhook when Area is deleted.
    
    This ensures cleanup of webhooks on Notion's side to avoid
    orphan webhooks sending events to our server.
    """
    # Only handle Notion areas
    if instance.action.service.name.lower() != 'notion':
        return
    
    try:
        logger.info(f"Deleting Notion webhook(s) for deleted Area {instance.id}")
        success = auto_delete_notion_webhook(instance)
        
        if success:
            logger.info(f"✅ Deleted Notion webhook(s) for Area {instance.id}")
        else:
            logger.warning(f"⚠️ Failed to fully delete Notion webhook(s) for Area {instance.id}")
    
    except Exception as e:
        logger.error(f"Error in handle_area_deleted for Area {instance.id}: {e}", exc_info=True)
