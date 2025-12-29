#!/usr/bin/env python3
"""
Wave Link API Client for Bandit
Controls Elgato Wave Link mixer via WebSocket JSON-RPC 2.0
Endpoint: ws://127.0.0.1:1824
"""

import asyncio
import json
import websockets
from typing import Optional, Dict, Any, List

WAVELINK_WS_URL = "ws://127.0.0.1:1824"


class WaveLinkClient:
    """Client for controlling Elgato Wave Link via WebSocket API."""
    
    def __init__(self, url: str = WAVELINK_WS_URL):
        self.url = url
        self.ws = None
        self.request_id = 0
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Wave Link WebSocket server."""
        try:
            self.ws = await websockets.connect(self.url)
            self.connected = True
            print(f"✅ Connected to Wave Link at {self.url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Wave Link: {e}")
            print("   Make sure Wave Link is running!")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Wave Link."""
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("🔌 Disconnected from Wave Link")
    
    async def _send_request(self, method: str, params: Dict = None) -> Dict:
        """Send JSON-RPC request and get response."""
        if not self.connected:
            await self.connect()
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params
        
        try:
            await self.ws.send(json.dumps(request))
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            return json.loads(response)
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}
    
    # ─────────────────────────────────────────────────────────────────────────
    # MIXER CONTROL METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    async def get_app_info(self) -> Dict:
        """Get Wave Link application info."""
        return await self._send_request("getApplicationInfo")
    
    async def get_mixer_info(self) -> Dict:
        """Get current mixer state with all channels."""
        return await self._send_request("getMixerInfo")
    
    async def get_outputs(self) -> Dict:
        """Get available output devices."""
        return await self._send_request("getOutputs")
    
    async def set_input_volume(self, channel_id: str, volume: int, mix: str = "local") -> Dict:
        """
        Set volume for an input channel.
        
        Args:
            channel_id: Channel identifier
            volume: Volume level (0-100)
            mix: "local" (what you hear) or "stream" (what goes to OBS)
        """
        return await self._send_request("setInputConfig", {
            "identifier": channel_id,
            "localMixVolume" if mix == "local" else "streamMixVolume": volume
        })
    
    async def set_input_mute(self, channel_id: str, muted: bool, mix: str = "local") -> Dict:
        """Mute/unmute an input channel."""
        return await self._send_request("setInputConfig", {
            "identifier": channel_id,
            "localMixMuted" if mix == "local" else "streamMixMuted": muted
        })
    
    async def set_output_volume(self, output_id: str, volume: int) -> Dict:
        """Set volume for an output device."""
        return await self._send_request("setOutputConfig", {
            "identifier": output_id,
            "volume": volume
        })
    
    async def set_output_mute(self, output_id: str, muted: bool) -> Dict:
        """Mute/unmute an output device."""
        return await self._send_request("setOutputConfig", {
            "identifier": output_id,
            "muted": muted
        })
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONVENIENCE METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    async def mute_all(self, mix: str = "local") -> None:
        """Mute all input channels."""
        mixer = await self.get_mixer_info()
        if "result" in mixer and "inputs" in mixer["result"]:
            for inp in mixer["result"]["inputs"]:
                await self.set_input_mute(inp["identifier"], True, mix)
        print("🔇 All channels muted")
    
    async def unmute_all(self, mix: str = "local") -> None:
        """Unmute all input channels."""
        mixer = await self.get_mixer_info()
        if "result" in mixer and "inputs" in mixer["result"]:
            for inp in mixer["result"]["inputs"]:
                await self.set_input_mute(inp["identifier"], False, mix)
        print("🔊 All channels unmuted")
    
    async def list_channels(self) -> List[Dict]:
        """List all input channels with their current state."""
        mixer = await self.get_mixer_info()
        channels = []
        if "result" in mixer and "inputs" in mixer["result"]:
            for inp in mixer["result"]["inputs"]:
                channels.append({
                    "id": inp.get("identifier"),
                    "name": inp.get("name"),
                    "local_volume": inp.get("localMixVolume"),
                    "stream_volume": inp.get("streamMixVolume"),
                    "local_muted": inp.get("localMixMuted"),
                    "stream_muted": inp.get("streamMixMuted"),
                })
        return channels
    
    async def print_status(self):
        """Print current mixer status."""
        print("\n🎛️  WAVE LINK MIXER STATUS")
        print("=" * 50)
        
        channels = await self.list_channels()
        for ch in channels:
            mute_icon = "🔇" if ch.get("local_muted") else "🔊"
            print(f"{mute_icon} {ch['name']}: {ch['local_volume']}% (local) | {ch['stream_volume']}% (stream)")


async def demo():
    """Demo Wave Link control."""
    client = WaveLinkClient()
    
    if await client.connect():
        # Get app info
        info = await client.get_app_info()
        print(f"App Info: {json.dumps(info, indent=2)}")
        
        # Print mixer status
        await client.print_status()
        
        # Disconnect
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(demo())
