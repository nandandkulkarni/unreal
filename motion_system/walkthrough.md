# Walkthrough: Cinematic Movie-Making Features

I have significantly enhanced the motion system to support high-quality movie production. You can now create cinematic sequences with smooth movement and intelligent camera tracking using simple JSON scripts.

## Key Enhancements

### 1. Smooth Cinematic Motion (Cubic Interpolation)
No more robotic, linear movements! All location and rotation keyframes now use **Cubic (Auto-Bezier)** interpolation by default. This creates natural-looking ease-in/ease-out for both characters and cameras.

### 2. Native Camera Tracking & Auto-Focus
I've harnessed Unreal's native `CineCameraActor` features:
- **LookAt Tracking**: The camera will intelligently stay pointed at your target.
- **Cinematic Smoothing**: Use `interp_speed` to give the camera a "lag" effect, making it feel like a real operator.
- **Auto-Focus**: The camera automatically tracks the target's distance and stays in sharp focus.

### 3. Simple Movie Trigger Workflow
I created a `trigger_movie.py` script that lets you run any JSON scene from your terminal:
```bash
python trigger_movie.py movies/scene_03_cinematic.json
```

> [!NOTE]
> **Workflow Optimization**: Shots are now capped at **15 seconds** for fast iteration, and the **Sequencer opens automatically** whenever a scene is generated.

---

## Example Cinematic Script
Here is how you define a cinematic shot in `scene_03_cinematic.json`:

```json
{
    "command": "add_camera", 
    "actor": "MainCam", 
    "location": [-500, -500, 250], 
    "look_at_actor": "Hero",
    "offset": [0, 0, 150],  // Target the chest/head, not feet
    "interp_speed": 10.0    // Smooth "laggy" follow
}
```

## How to Verify in Unreal
1.  Run the command above.
2.  Open the **Sequencer** in Unreal Editor.
3.  Observe the **Cubic Curves** in the Transform track (right-click a keyframe and check "Interpolation").
4.  Play the sequence and watch the camera smoothly track the "Hero" actor while maintaining focus.
