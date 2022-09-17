from django.db import models

# Model for Vehicle table
class Vehicle(models.Model):
    Unit_Number = models.CharField(
        primary_key = True,
        max_length = 8,
        null = False,
        blank = False,
    )

    Mileage = models.PositiveIntegerField(
        null = False,
        blank = False,
        default = 0
    )

    Manufacturer = models.CharField(
        max_length = 50,
        null = False,
        blank = False,
        default = "Unknown"
    )

    # Char used instead of BooleanField to account for unknown potential states
    Status = models.CharField(
        max_length = 50,
        null = False,
        blank = False,
        default = "Unknown"
    )

    class Meta:
        db_table = 'VEHICLE'

# Model for Mileage Records table
class MileageRecords(models.Model):
    Record_ID = models.AutoField(primary_key = True)

    Unit_Number = models.ForeignKey(Vehicle, to_field = 'Unit_Number', on_delete = models.CASCADE)

    # Would be automatic date in production, entered manually for demonstration
    Record_Date = models.DateField(
        auto_now_add = False,
        null = False,
        blank = False
    )

    # Mileage on date of record
    Mileage = models.PositiveIntegerField(
        null = False,
        blank = False,
        default = 0
    )

    class Meta:
        db_table = 'MILEAGE_RECORDS'
        unique_together = ('Unit_Number', 'Record_Date')
