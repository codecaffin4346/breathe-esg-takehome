import uuid
from django.db import models

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SourceSystem(models.Model):
    SYSTEM_TYPES = [
        ('SAP', 'SAP ERP'),
        ('UTILITY', 'Utility Portal'),
        ('TRAVEL', 'Travel Platform'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.system_type})"

class RawDataRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARSED', 'Parsed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE)
    raw_payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    ingested_at = models.DateTimeField(auto_now_add=True)

class NormalizedEmission(models.Model):
    STATUS_CHOICES = [
        ('PENDING_REVIEW', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    raw_record = models.OneToOneField(RawDataRecord, on_delete=models.CASCADE)
    
    scope = models.IntegerField()  # 1, 2, or 3
    category = models.CharField(max_length=255)
    emission_date = models.DateField()
    
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    emission_factor = models.FloatField(default=1.0) # Mocked factor
    co2e = models.FloatField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_REVIEW')
    validation_errors = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('EDITED', 'Edited'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(NormalizedEmission, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.CharField(max_length=255, default='Analyst')
    previous_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
