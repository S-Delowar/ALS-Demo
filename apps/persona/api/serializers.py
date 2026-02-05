# from rest_framework import serializers
# from apps.persona.models import UserPersona


# class UserPersonaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserPersona
#         fields = [
#             "profession",
#             "level",
#             "preferences",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = ["created_at", "updated_at"]

#     def validate_preferences(self, value):
#         if not isinstance(value, dict):
#             raise serializers.ValidationError("Preferences must be a JSON object.")
#         return value



# from rest_framework import serializers
# from apps.persona.models import UserPersona
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class UserPersonaSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source="user.email", read_only=True)
#     # Map 'profession' to the User model's profession field
#     profession = serializers.CharField(source="user.profession")

#     class Meta:
#         model = UserPersona
#         fields = [
#             "email",
#             "profession",
#             "level",
#             "preferences",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = ["created_at", "updated_at"]

#     def update(self, instance, validated_data):
#         # Extract user data (profession) from the nested source
#         user_data = validated_data.pop('user', {})
#         new_profession = user_data.get('profession')

#         # Update the User model if profession is provided
#         if new_profession:
#             instance.user.profession = new_profession
#             instance.user.save()

#         # Update the Persona model (level, preferences, etc.)
#         return super().update(instance, validated_data)

#     def validate_preferences(self, value):
#         if not isinstance(value, dict):
#             raise serializers.ValidationError("Preferences must be a JSON object.")
#         return value




from rest_framework import serializers
from apps.persona.models import UserPersona


class UserPersonaSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserPersona
        fields = [
            "full_name",
            "email",
            "profession", # This refers to UserPersona.profession
            "level",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def update(self, instance, validated_data):
        # 1. Get the new profession from the request
        new_profession = validated_data.get('profession')

        if new_profession:
            # 2. Update the User Model
            user = instance.user
            user.profession = new_profession
            user.save()

        # 3. Update the Persona Model (includes the profession field here too)
        return super().update(instance, validated_data)