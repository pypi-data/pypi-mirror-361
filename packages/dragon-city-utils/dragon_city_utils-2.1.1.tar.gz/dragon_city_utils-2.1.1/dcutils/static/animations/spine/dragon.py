from pydantic import validate_call
from typing import Optional

from ...platform_prefixes import PlatformPrefixes
from ...base import BaseStaticDownloader

WINDOWS = "dxt5"

class DragonSpineAnimation(BaseStaticDownloader):
    @validate_call
    def __init__(
        self,
        image_name: str,
        phase: int,
        skin: Optional[str] = None,
        platform: str = WINDOWS,
        platform_prefix: str = PlatformPrefixes.IOS,
        use_new_url: bool = True
    ) -> None:
        if phase < 0 or phase > 3:
            raise ValueError(f"{phase} Not a valid number for a dragon's phase. Choose a number between 0 and 3")

        if skin and skin > 0:
            skin = f"_{skin}"
        
        else:
            skin = ""

        if use_new_url:
            self.url = f"https://{platform_prefix}-static-s1.socialpointgames.com/static/dragoncity/mobile/engine/version_1_1/dragons/{image_name}_{phase}/{image_name}{skin}_{phase}_HD_tweened_{platform}.zip"
            
        else:
            self.url = f"https://{platform_prefix}-static-s1.socialpointgames.com/static/dragoncity/mobile/engine/version_1_1/dragons/{image_name}_{phase}/basic_{image_name}{skin}_{phase}_HD_spine-3-8-59_{platform}.zip"