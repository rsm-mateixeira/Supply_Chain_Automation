from django.db import models

class CapacityUtilization(models.Model):
    location = models.CharField(max_length=255)
    date = models.DateField()
    existing_capacity = models.PositiveIntegerField()
    current_utilization = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.location} - {self.date}: {self.current_utilization}/{self.existing_capacity})"


class PredictionsUtilization(models.Model):
    location = models.CharField(max_length=255)
    date = models.DateField()
    predicted_demand = models.PositiveIntegerField()
    existing_capacity = models.PositiveIntegerField()
    increase_capacity = models.CharField(max_length=255)
    units_increase = models.PositiveIntegerField(default=0)
    supplier_chosen = models.CharField(max_length=255, blank=True, null=True)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        increase_text = "Increase" if self.increase_capacity else "No Increase"
        return f"{self.location} - {self.date}: Demand {self.predicted_demand}, Capacity {self.existing_capacity} ({increase_text})"

    def capacity_gap(self):
        """Calculate the gap between predicted demand and existing capacity."""
        return self.predicted_demand - self.existing_capacity

    def is_capacity_sufficient(self):
        """Check if existing capacity meets or exceeds demand."""
        return self.existing_capacity >= self.predicted_demand


class Order(models.Model):
    location = models.CharField(max_length=255)
    date = models.DateField()
    units_increase = models.PositiveIntegerField(default=0)
    supplier_chosen = models.CharField(max_length=255, blank=True, null=True)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date} - {self.location}"