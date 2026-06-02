from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Telemetry
from .serializers import TelemetrySerializer


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TelemetrySerializer

    def get_queryset(self):
        queryset = Telemetry.objects.select_related("node").all()
        node_id = self.request.query_params.get("node_id")
        status_value = self.request.query_params.get("status")
        if node_id:
            queryset = queryset.filter(node__node_id=node_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        node_id = request.query_params.get("node_id")
        queryset = self.get_queryset()
        if node_id:
            instance = queryset.first()
            if instance is None:
                return Response(None)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        latest_by_node = []
        seen = set()
        for item in queryset:
            if item.node.node_id in seen:
                continue
            seen.add(item.node.node_id)
            latest_by_node.append(item)
        serializer = self.get_serializer(latest_by_node, many=True)
        return Response(serializer.data)
