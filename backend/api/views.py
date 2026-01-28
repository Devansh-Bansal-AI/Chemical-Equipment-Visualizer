from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import EquipmentFile
from .services import DataService

class UploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  # <--- Corporate Security: Must be logged in

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file_obj = request.FILES['file']
        
        try:
            # 1. Save initial record linked to user
            instance = EquipmentFile.objects.create(file=file_obj, user=request.user)
            
            # 2. Process Data via Service Layer (Clean Architecture)
            summary = DataService.process_csv(instance.file.path)
            
            # 3. Save Summary to DB
            instance.summary_data = summary
            instance.save()

            # 4. History Management (Keep last 5 per user)
            user_files = EquipmentFile.objects.filter(user=request.user).order_by('-uploaded_at')
            if user_files.count() > 5:
                for f in user_files[5:]:
                    f.file.delete()
                    f.delete()
            
            # Add the file_id to the response so the frontend can request the PDF later
            summary['file_id'] = instance.id
            return Response(summary, status=200)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)

class PDFReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            # Ensure user can only download their own reports
            instance = EquipmentFile.objects.get(id=file_id, user=request.user)
            
            if not instance.summary_data:
                return Response({"error": "No analysis data found"}, status=404)
            
            pdf_buffer = DataService.generate_pdf(instance.summary_data)
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{file_id}.pdf"'
            return response
        except EquipmentFile.DoesNotExist:
            return Response({"error": "File not found or unauthorized"}, status=404)