import csv
import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from ingest.models import Tenant, SourceSystem, RawDataRecord, NormalizedEmission

class Command(BaseCommand):
    help = 'Loads mock data from data/ folder and runs ingestion parsers'

    def handle(self, *args, **kwargs):
        Tenant.objects.all().delete()
        SourceSystem.objects.all().delete()
        
        tenant = Tenant.objects.create(name='Acme Corp')
        sap_sys = SourceSystem.objects.create(tenant=tenant, name='SAP ECC6 Europe', system_type='SAP')
        util_sys = SourceSystem.objects.create(tenant=tenant, name='PG&E Data Portal', system_type='UTILITY')
        travel_sys = SourceSystem.objects.create(tenant=tenant, name='Navan Global', system_type='TRAVEL')

        self.load_sap(sap_sys, tenant)
        self.load_utility(util_sys, tenant)
        self.load_travel(travel_sys, tenant)
        self.stdout.write(self.style.SUCCESS('Successfully loaded and parsed mock data!'))

    def load_sap(self, sys, tenant):
        path = os.path.join(settings.BASE_DIR, 'data', 'sap_export.csv')
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = RawDataRecord.objects.create(source_system=sys, raw_payload=row)
                
                # Validation rules
                errors = []
                if row.get('Werk') not in ['W001', 'W002']:
                    errors.append(f"Unknown Plant Code: {row.get('Werk')}")
                
                qty = float(row.get('Menge', 0))
                if qty == 0:
                    raw.status = 'FAILED'
                    raw.save()
                    continue
                if qty > 100000:
                    errors.append(f"Suspiciously high quantity: {qty}")

                try:
                    dt = datetime.strptime(row.get('Belegdatum'), '%d.%m.%Y').date()
                except:
                    dt = datetime.now().date()
                    errors.append("Invalid date format, using today")

                NormalizedEmission.objects.create(
                    tenant=tenant,
                    raw_record=raw,
                    scope=3,
                    category='Purchased Goods',
                    emission_date=dt,
                    quantity=qty,
                    unit=row.get('MEins', 'Unknown'),
                    emission_factor=2.5, # Mock factor
                    co2e=qty * 2.5,
                    validation_errors=errors if errors else None
                )
                raw.status = 'PARSED'
                raw.save()

    def load_utility(self, sys, tenant):
        path = os.path.join(settings.BASE_DIR, 'data', 'utility_export.csv')
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = RawDataRecord.objects.create(source_system=sys, raw_payload=row)
                
                # Tradeoff: Map to start date of billing period
                try:
                    dt = datetime.strptime(row.get('Start_Date'), '%Y-%m-%d').date()
                except:
                    dt = datetime.now().date()

                qty = float(row.get('Usage', 0))

                NormalizedEmission.objects.create(
                    tenant=tenant,
                    raw_record=raw,
                    scope=2,
                    category='Purchased Electricity',
                    emission_date=dt,
                    quantity=qty,
                    unit=row.get('Unit', 'kWh'),
                    emission_factor=0.35,
                    co2e=qty * 0.35,
                )
                raw.status = 'PARSED'
                raw.save()

    def load_travel(self, sys, tenant):
        path = os.path.join(settings.BASE_DIR, 'data', 'travel_api.json')
        with open(path, 'r') as f:
            data = json.load(f)
            for item in data:
                raw = RawDataRecord.objects.create(source_system=sys, raw_payload=item)
                
                details = item.get('details', {})
                dist = details.get('distance_km')
                errors = []
                
                if dist is None:
                    # Mock lookup
                    if details.get('origin') == 'SFO' and details.get('destination') == 'LHR':
                        dist = 8600
                        errors.append("Distance missing. Applied mock fallback for SFO->LHR.")
                    else:
                        dist = 0
                        errors.append("Distance missing and no fallback available.")

                try:
                    dt = datetime.strptime(item.get('date'), '%Y-%m-%d').date()
                except:
                    dt = datetime.now().date()

                NormalizedEmission.objects.create(
                    tenant=tenant,
                    raw_record=raw,
                    scope=3,
                    category='Business Travel',
                    emission_date=dt,
                    quantity=dist,
                    unit='km',
                    emission_factor=0.15, # Mock per km factor
                    co2e=dist * 0.15,
                    validation_errors=errors if errors else None
                )
                raw.status = 'PARSED'
                raw.save()
