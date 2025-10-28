from django.shortcuts import render

# Create your views here.
import hashlib
from pathlib import Path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import RemittanceFile
from .tasks import parse_remit

@api_view(['POST'])
@permission_classes([AllowAny])  # tighten later
def upload_pdf(request):
    f = request.FILES['pdf']
    content = f.read()
    sha = hashlib.sha256(content).hexdigest()

    if RemittanceFile.objects.filter(sha256=sha).exists():
        return Response({'detail': 'Duplicate file already processed.'}, status=200)

    path = Path('data/inbox') / f.name
    path.write_bytes(content)
    RemittanceFile.objects.create(sha256=sha, original_name=f.name,
                                  stored_path=str(path), status='STAGED')
    parse_remit.delay(str(path), sha)
    return Response({'detail':'Queued for parsing'})
