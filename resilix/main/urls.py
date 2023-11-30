from django.urls import path
from .views import (
    ListDisasterFeedback,
    ListLocations,
    send_sms_code,
    verify_phone,
    EmergencyAlertChoicesView,
    UserRegistration,
    UserLogin,
    AlertListCreateView,
)

urlpatterns = [
    path(
        "user/signup/",
        UserRegistration.as_view(),
        name="user-registration",
    ),
    path("login/", UserLogin.as_view(), name="login"),
    path(
        "resilix/disaster/feedbacks", ListDisasterFeedback.as_view(), name="feedbacks"
    ),
    path("resilix/locations/", ListLocations.as_view(), name="alerts"),
    path(
        "",
        EmergencyAlertChoicesView.as_view(),
        name="create-emergency",
    ),
    path("Alerts/", AlertListCreateView.as_view()),
    path("send_sms_code/", send_sms_code),
    path("verify_phone/<int:sms_code>", verify_phone),
]
