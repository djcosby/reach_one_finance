from celery import shared_task
from pathlib import Path
from .models import RemittanceFile, StagedClaims
from .normalize import ClaimLineNorm, to_json
from .pipeline import route_programs

@shared_task(bind=True, max_retries=2)
def parse_remit(self, path:str, sha:str):
    try:
        # STUB PARSER: returns a couple of fake claims so you can test the flow
        claims = [
          ClaimLineNorm(
            payer="Ohio Medicaid",
            check_date="2025-10-12",
            check_amount="15450.75",
            client_name="John Bradley",
            hcpcs_cpt="H0015",
            units="1",
            billed_amount="168.99",
            paid_amount="116.18",
            service_date="2025-10-05",
            notes={}
          ).asdict(),
        ]
        stash = StagedClaims.objects.create(sha256=sha, payload=to_json(claims))
        RemittanceFile.objects.filter(sha256=sha).update(status="PARSED")
        route_programs.delay(str(stash.id))
    except Exception as e:
        RemittanceFile.objects.filter(sha256=sha).update(status="FAILED")
        raise
