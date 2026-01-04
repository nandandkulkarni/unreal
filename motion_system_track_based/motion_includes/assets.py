"""
Centralized asset paths for the Motion System.
"""

class CharacterData:
    """Structure for character asset properties"""
    def __init__(self, path: str, height: float = 1.8, initial_yaw: float = -90.0):
        self.path = path
        self.height = height
        self.initial_yaw = initial_yaw

    def __repr__(self):
        return f"CharacterData(path='{self.path}', height={self.height}, initial_yaw={self.initial_yaw})"

class Characters:
    BELICA = CharacterData("/Game/ParagonLtBelica/Characters/Heroes/Belica/Meshes/Belica.Belica", 1.8)
    PIA = CharacterData("/Game/MetaHumans/Pia/BP_Pia.BP_Pia", 1.56)
    HANA = CharacterData("/Game/MetaHumans/Hana/BP_Hana.BP_Hana", 1.63) # Approx
    QUINN_SIMPLE = CharacterData("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple", 1.81)
    QUINN_THIRD_PERSON = CharacterData("/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple", 1.7)
    YIN = CharacterData('/Game/ParagonYin/Characters/Heroes/Yin/Meshes/Yin.Yin', 1.82)
    
    @staticmethod
    def get_path(name: str):
        """Get character path by case-insensitive name."""
        name_upper = name.upper()
        if hasattr(Characters, name_upper):
            obj = getattr(Characters, name_upper)
            if isinstance(obj, CharacterData):
                return obj.path
            return obj
        return name 

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
