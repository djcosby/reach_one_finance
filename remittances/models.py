from django.db import models

# Create your models here.
# remittances/models.py

from django.db import models
from decimal import Decimal
import uuid

class Program(models.Model):
    name = models.CharField(max_length=120, unique=True)
    def __str__(self): return self.name

class ClientRoster(models.Model):
    client_name = models.CharField(max_length=160)
    norm_name = models.CharField(max_length=160, db_index=True)
    program = models.ForeignKey(Program, on_delete=models.PROTECT)
    def __str__(self): return f"{self.client_name} → {self.program.name}"

class RemittanceFile(models.Model):
    sha256 = models.CharField(max_length=64, unique=True)
    original_name = models.CharField(max_length=255)
    stored_path = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ("STAGED","STAGED"),("PARSED","PARSED"),
        ("FAILED","FAILED"),("DUPLICATE","DUPLICATE")
    ])
    created_at = models.DateTimeField(auto_now_add=True)

class FinancePeriod(models.Model):
    start = models.DateField()
    end = models.DateField()
    label = models.CharField(max_length=40, unique=True) # e.g. 2025-10-01_10-15
    state = models.CharField(max_length=24, default="DRAFT")

class ClaimLine(models.Model):
    period = models.ForeignKey(FinancePeriod, on_delete=models.PROTECT)
    payer = models.CharField(max_length=160)
    check_date = models.DateField()
    check_amount = models.DecimalField(max_digits=12, decimal_places=2)
    client_name = models.CharField(max_length=160)
    hcpcs_cpt = models.CharField(max_length=16)
    units = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    billed_amount= models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    service_date = models.DateField()
    program = models.ForeignKey(Program, null=True, on_delete=models.SET_NULL)
    meta = models.JSONField(default=dict)

class PeriodSnapshot(models.Model):
    period = models.OneToOneField(FinancePeriod, on_delete=models.CASCADE)
    math = models.JSONField() # frozen results
    created_at = models.DateTimeField(auto_now_add=True)

class StagedClaims(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sha256 = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField() # list of normalized claim dicts
    created_at = models.DateTimeField(auto_now_add=True)