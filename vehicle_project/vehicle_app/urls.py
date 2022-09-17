from django.urls import path, register_converter
from datetime import datetime

from . import views

urlpatterns = [
    # Paths for adding, viewing, updating, and deleting Vehicle table entries
    path('assets/', views.PostOrGetAssetView.as_view(), name = 'All Vehicles'), 
    path('assets/<str:Unit_Number>/', views.UpdateMileageOrDeleteAssetView.as_view(), name = 'Specific Vehicle'),

    # Paths for viewing Mileage Records table entries
    path('mileage_records/', views.GetMileageRecordsView.as_view(), name = 'All Mileage Records'),
    path('mileage_records/<str:Unit_Number>/', views.GetMileageRecordsView.as_view(), name = 'Vehicle Mileage Records'),
    path('mileage_records/<str:Unit_Number>/<int:year>/<int:month>/<int:day>/', 
    views.GetMileageRecordsView.as_view(), name = 'Daily Vehicle Mileage Records'),

    # To compute distance a vehicle has travelled from chosen day to now
    path('distance_traveled/<str:Unit_Number>/<int:year>/<int:month>/<int:day>/', views.GetDistanceTraveledView.as_view(), 
    name = 'Distance Traveled')
]