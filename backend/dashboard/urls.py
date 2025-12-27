from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),
    path('upload/', views.upload, name='upload_inspection'),
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/<uuid:pk>/', views.inspection_detail, name='inspection_detail'),
]
