from django.urls import path
from . import views

app_name = "supplychain"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("chatbot/query/", views.chatbot_query, name="chatbot_query"),
    path("alerts/", views.alerts_view, name="alerts"),
    path("generate_report/<int:prediction_id>/", views.generate_report, name="generate_report"),
    path("accept-order/<int:alert_id>/", views.accept_order, name="accept_order"),
    path('generate-report/<int:prediction_id>/', views.generate_report, name='generate_report'),
    path("past-orders/", views.past_orders_view, name="orders"),
]
