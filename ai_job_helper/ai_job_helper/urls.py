from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('analysis/', include('analysis.urls')),
    path('resume/', include('resume.urls')),
    path('ats/', include('ats.urls')),
    path('exam/', include('exam.urls')),
    path('training/', include('training.urls')),
    path('interview/', include('interview.urls')),
    path('portfolio/', include('portfolio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
