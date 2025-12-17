# Solution: Adding Keyframes to Sequencer

## Problem
MovieSceneScriptingFloatChannel objects returned by `GetAllChannels()` are Python wrapper objects that cannot be serialized through the Remote Control API. When we try to call `AddKey` on these channels, we get "Invalid ChannelHandle" errors.

## Root Cause
The Unreal Remote Control API can only pass simple data types (strings, numbers, structs) - it cannot pass Python object references. Channel objects must exist in the same Python interpreter session where they're used.

## Solution Options

### Option 1: Run Python Script Inside Unreal (RECOMMENDED)
Execute the Python script directly in Unreal's Python console or via a startup script.

**Script location:** `CinematicPipeline_Scripts/unreal_scripts/add_keyframes_to_sequence.py`

**How to run:**
1. Open Unreal Engine
2. Open Output Log (Window > Developer Tools > Output Log)
3. Switch to "Python" tab or Cmd prompt
4. Run:
   ```python
   exec(open(r'C:/U/CinematicPipeline_Scripts/unreal_scripts/add_keyframes_to_sequence.py').read())
   ```

### Option 2: Enable PythonScriptLibrary in Remote Control
1. Edit > Project Settings
2. Plugins > Remote Control API
3. Add `/Script/PythonScriptPlugin.Default__PythonScriptLibrary` to allowed objects
4. Restart Unreal
5. Run: `python CinematicPipeline_Scripts/external_control/execute_python_file.py`

### Option 3: Use Recording/Baking Instead
Instead of manually adding keyframes, record actor movement:
- Use "Record" feature in Sequencer
- Move actors in viewport while recording
- Sequencer automatically creates keyframes

## Technical Details

### Why Remote Control Doesn't Work
```python
# This FAILS via Remote Control:
channels = GetAllChannels(section)  # Returns: ["/Engine/Transient.Location.X_4", ...]
AddKey(channels[0], ...)  # ERROR: Channel handle invalid!
```

The channel paths are transient Python objects that only exist in that interpreter session.

### Why Native Python Works
```python
# This WORKS in Unreal Python:
channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
channel = channels[0]  # Real Python object reference
channel.add_key(frame, value)  # SUCCESS! Same interpreter session
```

## Correct API Usage (Inside Unreal Python)

```python
import unreal

# Get sequence and binding
sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
binding = bindings[0]

# Get transform track and section
tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
transform_track = next(t for t in tracks if isinstance(t, unreal.MovieScene3DTransformTrack))
sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
section = sections[0]

# Get channels (returns real Python objects)
channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)

# Add keyframes (works because we're in same Python session!)
for i, value in enumerate([100, 200, 300]):
    frame_time = unreal.FrameNumber(i * 10)
    key = channels[0].add_key(  # Instance method on channel object
        frame_time,
        value,
        0.0,  # sub_frame
        unreal.SequenceTimeUnit.DISPLAY_RATE,
        unreal.MovieSceneKeyInterpolation.LINEAR
    )
```

## Recommendation
Use the Unreal Python script (`add_keyframes_to_sequence.py`) and run it inside Unreal's Python console. This is the most reliable method that doesn't require project setting changes.
