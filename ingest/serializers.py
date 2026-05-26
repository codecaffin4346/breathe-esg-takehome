from rest_framework import serializers
from .models import Tenant, SourceSystem, RawDataRecord, NormalizedEmission, AuditLog

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class SourceSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceSystem
        fields = '__all__'

class RawDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDataRecord
        fields = '__all__'

class NormalizedEmissionSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='raw_record.source_system.name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = NormalizedEmission
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
