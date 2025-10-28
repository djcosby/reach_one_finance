# apps/reports/sheets.py
def push_to_sheet(sheet_id:str, tab_name:str, rows:list[list[str]]):
    body = {'valueInputOption': 'USER_ENTERED',
            'data':[{'range': f"'{tab_name}'!A1", 'majorDimension':'ROWS', 'values': rows}]}
    sheets.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()

def write_audit_and_archive(period:FinancePeriod, files:list[RemittanceFile]):
    audit = {
      "period": {"start": str(period.start), "end": str(period.end), "label": period.label},
      "files": [{"sha256": f.sha256, "name": f.original_name} for f in files],
      "created_at": timezone.now().isoformat(),
      "user": get_current_email(),
    }
    folder = Path(f"/data/archive/{period.start:%Y}/{period.start:%m}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"audit_{period.label}.json").write_text(json.dumps(audit, indent=2))
    for f in files:
        shutil.move(f.stored_path, folder / Path(f.stored_path).name)

