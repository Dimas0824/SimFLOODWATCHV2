from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IoTNode
from .serializers import IoTNodeSerializer


class IoTNodeViewSet(viewsets.ModelViewSet):
    queryset = IoTNode.objects.all().order_by("node_id")
    serializer_class = IoTNodeSerializer
    lookup_field = "node_id"


class FleetHealthView(APIView):
    def get(self, request):
        nodes = IoTNode.objects.filter(is_active=True).order_by("node_id")
        payload = [node.health_snapshot() for node in nodes]
        return Response(
            {
                "count": len(payload),
                "results": payload,
            },
            status=status.HTTP_200_OK,
        )
