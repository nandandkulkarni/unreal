"""
Centralized asset paths for the Motion System.
"""

class Characters:
    BELICAX = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica"
    BELICA = "/Game/MetaHumans/Pia/BP_Pia.BP_Pia"
    PIA = "/Game/MetaHumans/Pia/BP_Pia.BP_Pia"
    QUINN_SIMPLE = "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"
    QUINN_THIRD_PERSON = "/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple"
    BELICA_OLD = "/Game/Characters/Belica/Mesh/SK_Belica" # Legacy

class Shapes:
    CUBE = "/Engine/BasicShapes/Cube.Cube"
    CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"
    # Basic Shapes for spawning (Actor Factories often use just the name without extension, but LoadObject needs full path)
    CUBE_PATH = "/Engine/BasicShapes/Cube" 
    CYLINDER_PATH = "/Engine/BasicShapes/Cylinder"

class Materials:
    RED = "/Game/MyMaterial/MyRed"
    BLUE = "/Game/MyMaterial/MyBlue"
    GREEN = "/Game/MyMaterial/MyGreen"
    YELLOW = "/Game/MyMaterial/MyYellow"
    
    @staticmethod
    def get_color(color_name: str):
        mapping = {
            "red": Materials.RED,
            "blue": Materials.BLUE,
            "green": Materials.GREEN,
            "yellow": Materials.YELLOW
        }
        return mapping.get(color_name.lower(), Materials.RED)

class Animations:
    PIA_JOG_FWD = "/Game/MetaHumans/Pia/Animations2/Unarmed/pia_rtg_3_MF_Unarmed_Jog_Fwd.pia_rtg_3_MF_Unarmed_Jog_Fwd"
    
    def belica(anim_name):
        return f"/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/{anim_name}.{anim_name}"
