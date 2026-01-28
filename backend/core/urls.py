from django.contrib import admin
from django.urls import path
from api.views import UploadView
from django.conf import settings
from django.conf.urls.static import static
from api.views import UploadView, PDFReportView

# --- ADD THIS IMPORT ---
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', UploadView.as_view(), name='upload'),
    
    # This line works only if the import above is present
    path('api/login/', obtain_auth_token, name='api_token_auth'), 
    path('api/report/<int:file_id>/', PDFReportView.as_view(), name='pdf_report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)