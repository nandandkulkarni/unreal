"""
Playback recorded movements from JSON file.
This creates smooth interpolated movement between keyframes.
"""
import requests
import json
import time
import math

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def set_actor_location(self, actor_path, x, y, z):
        """Move actor to position"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorLocation',
            'parameters': {
                'NewLocation': {'X': x, 'Y': y, 'Z': z}
            },
            'generateTransaction': True
        }
        try:
            resp = requests.put(url, json=payload, timeout=2)
            return resp.status_code == 200
        except:
            return False

    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        """Set actor rotation"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorRotation',
            'parameters': {
                'NewRotation': {'Pitch': pitch, 'Yaw': yaw, 'Roll': roll}
            },
            'generateTransaction': True
        }
        try:
            resp = requests.put(url, json=payload, timeout=2)
            return resp.status_code == 200
        except:
            return False


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t


def lerp_angle(a, b, t):
    """Interpolate angles (handles wraparound)"""
    diff = b - a
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360
    return a + diff * t


def playback_movement(filename='movement_recording.json', speed=1.0, smooth=True):
    """
    Play back recorded movement.
    
    Args:
        filename: JSON file with recorded keyframes
        speed: Playback speed multiplier (1.0 = normal, 2.0 = double speed)
        smooth: If True, interpolate between keyframes for smooth motion
    """
    controller = UnrealController()
    
    # Load recording
    with open(filename, 'r') as f:
        data = json.load(f)
    
    actor_path = data['actor_path']
    keyframes = data['keyframes']
    
    if len(keyframes) < 2:
        print("Not enough keyframes to play back")
        return
    
    total_duration = keyframes[-1]['time']
    
    print("="*60)
    print("PLAYING BACK MOVEMENT")
    print("="*60)
    print(f"Actor: {actor_path}")
    print(f"Duration: {total_duration:.2f}s (at {speed}x = {total_duration/speed:.2f}s)")
    print(f"Keyframes: {len(keyframes)}")
    print(f"Smooth interpolation: {smooth}")
    print("="*60)
    
    if smooth:
        # Smooth playback with interpolation
        fps = 30  # Target frames per second
        frame_time = 1.0 / fps
        current_time = 0
        
        start_real_time = time.time()
        
        while current_time <= total_duration:
            # Find surrounding keyframes
            kf_before = keyframes[0]
            kf_after = keyframes[-1]
            
            for i, kf in enumerate(keyframes):
                if kf['time'] <= current_time:
                    kf_before = kf
                if kf['time'] >= current_time and i > 0:
                    kf_after = kf
                    break
            
            # Calculate interpolation factor
            if kf_before['time'] == kf_after['time']:
                t = 0
            else:
                t = (current_time - kf_before['time']) / (kf_after['time'] - kf_before['time'])
            
            # Interpolate position
            x = lerp(kf_before['location']['X'], kf_after['location']['X'], t)
            y = lerp(kf_before['location']['Y'], kf_after['location']['Y'], t)
            z = lerp(kf_before['location']['Z'], kf_after['location']['Z'], t)
            
            # Interpolate rotation
            pitch = lerp_angle(kf_before['rotation']['Pitch'], kf_after['rotation']['Pitch'], t)
            yaw = lerp_angle(kf_before['rotation']['Yaw'], kf_after['rotation']['Yaw'], t)
            roll = lerp_angle(kf_before['rotation']['Roll'], kf_after['rotation']['Roll'], t)
            
            # Apply to actor
            controller.set_actor_location(actor_path, x, y, z)
            controller.set_actor_rotation(actor_path, pitch, yaw, roll)
            
            # Progress display
            progress = int((current_time / total_duration) * 50)
            bar = "█" * progress + "░" * (50 - progress)
            print(f"\r[{bar}] {current_time:.1f}s / {total_duration:.1f}s", end="", flush=True)
            
            # Wait for next frame
            time.sleep(frame_time / speed)
            current_time += frame_time
        
        print()  # New line after progress bar
    else:
        # Simple keyframe-to-keyframe playback
        for i, kf in enumerate(keyframes):
            loc = kf['location']
            rot = kf['rotation']
            
            print(f"\nKeyframe {i+1}/{len(keyframes)}: ({loc['X']}, {loc['Y']}, {loc['Z']})")
            
            controller.set_actor_location(actor_path, loc['X'], loc['Y'], loc['Z'])
            controller.set_actor_rotation(actor_path, rot['Pitch'], rot['Yaw'], rot['Roll'])
            
            if i < len(keyframes) - 1:
                wait_time = (keyframes[i+1]['time'] - kf['time']) / speed
                time.sleep(wait_time)
    
    print("\n" + "="*60)
    print("✓ PLAYBACK COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    import sys
    
    speed = 1.0
    smooth = True
    
    # Parse command line args
    if len(sys.argv) > 1:
        try:
            speed = float(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        smooth = sys.argv[2].lower() != 'false'
    
    playback_movement(speed=speed, smooth=smooth)
