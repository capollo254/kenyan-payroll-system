# apps/compliance/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StatutoryRate
from .serializers import StatutoryRateSerializer

class StatutoryRateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing statutory deduction rates (NSSF, SHIF, AHL)
    Only superusers can modify rates
    """
    serializer_class = StatutoryRateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StatutoryRate.objects.filter(is_active=True)
    
    def update(self, request, *args, **kwargs):
        # Only superusers can update rates
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can update statutory rates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        # Only superusers can create rates
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can create statutory rates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # Only superusers can delete rates
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can delete statutory rates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def current_rates(self, request):
        """
        Get the current active rates for all statutory deductions
        """
        rates = {}
        for rate_type, _ in StatutoryRate.RATE_TYPES:
            try:
                rate = StatutoryRate.objects.filter(
                    rate_type=rate_type, 
                    is_active=True
                ).first()
                if rate:
                    rates[rate_type] = {
                        'id': rate.id,
                        'rate_value': float(rate.rate_value),
                        'rate_percentage': float(rate.rate_value * 100),
                        'effective_date': rate.effective_date,
                        'description': rate.description
                    }
            except StatutoryRate.DoesNotExist:
                rates[rate_type] = None
        
        return Response(rates)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Update multiple statutory rates at once
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can update statutory rates'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        rates_data = request.data
        updated_rates = []
        
        for rate_type, rate_value in rates_data.items():
            if rate_type in [choice[0] for choice in StatutoryRate.RATE_TYPES]:
                # Convert percentage to decimal if needed
                if isinstance(rate_value, (int, float)) and rate_value > 1:
                    rate_value = rate_value / 100
                
                rate, created = StatutoryRate.objects.update_or_create(
                    rate_type=rate_type,
                    defaults={
                        'rate_value': rate_value,
                        'effective_date': request.data.get('effective_date', 
                                                         StatutoryRate.objects.filter(rate_type=rate_type).first().effective_date if StatutoryRate.objects.filter(rate_type=rate_type).exists() else '2024-01-01'),
                        'is_active': True
                    }
                )
                updated_rates.append({
                    'rate_type': rate_type,
                    'rate_value': float(rate.rate_value),
                    'rate_percentage': float(rate.rate_value * 100),
                    'created': created
                })
        
        return Response({
            'message': f'Updated {len(updated_rates)} statutory rates',
            'updated_rates': updated_rates
        })