"""
Serializers for the AREA automation system.

This module provides Django REST Framework serializers for:
- Service discovery (read-only)
- Action/Reaction discovery (read-only)
- Area CRUD operations with validation
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from users.oauth.manager import OAuthManager

from .models import Action, Area, Execution, Reaction, Service
from .validators import (
    ACTION_SCHEMAS,
    REACTION_SCHEMAS,
    validate_action_config,
    validate_action_reaction_compatibility,
    validate_reaction_config,
)
import requests
from urllib.parse import urlparse, unquote


_WIKI_IMAGE_CACHE = {}


def _resolve_wikipedia_file_url(url_or_text: str) -> str | None:
    """Given a Wikipedia file page URL or text containing 'File:...', query the
    appropriate Wikimedia API to obtain the direct image URL (upload.wikimedia.org).

    Returns the direct image URL or None on failure.
    """
    try:
        parsed = urlparse(url_or_text)
        netloc = parsed.netloc or "en.wikipedia.org"
        fragment = parsed.fragment or ""
        path = parsed.path or ""

        import re

        m = re.search(r"File:([^/#?]+)", fragment) or re.search(r"/wiki/File:([^/#?]+)", path) or re.search(r"File:([^/#?]+)", url_or_text)
        if not m:
            return None

        filename = unquote(m.group(1))
        key = (netloc, filename)
        if key in _WIKI_IMAGE_CACHE:
            return _WIKI_IMAGE_CACHE[key]

        api_url = (
            f"https://{netloc}/w/api.php?action=query&titles=File:{requests.utils.requote_uri(filename)}"
            "&prop=imageinfo&iiprop=url&format=json&formatversion=2"
        )

        resp = requests.get(api_url, timeout=5)
        if not resp.ok:
            _WIKI_IMAGE_CACHE[key] = None
            return None

        data = resp.json()
        pages = data.get("query", {}).get("pages", [])
        if pages:
            imageinfo = pages[0].get("imageinfo")
            if imageinfo and len(imageinfo) > 0:
                img_url = imageinfo[0].get("url")
                _WIKI_IMAGE_CACHE[key] = img_url
                return img_url

        _WIKI_IMAGE_CACHE[key] = None
        return None
    except Exception:
        return None



class ServiceSerializer(serializers.ModelSerializer):
    """Read-only serializer for Service discovery."""

    actions_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "status",
            "actions_count",
            "reactions_count",
        ]
        read_only_fields = [
            "id",
            "name",
            "description",
            "status",
            "actions_count",
            "reactions_count",
        ]

    @extend_schema_field(int)
    def get_actions_count(self, obj):
        """Return the number of available actions for this service."""
        return obj.actions.count()

    @extend_schema_field(int)
    def get_reactions_count(self, obj):
        """Return the number of available reactions for this service."""
        return obj.reactions.count()


class ActionSerializer(serializers.ModelSerializer):
    """Read-only serializer for Action discovery."""

    service_name = serializers.CharField(source="service.name", read_only=True)
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    config_schema = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = [
            "id",
            "name",
            "description",
            "service_id",
            "service_name",
            "config_schema",
        ]
        read_only_fields = [
            "id",
            "name",
            "description",
            "service_id",
            "service_name",
            "config_schema",
        ]

    def get_config_schema(self, obj):
        """Return the JSON schema for this action's configuration."""
        if obj.config_schema:
            return obj.config_schema
        return ACTION_SCHEMAS.get(obj.name, {})


class ReactionSerializer(serializers.ModelSerializer):
    """Read-only serializer for Reaction discovery."""

    service_name = serializers.CharField(source="service.name", read_only=True)
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    config_schema = serializers.SerializerMethodField()

    class Meta:
        model = Reaction
        fields = [
            "id",
            "name",
            "description",
            "service_id",
            "service_name",
            "config_schema",
        ]
        read_only_fields = [
            "id",
            "name",
            "description",
            "service_id",
            "service_name",
            "config_schema",
        ]

    def get_config_schema(self, obj):
        """Return the JSON schema for this reaction's configuration."""
        if obj.config_schema:
            return obj.config_schema
        return REACTION_SCHEMAS.get(obj.name, {})


class AreaSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for Area with validation."""

    action_detail = ActionSerializer(source="action", read_only=True)
    reaction_detail = ReactionSerializer(source="reaction", read_only=True)
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    # Convenience fields for easier access to action/reaction info
    action_name = serializers.CharField(source="action.name", read_only=True)
    reaction_name = serializers.CharField(source="reaction.name", read_only=True)
    action_service = serializers.CharField(source="action.service.name", read_only=True)
    reaction_service = serializers.CharField(
        source="reaction.service.name", read_only=True
    )

    class Meta:
        model = Area
        fields = [
            "id",
            "name",
            "status",
            "created_at",
            "action",
            "action_detail",
            "action_config",
            "action_name",
            "action_service",
            "reaction",
            "reaction_detail",
            "reaction_config",
            "reaction_name",
            "reaction_service",
            "owner",
            "owner_username",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "owner",
            "owner_username",
            "action_detail",
            "reaction_detail",
            "action_name",
            "action_service",
            "reaction_name",
            "reaction_service",
        ]

    def validate_action_config(self, value):
        """Validate that action_config matches the action's schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Action configuration must be a valid JSON object."
            )

        # La validation spécifique par schéma sera faite dans validate()
        # quand on aura accès à l'objet action
        return value

    def validate_reaction_config(self, value):
        """Validate that reaction_config matches the reaction's schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Reaction configuration must be a valid JSON object."
            )

        # La validation spécifique par schéma sera faite dans validate()
        # quand on aura accès à l'objet reaction
        return value

    def validate(self, attrs):
        """Cross-field validation for action/reaction compatibility."""
        action = attrs.get("action")
        reaction = attrs.get("reaction")

        if action and reaction:
            # Validation basique: s'assurer que l'action et la reaction existent et sont actives
            if action.service.status != Service.Status.ACTIVE:
                raise serializers.ValidationError(
                    {"action": f"Service '{action.service.name}' is not active."}
                )

            if reaction.service.status != Service.Status.ACTIVE:
                raise serializers.ValidationError(
                    {"reaction": f"Service '{reaction.service.name}' is not active."}
                )

            # TODO: Ajouter des règles de compatibilité spécifiques
            # Par exemple : certaines actions ne peuvent être liées qu'à certaines reactions
            # Cette logique sera ajoutée selon les besoins métier

            # Validation de la compatibilité action/reaction
            try:
                validate_action_reaction_compatibility(action.name, reaction.name)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"non_field_errors": str(e)})

            # Validation des configurations si elles sont fournies
            action_config = attrs.get("action_config", {})
            reaction_config = attrs.get("reaction_config", {})

            # ⚠️ Special validation: Prevent infinite loops for GitHub
            # If action is github_new_issue and reaction is github_create_issue,
            # they must target different repositories
            if (
                action.name == "github_new_issue"
                and reaction.name == "github_create_issue"
            ):
                action_repo = action_config.get("repository", "").lower()
                reaction_repo = reaction_config.get("repository", "").lower()

                if action_repo and reaction_repo and action_repo == reaction_repo:
                    raise serializers.ValidationError(
                        {
                            "non_field_errors": (
                                "⚠️ Infinite loop detected! Cannot create GitHub issues in the same "
                                "repository that triggers the action. Please use a different target "
                                "repository to avoid infinite loops."
                            )
                        }
                    )

            # Valider les configurations avec les schémas des actions/reactions
            try:
                validate_action_config(action.name, action_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"action_config": str(e)})

            try:
                validate_reaction_config(reaction.name, reaction_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"reaction_config": str(e)})

        return attrs


class AreaCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for Area creation with enhanced validation."""

    class Meta:
        model = Area
        fields = [
            "id",
            "name",
            "action",
            "reaction",
            "action_config",
            "reaction_config",
            "status",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "action_config": {"default": dict},
            "reaction_config": {"default": dict},
            "status": {"default": Area.Status.ACTIVE},
        }

    def validate(self, attrs):
        """Enhanced validation for Area creation."""
        # Réutiliser la validation du serializer parent
        attrs = super().validate(attrs)

        # Validation supplémentaire pour la création
        action = attrs.get("action")
        reaction = attrs.get("reaction")
        action_config = attrs.get("action_config", {})
        reaction_config = attrs.get("reaction_config", {})

        # OAuth2 Validation: Check if user has connected required services
        if action:
            service_name = action.service.name.lower()

            # Check if this service requires OAuth2 connection
            from django.conf import settings

            if service_name in settings.OAUTH2_PROVIDERS:
                # Verify user has a valid token for this service

                user = (
                    self.context.get("request").user
                    if self.context.get("request")
                    else None
                )
                if user:
                    token = OAuthManager.get_valid_token(user, service_name)

                    if not token:
                        raise serializers.ValidationError(
                            {
                                "action": f"You must connect your {action.service.name} account before creating "
                                f"an area with this action. Please visit /auth/oauth/{service_name}/ to connect."
                            }
                        )

            # Validate action configuration against schema
            try:
                validate_action_config(action.name, action_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"action_config": str(e)})

        if reaction:
            service_name = reaction.service.name.lower()

            # Check if this service requires OAuth2 connection
            from django.conf import settings

            if service_name in settings.OAUTH2_PROVIDERS:
                # Verify user has a valid token for this service

                user = (
                    self.context.get("request").user
                    if self.context.get("request")
                    else None
                )
                if user:
                    token = OAuthManager.get_valid_token(user, service_name)

                    if not token:
                        raise serializers.ValidationError(
                            {
                                "reaction": f"You must connect your {reaction.service.name} account before creating "
                                f"an area with this reaction. Please visit /auth/oauth/{service_name}/ to connect."
                            }
                        )

            # Validate reaction configuration against schema
            try:
                validate_reaction_config(reaction.name, reaction_config)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"reaction_config": str(e)})

        if action and reaction:
            # Validation de la compatibilité métier
            try:
                validate_action_reaction_compatibility(action.name, reaction.name)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"non_field_errors": str(e)})

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
        fields = ["name", "description", "config_schema"]


