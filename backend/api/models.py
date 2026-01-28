from django.db import models
from django.contrib.auth.models import User

class EquipmentFile(models.Model):
    # Link upload to a user (Corporate Requirement: Auth)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='csvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Store summary stats as JSON to avoid re-processing CSVs later
    summary_data = models.JSONField(null=True, blank=True) 

    def __str__(self):
        return f"File {self.id} - {self.uploaded_at}"