from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Any, Union
    

class ZoneArray(RootModel[dict[str, Any]]):
    root: dict[str, Any] = Field(default_factory=dict, alias="zonearrayitem")
    
class Zone(BaseModel):
    zone_name: str = Field(..., alias='zonename')
    zone_keys: dict[str, Union[str, int]] = Field(default_factory=dict, alias='zonekeys')
    zone_arrays: list[ZoneArray] = Field(default_factory=list, alias='zonearray')
    zone_delete: bool = Field(default=False, alias='zonedelete')

    

    
class ZoneCollection(BaseModel): 
    """Top level collection of zones."""
    zones: list[Zone]
    
    def get_zone_by_name(self, name: str) -> Union[Zone, None]:
        for zone in self.zones:
            if zone.zone_name == name:
                return zone
        return None