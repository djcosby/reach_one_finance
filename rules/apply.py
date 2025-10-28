from celery import shared_task
from decimal import Decimal
from collections import defaultdict
from remittances.models import FinancePeriod, ClaimLine, PeriodSnapshot, Program

IOP = 'H0015'
DIFF_PER_UNIT = Decimal('52.81')

PARTNER_SPLITS = {
    'Miracle House': (Decimal('0.60'), Decimal('0.40')),
    'Stairway to Hope': (Decimal('0.60'), Decimal('0.40')),
    'Peer Support DJ': (Decimal('0.60'), Decimal('0.40')),
    'Hope over Homeless': (Decimal('0.90'), Decimal('0.10')),
}

FIXED_COSTS = {
    'Michael Collins': Decimal('5000'),
    'Monte Barnett'  : Decimal('5000'),
    'Lauren Myatt'   : Decimal('1000'),
    'Ms. Celeste'    : Decimal('500'),
    'Mr. Wallace'    : Decimal('400'),
}
HOUSING = {'Men': Decimal('2200'), 'Women': Decimal('2200')}

def r2(x:Decimal): return x.quantize(Decimal('0.01'))

def get_donation_for_period(period):  # later: configure via UI
    return Decimal('0.00')

@shared_task
def apply_rules_for_period(period_id:int):
    period = FinancePeriod.objects.get(id=period_id)
    claims = ClaimLine.objects.filter(period=period)

    program_paid = defaultdict(Decimal)
    iop_units_partner = Decimal('0')
    rors_direct = Decimal('0')

    for c in claims:
        program_paid[c.program.name] += Decimal(c.paid_amount)
        if c.program.name == 'Reach One Recovery Services':
            rors_direct += Decimal(c.paid_amount)
        else:
            if c.hcpcs_cpt == IOP:
                units = Decimal(c.units or 1)
                iop_units_partner += units

    difference_pot = iop_units_partner * DIFF_PER_UNIT

    partner_payouts = {}
    rors_share_total = Decimal('0')
    for prog, paid in program_paid.items():
        if prog in PARTNER_SPLITS:
            p_pct, r_pct = PARTNER_SPLITS[prog]
            partner_payouts[prog] = r2(paid * p_pct)
            rors_share_total += paid * r_pct

    rors_pot = r2(rors_direct + rors_share_total + difference_pot)

    fixed_total = sum(FIXED_COSTS.values())
    donation = get_donation_for_period(period)
    housing_total = sum(HOUSING.values())
    residual = r2(rors_pot - (Decimal(fixed_total) + donation + Decimal(housing_total)))
    savings = residual if residual > 0 else Decimal('0.00')
    deficit = abs(residual) if residual < 0 else Decimal('0.00')

    snapshot = {
      'totals': {
        'total_gross': r2(sum(program_paid.values())),
        'difference_pot': r2(difference_pot),
        'rors_direct': r2(rors_direct),
        'rors_share_total': r2(rors_share_total),
        'rors_pot': rors_pot,
      },
      'partner': {
        'program_paid': {k: r2(v) for k,v in program_paid.items()},
        'partner_payouts': {k: str(v) for k,v in partner_payouts.items()},
        'rors_share_total': r2(rors_share_total),
      },
      'costs': {
        'fixed_costs': {k: str(v) for k,v in FIXED_COSTS.items()},
        'fixed_total': r2(Decimal(fixed_total)),
        'donation': r2(donation),
        'housing': {k: str(v) for k,v in HOUSING.items()},
        'housing_total': r2(Decimal(housing_total)),
      },
      'result': {
        'residual': residual,
        'savings': savings,
        'deficit': deficit,
      }
    }
    PeriodSnapshot.objects.update_or_create(period=period, defaults={'math': snapshot})
