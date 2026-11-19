from django.urls import path
from . import views

app_name = "predictor"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("api/chat/", views.chat_view, name="chat"),
    path("api/history/", views.history_api_view, name="history_api"),
]
