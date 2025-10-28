# finance_project/urls.py
from django.contrib import admin
from django.urls import path, include  # <-- Make sure 'include' is added

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Add these two lines from Part 5 and Part 9
    path('remit/', include('remittances.urls')),
    path('reports/', include('reports.urls')),
]