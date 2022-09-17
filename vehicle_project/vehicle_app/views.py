from django.shortcuts import render
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin

from .models import *
from .serializers import *

# For processing GET HTTP requests of Mileage Records
class GetMileageRecordsView(APIView):
    def get(self, request, Unit_Number = None, year = None, month = None, day = None):
        if year and month and day:
            Record_Date = datetime.datetime(year, month, day).date()
        else:
            Record_Date = None

        if Unit_Number:
            if Record_Date:
                try:
                    query_set = MileageRecords.objects.filter(Unit_Number = Unit_Number).filter(Record_Date = Record_Date)
                except MileageRecords.DoesNotExist:
                    return Response({'Error': 'There are no matching mileage records.'}, status = 400)
            else:
                query_set = MileageRecords.objects.filter(Unit_Number = Unit_Number)
        else:
            try:
                query_set = MileageRecords.objects.all()
            except MileageRecords.DoesNotExist:
                return Response({'Error': 'There are no matching mileage records.'}, status = 400)
        read_serializer = MileageRecordsSerializer(query_set, many = True)
        return Response(read_serializer.data) 
        

# For processing POST or GET HTTP requests of Vehicle table info
class PostOrGetAssetView(GenericAPIView, CreateModelMixin):
    # Record_Date must be input as ISO 8601 format date string i.e. "2022-03-12"

    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def get(self, request, Unit_Number = None):
        if Unit_Number:
            try:
                query_set = Vehicle.objects.filter(Unit_Number = Unit_Number)
            except Vehicle.DoesNotExist:
                return Response({'Error': 'This vehicle does not exist in the database.'}, status = 400)
            read_serializer = VehicleSerializer(query_set, many = True)
        else:
            query_set = Vehicle.objects.all()
            read_serializer = VehicleSerializer(query_set, many = True)
        return Response(read_serializer.data)

    def post(self, request):
        create_vehicle_serializer = VehicleSerializer(data = request.data)
        if create_vehicle_serializer.is_valid():
            mileage_record_serializer = MileageRecordsSerializer(data = request.data)

            print(mileage_record_serializer.is_valid())

            if mileage_record_serializer.is_valid():
                try:
                    asset = create_vehicle_serializer.save()
                    read_vehicle_serializer = VehicleSerializer(asset)
                    mileage_record_serializer.save()    # Automatically adds to mileage records for use in calculating distance
                    return Response(read_vehicle_serializer.data, status = 201)
                except IntegrityError:
                   return Response({'Error' : 'Record_Date must be included and Unit_Number must be unique'}, status = 400) 
            return Response({'Error' : 'Record_Date must be included and Unit_Number must be unique'}, status = 400)
        return Response(create_vehicle_serializer.errors, status = 400)


# For Processing of PUT and DELETE HTTP requests of Vehicle table info
class UpdateMileageOrDeleteAssetView(GenericAPIView, UpdateModelMixin): 
    # Record_Date must be input as ISO 8601 format date string i.e. "2022-03-12"

    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    # Disallows OPTIONS method requests
    metadata_class = None

    def get(self, request, Unit_Number = None):
        if Unit_Number:
            try:
                query_set = Vehicle.objects.filter(Unit_Number = Unit_Number)
            except Vehicle.DoesNotExist:
                return Response({'Error': 'This vehicle does not exist in the database.'}, status = 400)
            read_serializer = VehicleSerializer(query_set, many = True) 
        else:
            query_set = Vehicle.objects.all()
            read_serializer = VehicleSerializer(query_set, many = True)
        return Response(read_serializer.data)

    def put(self, request, Unit_Number = None):
        # Check that update request matches given path
        if(Unit_Number != request.data['Unit_Number']):
            return Response({'Error' : 'Vehicle Unit Number in path does not match specified Unit Number for intended update.'})

        # Check that vehicle already exists in database
        try:
            asset = Vehicle.objects.get(Unit_Number = request.data['Unit_Number'])
        except Vehicle.DoesNotExist:
            return Response({'Error': 'This vehicle does not exist in the database. Please add first if you would like to update.'}, status = 400)

        latest_mileage_record_date = max(MileageRecords.objects.filter(Unit_Number = Unit_Number).values_list('Record_Date'))[0]

        # Assume mileage must never decrease with time
        if(request.data['Record_Date'] >= str(latest_mileage_record_date)):
            # If date is later than latest, mileage must be equal or greater than latest
            if(int(request.data['Mileage']) < Vehicle.objects.filter(Unit_Number = request.data['Unit_Number']).values('Mileage').first()['Mileage']):
                return Response({'Error' : 'Updated mileage for a later date must be greater than or equal to current value.'})
            else:
                update_serializer = VehicleSerializer(asset, data = request.data)
                if update_serializer.is_valid():
                    mileage_record_serializer = MileageRecordsSerializer(data = request.data)
                
                    if mileage_record_serializer.is_valid():
                        asset_object = update_serializer.save()
                        read_serializer = VehicleSerializer(asset_object)
                        mileage_record_serializer.save()
                        return Response(read_serializer.data, status = 200)
                    return Response({'Error':'Record_Date must be included to update vehicle mileage. Record_Date and Unit_Number combination must be unique. Check mileage records.'}, status = 400)
                return Response(update_serializer.errors, status = 400)
                
        else: 
            # If date is earlier than latest, mileage must be equal or less than latest
            if(int(request.data['Mileage']) > Vehicle.objects.filter(Unit_Number = request.data['Unit_Number']).values('Mileage').first()['Mileage']):
                return Response({'Error' : 'Updated mileage for a prior date must be less than or equal to current value.'})
            else:
                mileage_record_serializer = MileageRecordsSerializer(data = request.data)
                if mileage_record_serializer.is_valid():
                    mileage_record_serializer.save()
                    return Response({'Success':'Mileage records value added for prior date. Vehicle table current mileage unchanged. '}, status = 200)
                return Response({'Error':'Record_Date must be included to update vehicle mileage. Record_Date and Unit_Number combination must be unique. Check mileage records.'}, status = 400)
 
    def delete(Self, request, Unit_Number = None):
        try:
            asset = Vehicle.objects.get(Unit_Number = Unit_Number)
        except Vehicle.DoesNotExist:
            return Response({'Error': 'This vehicle does not exist in the database'}, status = 400)
        asset.delete()
        return Response(status = 204)

    
# To tell what distance an asset has traveled from a particular day to now (the latest mileage within the Vehicle table)
class GetDistanceTraveledView(APIView):
    def get(self, request, Unit_Number = None,  year = None, month = None, day = None):

        if Unit_Number and year and month and day:
            try:
                Record_Date = datetime.datetime(year, month, day).date()
                vehicle_object = Vehicle.objects.filter(Unit_Number = Unit_Number).all().first()
                current_mileage = vehicle_object.Mileage
                mileage_on_selected_date = MileageRecords.objects.filter(Unit_Number = vehicle_object).filter(Record_Date = Record_Date).all().first().Mileage
                distance_traveled = current_mileage - mileage_on_selected_date
                return Response({'Distance Traveled by Vehicle Since Chosen Day (miles):' : distance_traveled}, status = 200)
            except:
                return Response({'Error':'The distance could not be computed. Check that there is a record for the chosen day.'}, status = 400)
        else:
            return Response({'Error':'You must provide Unit_Number with year, month, and day.'}, status = 400)

