import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from supplychain.models import CapacityUtilization, PredictionsUtilization

class Command(BaseCommand):
    help = "Import data for CapacityUtilization and PredictionsUtilization from CSV files"

    def add_arguments(self, parser):
        parser.add_argument('capacity_csv', type=str, help="Path to the CapacityUtilization CSV file")
        parser.add_argument('predictions_csv', type=str, help="Path to the PredictionsUtilization CSV file")

    def handle(self, *args, **kwargs):
        capacity_csv_path = kwargs['capacity_csv']
        predictions_csv_path = kwargs['predictions_csv']

        if not os.path.exists(capacity_csv_path) or not os.path.exists(predictions_csv_path):
            self.stderr.write("Error: One or both CSV files do not exist.")
            return

        try:
            self.import_capacity_utilization(capacity_csv_path)
            self.import_predictions_utilization(predictions_csv_path)
            self.stdout.write(self.style.SUCCESS("Successfully imported data for both models."))

        except Exception as e:
            self.stderr.write(f"Error during import: {e}")

    def import_capacity_utilization(self, csv_file_path):
        """Imports CapacityUtilization data from a CSV file."""
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row

            records_created = 0
            for row in reader:
                if len(row) < 4:
                    self.stderr.write(f"Skipping incomplete row: {row}")
                    continue

                location = row[0]
                date = datetime.strptime(row[1], "%Y-%m-%d").date()
                existing_capacity = int(row[2])
                current_utilization = int(row[3])

                CapacityUtilization.objects.update_or_create(
                    location=location,
                    date=date,
                    defaults={
                        "existing_capacity": existing_capacity,
                        "current_utilization": current_utilization,
                    },
                )
                records_created += 1

            self.stdout.write(self.style.SUCCESS(f"Imported {records_created} CapacityUtilization records."))

    def import_predictions_utilization(self, csv_file_path):
        """Imports PredictionsUtilization data from a CSV file."""
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row

            records_created = 0
            for row in reader:
                if len(row) < 9:
                    self.stderr.write(f"Skipping incomplete row: {row}")
                    continue

                location = row[1]
                date = datetime.strptime(row[2], "%Y-%m-%d").date()
                predicted_demand = int(float(row[3]))
                existing_capacity = int(row[4])
                increase_capacity = row[5]
                units_increase = int(row[6]) if row[6] else 0
                supplier_chosen = row[7] if row[7] else None
                order_cost = float(row[8]) if row[8] else 0.0

                PredictionsUtilization.objects.update_or_create(
                    location=location,
                    date=date,
                    defaults={
                        "predicted_demand": predicted_demand,
                        "existing_capacity": existing_capacity,
                        "increase_capacity": increase_capacity,
                        "units_increase": units_increase,
                        "supplier_chosen": supplier_chosen,
                        "order_cost": order_cost,
                    },
                )
                records_created += 1

            self.stdout.write(self.style.SUCCESS(f"Imported {records_created} PredictionsUtilization records."))
