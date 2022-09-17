from rest_framework import serializers

from .models import *


class MileageRecordsSerializer(serializers.ModelSerializer):
    Record_ID = serializers.IntegerField(required = False)
    Unit_Number = serializers.CharField(max_length = 8, required = True)
    Record_Date = serializers.DateField(required = True)
    Mileage = serializers.IntegerField(required = True)

    def create(self, validated_data):
        
        return MileageRecords.objects.create(
            Record_ID = validated_data.get('Record_ID'),
            Unit_Number = Vehicle.objects.get(Unit_Number = validated_data.get('Unit_Number')),
            Record_Date = validated_data.get('Record_Date'),
            Mileage = validated_data.get('Mileage')
        )

    class Meta:
        model = MileageRecords
        fields = (
            'Record_ID',
            'Unit_Number',
            'Record_Date',
            'Mileage'
        )
        read_only_fields = (
            'Record_ID',
            'Unit_Number',
            'Record_Date',
            'Mileage'
        )


class VehicleSerializer(serializers.ModelSerializer):

    Unit_Number = serializers.CharField(max_length = 8, required = True)
    Mileage = serializers.IntegerField(required = True)
    Manufacturer = serializers.CharField(max_length = 50, required = True)
    Status = serializers.CharField(max_length = 50, required = True)
    Record_Date = serializers.DateField(required = False)

    def create(self, validated_data):

        return Vehicle.objects.create(
            Unit_Number = validated_data.get('Unit_Number'),
            Mileage = validated_data.get('Mileage'),
            Manufacturer = validated_data.get('Manufacturer'),
            Status = validated_data.get('Status')
        )

    def update(self, instance, validated_data):
        # Only an asset's Mileage and Status need to be modifiable as per requriements
        instance.Mileage = validated_data.get('Mileage', instance.Mileage)
        instance.Status = validated_data.get('Status', instance.Status)
        instance.save()
        return instance

    class Meta:
        model = Vehicle
        fields = (
            'Unit_Number',
            'Mileage',
            'Manufacturer',
            'Status',
            'Record_Date'
        )
        read_only_fields = (
            'Unit_Number',
            'Manufacturer',
        )