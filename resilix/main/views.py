from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import openai


from .serializers import (
    AlertSerializer,
    DisasterFeedbackSerializer,
    LoacationSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AlertChoicesSerializer,
)

from .models import Alert, DisasterFeedback, Location, AlertChoices
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from rest_framework import generics
import pyotp
from twilio.rest import Client
from rest_framework.decorators import authentication_classes, api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions


# sending sms
def send_sms_code(user):
    time_otp = pyotp.TOTP(user.otp, interval=300)
    time_otp = time_otp.now()
    user_phone_number = user.phone_number

    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    client.messages.create(
        body="Your verification code is " + time_otp,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=user_phone_number,
    )


def verify_phone(user, sms_code):
    code = int(sms_code)
    if user.authenticate(code):
        user.phone.verified = True
        user.phone.save()
        return True
    return False


# registration logic
# Endpoint for registring users
class UserRegistration(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            user = serializer.save()

            # Send SMS code
            send_sms_code(user)
            sms_code = data.get("sms_code")
            # Verify the phone number
            if verify_phone(user, sms_code):
                response = {
                    "message": "User Created Successfully",
                    "data": serializer.data,
                }
                return Response(data=response, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])  # Include token authentication
class UserLogin(APIView):
    def post(self, request: Request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            if user:
                token, created = Token.objects.get_or_create(user=user)
                print(token)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED
        )

    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)


class ListDisasterFeedback(APIView):
    # getting disaster feedbacks
    def get(self, request):
        disaster_feedback = DisasterFeedback.objects.all()
        serializer = DisasterFeedbackSerializer(disaster_feedback, many=True)
        return Response(serializer.data)

    # creating disaster feedbacks
    def post(self, request):
        serializer = DisasterFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListLocations(APIView):
    # getting disaster feedbacks
    def get(self, request):
        locations = Location.objects.all()
        serializer = LoacationSerializer(locations, many=True)
        return Response(serializer.data)

    # creating disaster feedbacks
    def post(self, request):
        serializer = LoacationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Homepage Api endpoint
class EmergencyAlertChoicesView(APIView):
    # getting emergency alert choices
    def get(self, request):
        emergency_choices = AlertChoices.objects.all()
        serializer = AlertChoicesSerializer(emergency_choices, many=True)
        return Response(serializer.data)

    # creating emergency  choices
    def post(self, request):
        serializer = AlertChoicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Listing and creating alerts
class AlertListCreateView(generics.ListCreateAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    def perform_create(self, serializer):
        # Extract user's location from the request data
        user_location_data = self.request.data.get("user_location", None)

        # Validate and save the location if available
        if user_location_data:
            location_serializer = LoacationSerializer(data=user_location_data)
            if location_serializer.is_valid():
                location_instance = location_serializer.save()
                serializer.validated_data["location"] = location_instance

        # Save the alert instance
        alert_instance = serializer.save()

        # Use OpenAI to generate first aid response
        alert_description = alert_instance.description
        first_aid_response = serializer.get_first_aid_response(alert_description)

        # Update the alert instance with the first aid response
        alert_instance.first_aid_response = first_aid_response
        alert_instance.save()

        return alert_instance
