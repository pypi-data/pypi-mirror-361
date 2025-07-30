from django.contrib.auth import get_user_model
from rest_framework import serializers

user_model = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model
        fields = (
            "id",
            user_model.USERNAME_FIELD,
            user_model.EMAIL_FIELD,
            "first_name",
            "last_name",
        )
