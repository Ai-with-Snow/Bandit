import os
import requests
import logging

class LIFXService:
    """LIFX HTTP API Service for light control."""
    
    BASE_URL = "https://api.lifx.com/v1/lights/"
    
    def __init__(self, token=None):
        self.token = token or os.getenv("LIFX_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            logging.warning("LIFX_TOKEN not found. Light control will fail.")

    def _log_error(self, method, e):
        """Helper to log detailed error info including response body."""
        text = getattr(e.response, 'text', '') if hasattr(e, 'response') else ''
        logging.error(f"LIFX Error ({method}): {e} {text}")

    def get_lights(self, selector="all"):
        """Get state of lights."""
        try:
            response = self.session.get(f"{self.BASE_URL}{selector}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("get_lights", e)
            return None

    def toggle(self, selector="all", duration=1.0):
        """Toggle power for selected lights."""
        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/toggle", json={"duration": duration})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("toggle", e)
            return None

    def set_state(self, selector="all", power=None, color=None, brightness=None, duration=1.0, fast=False):
        """Set state for selected lights."""
        payload = {"duration": duration, "fast": fast}
        if power: payload["power"] = power
        if color: payload["color"] = color
        if brightness is not None: payload["brightness"] = brightness

        try:
            response = self.session.put(f"{self.BASE_URL}{selector}/state", json=payload)
            if fast and response.status_code == 202: return {"status": "accepted"}
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("set_state", e)
            return None

    def breathe(self, selector="all", color="purple", period=1.0, cycles=5, persist=False, peak=0.5):
        """Fade between two colors."""
        payload = {"color": color, "period": period, "cycles": cycles, "persist": persist, "peak": peak}
        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/effects/breathe", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("breathe", e)
            return None

    def pulse(self, selector="all", color="red", period=0.5, cycles=3, persist=False):
        """Fast flash effect."""
        payload = {"color": color, "period": period, "cycles": cycles, "persist": persist}
        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/effects/pulse", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("pulse", e)
            return None

    def morph(self, selector="all", palette=None, duration=5.0, speed=1.0):
        """Morph effect for multizone devices."""
        payload = {"palette": palette or ["red", "orange", "yellow", "green", "blue", "purple"], "duration": duration, "speed": speed}
        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/effects/morph", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("morph", e)
            return None

    def list_scenes(self):
        """List all available scenes."""
        try:
            response = self.session.get("https://api.lifx.com/v1/scenes")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("list_scenes", e)
            return None

    def activate_scene(self, scene_id, duration=1.0, fast=False):
        """Activate a scene by ID."""
        payload = {"duration": duration, "fast": fast}
        try:
            response = self.session.put(f"https://api.lifx.com/v1/scenes/scene_id:{scene_id}/activate", json=payload)
            if fast and response.status_code == 202: return {"status": "accepted"}
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("activate_scene", e)
            return None

    def validate_color(self, color_string):
        """Validate a color string via LIFX API."""
        try:
            response = self.session.get(f"https://api.lifx.com/v1/color?string={color_string}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("validate_color", e)
            return None

    def clean(self, selector="all", stop=False, duration=0):
        """Switch a light to clean mode."""
        payload = {"stop": stop, "duration": duration}
        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/clean", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("clean", e)
            return None

    def state_delta(self, selector="all", power=None, duration=1.0, hue=None, saturation=None, brightness=None, kelvin=None, fast=False):
        """Additive state changes (e.g., brightness +0.1)."""
        payload = {"duration": duration, "fast": fast}
        if power: payload["power"] = power
        if hue is not None: payload["hue"] = hue
        if saturation is not None: payload["saturation"] = saturation
        if brightness is not None: payload["brightness"] = brightness
        if kelvin is not None: payload["kelvin"] = kelvin

        try:
            response = self.session.post(f"{self.BASE_URL}{selector}/state/delta", json=payload)
            if fast and response.status_code == 202: return {"status": "accepted"}
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("state_delta", e)
            return None

    def set_states(self, states, defaults=None):
        """Set states for multiple selectors in one request."""
        payload = {
            "states": states
        }
        if defaults:
            payload["defaults"] = defaults

        try:
            response = self.session.put(f"https://api.lifx.com/v1/lights/states", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log_error("set_states", e)
            return None
