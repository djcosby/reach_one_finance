# remittances/management/commands/process_inbox.py
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand
from remittances.models import RemittanceFile
from remittances.tasks import parse_remit
import shutil

class Command(BaseCommand):
    help = 'Scans the data/inbox folder and queues any new files for processing.'

    def handle(self, *args, **options):
        self.stdout.write("Starting inbox scan...")
        
        inbox_path = Path('data/inbox')
        processed_path = Path('data/processed')
        
        # Ensure the processed folder exists
        processed_path.mkdir(exist_ok=True)
        
        found_files = 0
        queued_files = 0
        
        for file_path in inbox_path.glob('*.*'): # Get all files
            if not file_path.is_file():
                continue
                
            found_files += 1
            self.stdout.write(f"  Checking: {file_path.name}")
            
            # 1. Calculate the file's hash
            content = file_path.read_bytes()
            sha = hashlib.sha256(content).hexdigest()
            
            # 2. Check if we've seen it before
            if RemittanceFile.objects.filter(sha256=sha).exists():
                self.stdout.write(self.style.WARNING(f"    Skipping (duplicate): {file_path.name}"))
                continue
                
            # 3. If new, move it to 'processed'
            new_path = processed_path / file_path.name
            shutil.move(file_path, new_path)
            
            # 4. Create the database record
            RemittanceFile.objects.create(
                sha256=sha,
                original_name=file_path.name,
                stored_path=str(new_path),
                status='STAGED' # 'STAGED' means "waiting for Celery"
            )
            
            # 5. Send the job to Celery (just like the web upload does)
            parse_remit.delay(str(new_path), sha)
            
            self.stdout.write(self.style.SUCCESS(f"    Queued for parsing: {file_path.name}"))
            queued_files += 1
            
        self.stdout.write("--------------------")
        self.stdout.write(f"Scan complete. Found {found_files} files, queued {queued_files} new files.")