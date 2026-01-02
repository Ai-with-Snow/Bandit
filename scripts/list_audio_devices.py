"""
List all available audio input devices
Helps identify the correct device index for Elgato Wave Link
"""
import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    
    print("=" * 80)
    print("AVAILABLE AUDIO INPUT DEVICES")
    print("=" * 80)
    
    input_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        
        # Only show input devices
        if info['maxInputChannels'] > 0:
            input_devices.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels'],
                'sample_rate': int(info['defaultSampleRate'])
            })
            
            # Highlight Elgato devices
            is_elgato = 'elgato' in info['name'].lower() or 'wave' in info['name'].lower()
            prefix = ">>> " if is_elgato else "    "
            
            print(f"{prefix}[{i}] {info['name']}")
            print(f"{prefix}    Channels: {info['maxInputChannels']}, Sample Rate: {int(info['defaultSampleRate'])} Hz")
            
            if is_elgato:
                print(f"{prefix}    ⭐ ELGATO DEVICE DETECTED!")
            print()
    
    p.terminate()
    
    # Show default device
    try:
        p = pyaudio.PyAudio()
        default_info = p.get_default_input_device_info()
        print("=" * 80)
        print(f"DEFAULT INPUT DEVICE: [{default_info['index']}] {default_info['name']}")
        print("=" * 80)
        p.terminate()
    except:
        print("No default input device found")
    
    return input_devices

if __name__ == "__main__":
    devices = list_audio_devices()
    
    # Look for Elgato specifically
    elgato_devices = [d for d in devices if 'elgato' in d['name'].lower() or 'wave' in d['name'].lower() or 'chat mix' in d['name'].lower()]
    
    if elgato_devices:
        print("\n" + "=" * 80)
        print("🎙️ ELGATO DEVICES FOUND:")
        print("=" * 80)
        for device in elgato_devices:
            print(f"Device Index: {device['index']}")
            print(f"Name: {device['name']}")
            print(f"Channels: {device['channels']}")
            print(f"Sample Rate: {device['sample_rate']} Hz")
            print()
            print(f"To use this device in voice_thinking.py, set:")
            print(f"  self.input_device = {device['index']}")
            print()
    else:
        print("\n⚠️ No Elgato devices found. Make sure Wave Link is running and your mic is connected.")
