from rest_framework import serializers
from .models import PDFDocument

class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = '__all__'
