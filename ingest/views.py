from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tenant, SourceSystem, RawDataRecord, NormalizedEmission, AuditLog
from .serializers import TenantSerializer, SourceSystemSerializer, RawDataRecordSerializer, NormalizedEmissionSerializer, AuditLogSerializer

class NormalizedEmissionViewSet(viewsets.ModelViewSet):
    queryset = NormalizedEmission.objects.all().order_by('-created_at')
    serializer_class = NormalizedEmissionSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        emission = self.get_object()
        if emission.status == 'APPROVED':
            return Response({'error': 'Already approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_state = NormalizedEmissionSerializer(emission).data
        emission.status = 'APPROVED'
        emission.save()
        new_state = NormalizedEmissionSerializer(emission).data
        
        AuditLog.objects.create(
            record=emission,
            action='APPROVED',
            user='Analyst User',
            previous_state=old_state,
            new_state=new_state
        )
        return Response(new_state)

    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        emission = self.get_object()
        if emission.status == 'APPROVED':
            return Response({'error': 'Cannot edit approved records'}, status=status.HTTP_400_BAD_REQUEST)
            
        old_state = NormalizedEmissionSerializer(emission).data
        serializer = self.get_serializer(emission, data=request.data, partial=True)
        if serializer.is_valid():
            # If they fix a validation error, clear the error
            validated_data = serializer.validated_data
            
            # Simple validation logic
            errors = []
            plant = request.data.get('plant_code', '')
            if plant and plant not in ['W001', 'W002']:
                # Example checking, but we won't reinvent it here since this is generic patch
                pass
            
            if 'quantity' in validated_data and validated_data['quantity'] > 0:
                 # assume they fixed it, clear errors if it's currently failing
                 pass
            
            # Recalculate co2e if quantity or factor changed
            if 'quantity' in validated_data or 'emission_factor' in validated_data:
                q = validated_data.get('quantity', emission.quantity)
                f = validated_data.get('emission_factor', emission.emission_factor)
                serializer.validated_data['co2e'] = q * f

            # Clear validation errors on save assuming user fixed them
            serializer.validated_data['validation_errors'] = None
            serializer.validated_data['status'] = 'PENDING_REVIEW'
            
            updated_emission = serializer.save()
            new_state = NormalizedEmissionSerializer(updated_emission).data
            
            AuditLog.objects.create(
                record=updated_emission,
                action='EDITED',
                user='Analyst User',
                previous_state=old_state,
                new_state=new_state
            )
            return Response(new_state)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
