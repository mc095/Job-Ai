from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('analysis/', include('analysis.urls')),
    path('resume/', include('resume.urls')),
    path('ats/', include('ats.urls')),
    path('exam/', include('exam.urls')),
    path('training/', include('training.urls')),
    path('interview/', include('interview.urls')),
]
