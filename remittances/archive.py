import json, shutil
from pathlib import Path
from django.utils import timezone
from .models import RemittanceFile, FinancePeriod

def write_audit_and_archive(period:FinancePeriod, files:list[RemittanceFile]):
    audit = {
      "period": {"start": str(period.start), "end": str(period.end), "label": period.label},
      "files": [{"sha256": f.sha256, "name": f.original_name} for f in files],
      "created_at": timezone.now().isoformat(),
    }
    folder = Path(f"data/archive/{period.start:%Y}/{period.start:%m}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"audit_{period.label}.json").write_text(json.dumps(audit, indent=2))
    for f in files:
        shutil.move(f.stored_path, folder / Path(f.stored_path).name)
