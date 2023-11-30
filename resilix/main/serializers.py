from rest_framework import serializers

from .models import Alert, DisasterFeedback, Location, CustomUser, AlertChoices
from rest_framework.validators import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import openai


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["alert_type", "description", "location"]

    def get_first_aid_response(self, alert_description):
        openai.api_key = "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"

        prompt = f"Given the following emergency alert: {alert_description},  You are well-versed in first aid measures for emergencies in Cameroon. Provide immediate and clear first aid measures.Offer concise and effective first aid guidance."

        response = openai.Completion.create(
            engine="text-davinci-002",  # Choose the appropriate OpenAI engine
            prompt=prompt,
            max_tokens=150,  # Adjust as needed
        )

        return response.choices[0].text.strip()


class DisasterFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterFeedback
        fields = ["description", "date_time_of_feedback", "alert"]


class LoacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["longitude", "latitude"]

    def create(self, validated_data):
        return Location.objects.create(**validated_data)


class AlertChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertChoices
        fields = ["emergency_name"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=15)
    username = serializers.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = ["username", "phone_number", "password"]

    def validate(self, attrs):
        username_exist = CustomUser.objects.filter(username=attrs["username"]).exists()

        if username_exist:
            raise ValidationError("Username Already Taken")
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is not active.")
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError(
                "Must include 'username' and 'password' fields."
            )

        return data


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
