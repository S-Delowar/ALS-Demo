from rest_framework import serializers
from apps.persona.models import UserPersona


class UserPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPersona
        fields = [
            "profession",
            "level",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_preferences(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferences must be a JSON object.")
        return value
