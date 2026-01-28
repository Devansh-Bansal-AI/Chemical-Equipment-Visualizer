from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EquipmentFile
import pandas as pd
import os

class UploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        
        # 1. Save file to DB
        equipment_file = EquipmentFile.objects.create(file=file_obj)
        
        # 2. History Management (Keep only last 5)
        files = EquipmentFile.objects.all().order_by('-uploaded_at')
        if files.count() > 5:
            for f in files[5:]:
                f.file.delete() # Delete actual file
                f.delete()      # Delete DB record

        # 3. Read with Pandas
        try:
            df = pd.read_csv(equipment_file.file.path)
            
            # 4. Calculate Stats
            summary = {
                "total_count": len(df),
                "avg_temperature": round(df['Temperature'].mean(), 2),
                "avg_pressure": round(df['Pressure'].mean(), 2),
                "avg_flowrate": round(df['Flowrate'].mean(), 2),
                # Get counts for "Type" (e.g., Reactor: 5, Pump: 2)
                "type_distribution": df['Type'].value_counts().to_dict(),
                # Raw data for charts (Temperature vs Pressure)
                "chart_data": {
                    "labels": df['Equipment Name'].tolist(),
                    "temperature": df['Temperature'].tolist(),
                    "pressure": df['Pressure'].tolist()
                }
            }
            return Response(summary, status=200)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)