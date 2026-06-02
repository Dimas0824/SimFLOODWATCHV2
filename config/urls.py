from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from devices.views import FleetHealthView, IoTNodeViewSet
from simulator.views import SimulatorControlView, SimulatorTickView
from telemetry.views import TelemetryViewSet


router = DefaultRouter()
router.register("nodes", IoTNodeViewSet, basename="node")
router.register("telemetry", TelemetryViewSet, basename="telemetry")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/health/", FleetHealthView.as_view(), name="fleet-health"),
    path("api/simulator/control/", SimulatorControlView.as_view(), name="simulator-control"),
    path("api/simulator/tick/<str:node_id>/", SimulatorTickView.as_view(), name="simulator-tick"),
]