class AboutReactionSerializer(serializers.ModelSerializer):
    """Simplified Reaction serializer for /about.json endpoint."""

    class Meta:
        model = Reaction
        fields = ["name", "description", "config_schema"]


class AboutServiceSerializer(serializers.ModelSerializer):
    """Service serializer for /about.json endpoint with nested actions/reactions."""

    actions = AboutActionSerializer(many=True, read_only=True)
    reactions = AboutReactionSerializer(many=True, read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["name", "actions", "reactions", "logo"]

    def get_logo(self, obj):
        """Return the configured logo URL for the service or a fallback.

        - Use an internal mapping of known services to their official/Wikipedia SVG URLs.
        - If a service is not present in the mapping, return None.
        """
        try:
            name = (obj.name or "").strip().lower()
        except Exception:
            return None
        # Inline mapping: service name (lowercase) -> direct image or wiki file page URL
        mapping = {
            # Direct upload.wikimedia.org URLs for reliable browser rendering
            "timer": "https://upload.wikimedia.org/wikipedia/commons/d/dd/OOjs_UI_icon_clock.svg",
            "debug": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Gear_icon_svg.svg",
            "email": "https://upload.wikimedia.org/wikipedia/commons/7/7f/OOjs_UI_icon_message.svg",
            "webhook": "https://upload.wikimedia.org/wikipedia/commons/7/72/OOjs_UI_icon_link-ltr.svg",
            "weather": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Circle-icons-weather.svg",
            # External services
            "teams": "https://upload.wikimedia.org/wikipedia/commons/5/50/Microsoft_Teams.png",
            "github": "https://upload.wikimedia.org/wikipedia/commons/c/c2/GitHub_Invertocat_Logo.svg",
            "gmail": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg",
            "slack": "https://upload.wikimedia.org/wikipedia/commons/7/76/Slack_Icon.png",
            "twitch": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Twitch_Glitch_Logo_Purple.svg",
            "google_calendar": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Google_Calendar_icon_%282020%29.svg",
        }

        import re

        def _normalize_key(s: str) -> str:
            return re.sub(r"[^a-z0-9]", "", (s or "").lower())

        candidates = [name, name.replace("_", ""), name.replace(" ", ""), _normalize_key(name)]

        found = None
        for k in candidates:
            if k in mapping:
                found = mapping[k]
                break

        if not found:
            return None

        if ("wikipedia.org" in found) or ("/media/" in found) or ("File:" in found):
            direct = _resolve_wikipedia_file_url(found)
            if direct:
                return direct

        return found





# Serializers pour Execution (journaling)


class ExecutionAreaSerializer(serializers.ModelSerializer):
    """Nested Area representation for Execution serializer."""

    action_name = serializers.CharField(source="action.name", read_only=True)
    reaction_name = serializers.CharField(source="reaction.name", read_only=True)
    action_service = serializers.CharField(source="action.service.name", read_only=True)
    reaction_service = serializers.CharField(
        source="reaction.service.name", read_only=True
    )

    class Meta:
        model = Area
        fields = [
            "id",
            "name",
            "action_name",
            "reaction_name",
            "action_service",
            "reaction_service",
        ]
        read_only_fields = fields


class ExecutionSerializer(serializers.ModelSerializer):
    """
    Full serializer for Execution with nested Area details.

    Used for retrieve/detail views where complete information is needed.
    """

    area_detail = ExecutionAreaSerializer(source="area", read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    is_terminal = serializers.BooleanField(read_only=True)

    class Meta:
        model = Execution
        fields = [
            "id",
            "area",
            "area_detail",
            "external_event_id",
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "trigger_data",
            "result_data",
            "error_message",
            "retry_count",
            "duration_seconds",
            "is_terminal",
        ]
        read_only_fields = fields

    @extend_schema_field(float)
    def get_duration_seconds(self, obj):
        """Return execution duration in seconds."""
        return obj.duration


class ExecutionListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for Execution list views.

    Excludes heavy JSON fields and nested data for better performance
    in list endpoints.
    """

    area_name = serializers.CharField(source="area.name", read_only=True)
    action_name = serializers.CharField(source="area.action.name", read_only=True)
    reaction_name = serializers.CharField(source="area.reaction.name", read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Execution
        fields = [
            "id",
            "area",
            "area_name",
            "action_name",
            "reaction_name",
            "external_event_id",
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "duration_seconds",
            "retry_count",
        ]
        read_only_fields = fields

    @extend_schema_field(float)
    def get_duration_seconds(self, obj):
        """Return execution duration in seconds."""
        return obj.duration


class ExecutionStatsSerializer(serializers.Serializer):
    """Serializer for execution statistics."""

    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    running = serializers.IntegerField()
    success = serializers.IntegerField()
    failed = serializers.IntegerField()
    skipped = serializers.IntegerField()
    by_area = serializers.DictField(child=serializers.IntegerField())
    recent_failures = ExecutionListSerializer(many=True, read_only=True)
