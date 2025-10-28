from celery import shared_task
from .models import StagedClaims, ClientRoster, Program, FinancePeriod, ClaimLine
from .normalize import from_json
from django.utils.crypto import get_random_string
from datetime import date

def normalize_name(n): return " ".join(n.strip().lower().split())

def create_period_if_needed():
    # Simple example: treat "this month 1–15" as the current period; replace with your selector UI
    start = date.today().replace(day=1)
    end = date.today()
    label = f"{start:%Y-%m-%d}_{end:%m-%d}"
    fp, _ = FinancePeriod.objects.get_or_create(label=label, defaults={'start': start, 'end': end})
    return fp

@shared_task
def route_programs(staged_id:str):
    st = StagedClaims.objects.get(id=staged_id)
    claims = from_json(st.payload)
    unknown = set()
    program_cache = {p.name: p.id for p in Program.objects.all()}
    roster = {r.norm_name: r.program_id for r in ClientRoster.objects.all()}

    for c in claims:
        nm = normalize_name(c['client_name'])
        if nm not in roster:
            unknown.add(c['client_name'])

    if unknown:
        # In a real app, create an ActionItem and show a UI to assign programs
        raise Exception(f"Unknown clients need assignment: {sorted(unknown)}")

    # Persist claims into current period
    period = create_period_if_needed()
    for c in claims:
        prog_id = roster[normalize_name(c['client_name'])]
        ClaimLine.objects.create(
            period=period, payer=c['payer'], check_date=c['check_date'],
            check_amount=c['check_amount'], client_name=c['client_name'],
            hcpcs_cpt=c['hcpcs_cpt'], units=c['units'],
            billed_amount=c['billed_amount'], paid_amount=c['paid_amount'],
            service_date=c['service_date'], program_id=prog_id, meta=c['notes']
        )
    from rules.apply import apply_rules_for_period
    apply_rules_for_period.delay(period.id)
