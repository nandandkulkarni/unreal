# Available Sequence Control Functions

Generated: 2025-12-16

## LevelSequenceEditorBlueprintLibrary

Key playback functions:
- **Play()** - Start playback forwards from current time cursor
- **Pause()** - Pause playback
- **PlayTo()** - Play to a specific position then pause
- **SetLockCameraCutToViewport(bLock)** - Lock viewport to camera cuts (CRITICAL for viewing animation)
- **IsCameraCutLockedToViewport()** - Check lock status
- **ForceUpdate()** - Force sequencer evaluation and UI update immediately
- **IsPlaying()** - Check if actively playing
- **OpenLevelSequence(LevelSequence)** - Open a level sequence asset
- **FocusLevelSequence(SubSection)** - Focus on sequence
- **CloseLevelSequence()** - Close sequence
- **RefreshCurrentLevelSequence()** - Refresh current sequence

Playback control:
- **SetPlaybackSpeed(float)** - Set playback speed
- **GetPlaybackSpeed()** - Get current speed
- **SetLoopMode()** - Configure looping
- **GetLoopMode()** - Get loop mode
- **SetCurrentTime()** - Set playhead position
- **GetCurrentTime()** - Get current time
- **GetLocalPosition(TimeUnit)** - Get local playhead
- **SetLocalPosition()** - Set local position
- **GetGlobalPosition(TimeUnit)** - Get global playhead

Sequence info:
- **GetCurrentLevelSequence()** - Get currently opened root sequence
- **GetFocusedLevelSequence()** - Get focused sequence in hierarchy
- **GetBoundObjects(ObjectBinding)** - Get objects bound to binding ID
- **GetSubSequenceHierarchy()** - Get sub-sequence hierarchy

Selection:
- **SelectBindings()** - Select object bindings
- **SelectTracks()** - Select tracks
- **SelectSections()** - Select sections
- **EmptySelection()** - Clear selection

## LevelSequencePlayer (Runtime)

For runtime playback (not editor):
- **Play()** - Start forward playback
- **PlayReverse()** - Reverse playback
- **PlayLooping(NumLoops)** - Loop playback
- **Pause()** - Pause
- **Stop()** - Stop and move to end/start
- **StopAtCurrentTime()** - Stop without moving cursor
- **Scrub()** - Scrub playback
- **GoToEndAndStop()** - Jump to end
- **SetPlaybackPosition(PlaybackParams)** - Evaluate to position
- **SetDisableCameraCuts(bool)** - Disable camera cuts
- **SetHideHud(bool)** - Hide HUD during play

## Key Findings

**Critical for remote playback:**
1. `SetLockCameraCutToViewport(true)` - Must be called to see animation in viewport
2. `ForceUpdate()` - Ensures UI and evaluation sync
3. `Play()` - Starts playback

**Workflow for remote playback:**
```
1. OpenLevelSequence(sequence_path)
2. SetLockCameraCutToViewport(true)
3. ForceUpdate()
4. Play()
```
