from __future__ import annotations

from django import forms

from .models import IoTNode


class IoTNodeAdminForm(forms.ModelForm):
    class Meta:
        model = IoTNode
        fields = "__all__"
        widgets = {
            "simulation_distance_cm": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": 0,
                    "max": 400,
                    "step": 0.1,
                    "data-range-output": "simulation-distance-output",
                }
            ),
            "simulation_drift_bias_cm": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": -100,
                    "max": 100,
                    "step": 0.1,
                    "data-range-output": "simulation-drift-output",
                }
            ),
        }

    class Media:
        js = ("devices/admin/iotnode_simulation.js",)
