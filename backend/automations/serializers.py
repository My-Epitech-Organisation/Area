"""
Serializers for the AREA automation system.

This module provides Django REST Framework serializers for:
- Service discovery (read-only)
- Action/Reaction discovery (read-only)
- Area CRUD operations with validation
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Service, Action, Reaction, Area
from .validators import (
    validate_action_config,
    validate_reaction_config,
    validate_action_reaction_compatibility
)


class ServiceSerializer(serializers.ModelSerializer):
    """Read-only serializer for Service discovery."""

    actions_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'status', 'actions_count', 'reactions_count']
        read_only_fields = ['id', 'name', 'description', 'status', 'actions_count', 'reactions_count']

    def get_actions_count(self, obj):
        """Return the number of available actions for this service."""
        return obj.actions.count()

    def get_reactions_count(self, obj):
        """Return the number of available reactions for this service."""
        return obj.reactions.count()


class ActionSerializer(serializers.ModelSerializer):
    """Read-only serializer for Action discovery."""

    service_name = serializers.CharField(source='service.name', read_only=True)
    service_id = serializers.IntegerField(source='service.id', read_only=True)

    class Meta:
        model = Action
        fields = ['id', 'name', 'description', 'service_id', 'service_name']
        read_only_fields = ['id', 'name', 'description', 'service_id', 'service_name']


class ReactionSerializer(serializers.ModelSerializer):
    """Read-only serializer for Reaction discovery."""

    service_name = serializers.CharField(source='service.name', read_only=True)
    service_id = serializers.IntegerField(source='service.id', read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'name', 'description', 'service_id', 'service_name']
        read_only_fields = ['id', 'name', 'description', 'service_id', 'service_name']


class AreaSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for Area with validation."""

    action_detail = ActionSerializer(source='action', read_only=True)
    reaction_detail = ReactionSerializer(source='reaction', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    # Convenience fields for easier access to action/reaction info
    action_name = serializers.CharField(source='action.name', read_only=True)
    reaction_name = serializers.CharField(source='reaction.name', read_only=True)
    action_service = serializers.CharField(source='action.service.name', read_only=True)
    reaction_service = serializers.CharField(source='reaction.service.name', read_only=True)

    class Meta:
        model = Area
        fields = [
            'id', 'name', 'status', 'created_at',
            'action', 'action_detail', 'action_config', 'action_name', 'action_service',
            'reaction', 'reaction_detail', 'reaction_config', 'reaction_name', 'reaction_service',
            'owner', 'owner_username'
        ]
        read_only_fields = ['id', 'created_at', 'owner', 'owner_username', 'action_detail', 'reaction_detail',
                           'action_name', 'action_service', 'reaction_name', 'reaction_service']

    def validate_action_config(self, value):
        """Validate that action_config matches the action's schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Action configuration must be a valid JSON object.")

        # La validation spécifique par schéma sera faite dans validate()
        # quand on aura accès à l'objet action
        return value

    def validate_reaction_config(self, value):
        """Validate that reaction_config matches the reaction's schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Reaction configuration must be a valid JSON object.")

        # La validation spécifique par schéma sera faite dans validate()
        # quand on aura accès à l'objet reaction
        return value

    def validate(self, attrs):
        """Cross-field validation for action/reaction compatibility."""
        action = attrs.get('action')
        reaction = attrs.get('reaction')

        if action and reaction:
            # Validation basique: s'assurer que l'action et la reaction existent et sont actives
            if action.service.status != Service.Status.ACTIVE:
                raise serializers.ValidationError({
                    'action': f"Service '{action.service.name}' is not active."
                })

            if reaction.service.status != Service.Status.ACTIVE:
                raise serializers.ValidationError({
                    'reaction': f"Service '{reaction.service.name}' is not active."
                })

            # TODO: Ajouter des règles de compatibilité spécifiques
            # Par exemple : certaines actions ne peuvent être liées qu'à certaines reactions
            # Cette logique sera ajoutée selon les besoins métier

            # Validation de la compatibilité action/reaction
            try:
                validate_action_reaction_compatibility(action.name, reaction.name)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'non_field_errors': str(e)
                })

            # Validation des configurations si elles sont fournies
            action_config = attrs.get('action_config', {})
            reaction_config = attrs.get('reaction_config', {})

            # Valider les configurations avec les schémas des actions/reactions
            try:
                validate_action_config(action.name, action_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'action_config': str(e)
                })

            try:
                validate_reaction_config(reaction.name, reaction_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'reaction_config': str(e)
                })

        return attrs


class AreaCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for Area creation with enhanced validation."""

    class Meta:
        model = Area
        fields = ['id', 'name', 'action', 'reaction', 'action_config', 'reaction_config', 'status']
        extra_kwargs = {
            'id': {'read_only': True},
            'action_config': {'default': dict},
            'reaction_config': {'default': dict},
            'status': {'default': Area.Status.ACTIVE},
        }

    def validate(self, attrs):
        """Enhanced validation for Area creation."""
        # Réutiliser la validation du serializer parent
        attrs = super().validate(attrs)

        # Validation supplémentaire pour la création
        action = attrs.get('action')
        reaction = attrs.get('reaction')
        action_config = attrs.get('action_config', {})
        reaction_config = attrs.get('reaction_config', {})

        if action:
            # Validate action configuration against schema
            try:
                validate_action_config(action.name, action_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'action_config': str(e)
                })

        if reaction:
            # Validate reaction configuration against schema
            try:
                validate_reaction_config(reaction.name, reaction_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'reaction_config': str(e)
                })

        if action and reaction:
            # Validation de la compatibilité métier
            try:
                validate_action_reaction_compatibility(action.name, reaction.name)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'non_field_errors': str(e)
                })

        return attrs



    def create(self, validated_data):
        """Create Area with proper owner assignment."""
        # L'owner sera assigné dans la vue via perform_create
        return super().create(validated_data)


# Serializers utilitaires pour /about.json
class AboutActionSerializer(serializers.ModelSerializer):
    """Simplified Action serializer for /about.json endpoint."""

    class Meta:
        model = Action
        fields = ['name', 'description']


class AboutReactionSerializer(serializers.ModelSerializer):
    """Simplified Reaction serializer for /about.json endpoint."""

    class Meta:
        model = Reaction
        fields = ['name', 'description']


class AboutServiceSerializer(serializers.ModelSerializer):
    """Service serializer for /about.json endpoint with nested actions/reactions."""

    actions = AboutActionSerializer(many=True, read_only=True)
    reactions = AboutReactionSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['name', 'actions', 'reactions']