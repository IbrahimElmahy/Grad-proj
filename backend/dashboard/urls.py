from django.urls import path
from .views import DashboardStatsView, dashboard_view, upload_view, inspection_list_view, inspection_detail_view, reports_view

urlpatterns = [
    path('', dashboard_view, name='dashboard_index'),
    path('upload/', upload_view, name='upload_inspection'),
    path('inspections/', inspection_list_view, name='inspection_list'),
    path('inspections/<uuid:pk>/', inspection_detail_view, name='inspection_detail'),
    path('reports/', reports_view, name='reports_page'),
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
