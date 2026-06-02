from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from devices.models import IoTNode
from telemetry.serializers import TelemetrySerializer

from .control import apply_control_message
from .services import FloodWatchSimulator


class SimulatorControlView(APIView):
    def post(self, request):
        if not isinstance(request.data, dict):
            return Response({"detail": "Payload JSON object wajib."}, status=status.HTTP_400_BAD_REQUEST)

        payload = dict(request.data)
        node_id = payload.get("node_id") or payload.get("nodeId")
        if not node_id:
            return Response({"detail": "node_id atau nodeId wajib diisi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            node = IoTNode.objects.get(node_id=node_id)
        except IoTNode.DoesNotExist:
            return Response({"detail": f"Node `{node_id}` tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = apply_control_message(node, payload, persist=True)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


class SimulatorTickView(APIView):
    def post(self, request, node_id: str):
        try:
            node = IoTNode.objects.get(node_id=node_id)
        except IoTNode.DoesNotExist:
            return Response({"detail": f"Node `{node_id}` tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        telemetry, payload = FloodWatchSimulator(node).tick()
        serializer = TelemetrySerializer(telemetry)
        return Response(
            {
                "payload": payload,
                "telemetry": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
