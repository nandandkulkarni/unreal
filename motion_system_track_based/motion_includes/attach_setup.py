# Attach setup module for Unreal
# Handles MovieScene3DAttachTrack creation

import unreal

def log(msg):
    print(msg)


def setup_attachment(sequence, child_binding, parent_binding, 
                     socket_name: str = "",
                     start_frame: int = 0,
                     end_frame: int = None,
                     location_rule: str = "KEEP_RELATIVE",
                     rotation_rule: str = "KEEP_RELATIVE",
                     scale_rule: str = "KEEP_RELATIVE"):
    """
    Add an Attach Track to the child actor in the sequence.
    
    This creates Unreal's native MovieScene3DAttachTrack which links
    the child actor to a parent actor (optionally at a specific socket).
    
    Args:
        sequence: Level sequence asset
        child_binding: MovieSceneBindingProxy for the child actor
        parent_binding: MovieSceneBindingProxy for the parent actor
        socket_name: Optional socket on parent's skeletal mesh
        start_frame: Frame when attachment begins
        end_frame: Frame when attachment ends (None = entire sequence)
        location_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
        rotation_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
        scale_rule: KEEP_RELATIVE, KEEP_WORLD, or SNAP_TO_TARGET
    
    Returns:
        The created MovieScene3DAttachTrack or None on failure
    """
    try:
        # Add attach track to child binding
        attach_track = child_binding.add_track(unreal.MovieScene3DAttachTrack)
        
        if not attach_track:
            log(f"  ✗ Failed to create attach track")
            return None
        
        # Add section
        attach_section = attach_track.add_section()
        
        if not attach_section:
            log(f"  ✗ Failed to create attach section")
            return None
        
        # Set the parent binding
        parent_binding_id = parent_binding.get_binding_id()
        attach_section.set_constraint_binding_id(parent_binding_id)
        
        # Set socket name if specified
        if socket_name:
            attach_section.set_attach_socket_name(socket_name)
        
        # Set time range
        attach_section.set_range(start_frame, end_frame if end_frame else sequence.get_playback_end())
        
        # Set attachment rules
        rule_map = {
            "KEEP_RELATIVE": unreal.EAttachmentRule.KEEP_RELATIVE,
            "KEEP_WORLD": unreal.EAttachmentRule.KEEP_WORLD,
            "SNAP_TO_TARGET": unreal.EAttachmentRule.SNAP_TO_TARGET
        }
        
        loc_rule = rule_map.get(location_rule, unreal.EAttachmentRule.KEEP_RELATIVE)
        rot_rule = rule_map.get(rotation_rule, unreal.EAttachmentRule.KEEP_RELATIVE)
        scale_r = rule_map.get(scale_rule, unreal.EAttachmentRule.KEEP_RELATIVE)
        
        # Note: Setting rules may vary by UE version
        # attach_section.set_attach_location_rule(loc_rule)
        # attach_section.set_attach_rotation_rule(rot_rule)
        # attach_section.set_attach_scale_rule(scale_r)
        
        log(f"  ✓ Attached to parent (socket: {socket_name or 'root'})")
        return attach_track
        
    except Exception as e:
        log(f"  ✗ Failed to setup attachment: {e}")
        return None


def process_attachments(sequence, actors_info, fps):
    """
    Process all pending attachments after actors are spawned.
    
    Args:
        sequence: Level sequence asset
        actors_info: Dict of actor_name -> {actor, binding, attachment_data}
        fps: Frames per second
    """
    for actor_name, info in actors_info.items():
        attachment = info.get("attachment")
        if not attachment:
            continue
        
        parent_name = attachment.get("parent_actor")
        if not parent_name:
            continue
        
        if parent_name not in actors_info:
            log(f"  ⚠ Attachment parent '{parent_name}' not found for {actor_name}")
            continue
        
        parent_info = actors_info[parent_name]
        
        log(f"  Setting up attachment: {actor_name} → {parent_name}")
        
        setup_attachment(
            sequence=sequence,
            child_binding=info["binding"],
            parent_binding=parent_info["binding"],
            socket_name=attachment.get("socket_name", ""),
            start_frame=attachment.get("start_frame", 0),
            end_frame=attachment.get("end_frame"),
            location_rule=attachment.get("location_rule", "KEEP_RELATIVE"),
            rotation_rule=attachment.get("rotation_rule", "KEEP_RELATIVE"),
            scale_rule=attachment.get("scale_rule", "KEEP_RELATIVE")
        )
