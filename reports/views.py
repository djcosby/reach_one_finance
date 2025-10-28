from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .services import render_master_html

@api_view(['POST'])
@permission_classes([AllowAny])
def build_master(request):
    period_id = int(request.data['period_id'])
    path = render_master_html(period_id)
    return Response({'html_path': path})
