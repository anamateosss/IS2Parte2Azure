from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('destinations/', views.destinations, name='destinations'),
    path('destination/<int:pk>', views.DestinationDetailView.as_view(), name='destination_detail'),
    path('cruise/<int:pk>', views.CruiseDetailView.as_view(), name='cruise_detail'),
    path('info_request', views.InfoRequestCreate.as_view(), name='info_request'),
    path('destination/<int:pk>/review/new/', views.DestinationReviewCreate.as_view(), name='destination_review_create'),
    path('cruise/<int:pk>/review/new/', views.CruiseReviewCreate.as_view(), name='cruise_review_create'),
    path('destination/<int:pk>/purchase/', views.purchase_destination, name='purchase_destination'),
    path('cruise/<int:pk>/purchase/', views.purchase_cruise, name='purchase_cruise'),
    ]