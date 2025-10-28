from pathlib import Path
from django.template.loader import render_to_string
from remittances.models import PeriodSnapshot, FinancePeriod

# apps/reports/services.py
def render_master_html(snapshot:dict, period:FinancePeriod) -> Path:
    html = render_to_string('reports/master.html', {
        'period': period, 'totals': format_totals(snapshot),
        'remittances': build_remittance_rows(period),
        'programs': build_program_rows(snapshot),
        'partner_rows': build_partner_rows(snapshot),
        'partner_totals': build_partner_totals(snapshot),
        'adjustments': {'iop_units': snapshot['adjustments']['iop_units']},
        'costs': format_costs(snapshot),
        'housing': infer_housing_status(snapshot),
        'result': format_result(snapshot),
        'links': roster_links(period)
    })
    out = Path(f'exports/reports/master_{period.label}.html')
    out.write_text(html, encoding='utf-8')
    return out
