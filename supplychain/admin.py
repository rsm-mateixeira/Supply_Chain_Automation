from django.contrib import admin
from .models import CapacityUtilization, PredictionsUtilization, Order

@admin.register(CapacityUtilization)
class CapacityUtilizationAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "existing_capacity", "current_utilization")
    list_filter = ("location", "date")
    search_fields = ("location",)

@admin.register(PredictionsUtilization)
class PredictionsUtilizationAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "predicted_demand", "existing_capacity", "increase_capacity", "supplier_chosen", "order_cost")
    list_filter = ("location", "increase_capacity", "supplier_chosen")
    search_fields = ("location",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "units_increase", "supplier_chosen", "order_cost")

