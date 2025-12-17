# Solution: Adding Keyframes to Sequencer

## ✅ SOLVED: ExecutePythonCommand Works!

## Problem
MovieSceneScriptingFloatChannel objects returned by `GetAllChannels()` are **transient Python wrapper objects** that cannot be serialized through the Remote Control API's HTTP/JSON interface. When we try to call `AddKey` on these channels remotely, we get "Invalid ChannelHandle" errors.

## Root Cause
- Remote Control API can only pass **primitive types** (strings, ints, floats, structs of primitives)
- Channels are `/Engine/Transient` Python objects that only exist in the current interpreter session
- When passed through HTTP, the transient path cannot be deserialized back into a valid channel object
- Result: HTTP 200 response but "Invalid ChannelHandle" logged in Unreal

## ✅ THE SOLUTION: ExecutePythonCommand

Run Python code **inside Unreal** where channel objects exist natively:

```python
import requests

python_code = '''
import unreal

# Get sequence and channels
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
binding = bindings[0]
tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
transform_track = next(t for t in tracks if isinstance(t, unreal.MovieScene3DTransformTrack))
sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
section = sections[0]
channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)

# Add keyframes - channels are REAL objects here!
frame = unreal.FrameNumber(100)
channels[0].add_key(frame, 500.0)  # Location.X
channels[1].add_key(frame, 300.0)  # Location.Y
channels[2].add_key(frame, 150.0)  # Location.Z

print("Keyframes added successfully!")
'''

response = requests.put(
    "http://localhost:30010/remote/object/call",
    json={
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_code}
    }
)
```

## Configuration Required

In `CinematicPipeline/Config/DefaultEngine.ini`:

```ini
[RemoteControl]
bRestrictServerAccess=true
bRemoteExecution=true
bEnableRemotePythonExecution=true
+RemoteControlWebInterfaceAllowedObjects=/Script/PythonScriptPlugin.PythonScriptLibrary
```

**Important:** Restart Unreal Editor after config changes!

## Why This Works

| Approach | Why It Fails/Works |
|----------|-------------------|
| HTTP AddKey with channel path | ❌ Channel is transient `/Engine/Transient.Location.X_7` |
| GetChannel + ChannelIndex | ❌ Returns empty string, silently fails |
| Section + ChannelName params | ❌ No such API method exists |
| **ExecutePythonCommand** | ✅ **Code runs inside Unreal's Python interpreter where channels are real objects** |

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
