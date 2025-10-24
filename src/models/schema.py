from pydantic import BaseModel, Field, RootModel
"""
Module-level documentation for pydantic models representing DNS-like "zones".
This module defines light-weight pydantic models used to parse, validate,
and serialize a collection of "zones" and their associated structured data.
Models use explicit Field aliases to match an external data shape (for example,
when loading from YAML, JSON, or other sources). When serializing back to the
external representation, use the pydantic .model_dump(by_alias=True) / 
.dict(by_alias=True) options to obtain keys that match the original aliases.
Models
------
ZoneArray
    A thin wrapper around an arbitrary mapping used to represent a single
    entry from a zone's "array" of items.
    Attributes
    - root (dict[str, Any])
        The underlying mapping for the array item. This field uses the alias
        "zonearrayitem" to match the external input format. Defaults to an
        empty dict.
    Notes
    - Implemented as a RootModel to make the inner dictionary the "root"
      value for easier parsing/serialization when the external data treats the
      item as an inline mapping.
Zone
    Represents a single zone and its associated metadata and collections.
    Attributes
    - zone_name (str)
        The zone's identifier. Required. Uses the alias "zonename".
    - zone_keys (dict[str, Union[str, int]])
        Key/value metadata associated with the zone. Uses the alias
        "zonekeys". Defaults to an empty dict.
    - zone_arrays (list[ZoneArray])
        A list of ZoneArray entries representing structured list items within
        the zone. Uses the alias "zonearray". Defaults to an empty list.
    - zone_delete (bool)
        Flag indicating whether the zone is marked for deletion. Uses the
        alias "zonedelete". Defaults to False.
    Validation / Behavior
    - Aliasing: Input data that uses the external keys (zonename, zonekeys,
      zonearray, zonedelete) will be accepted and mapped to the model fields.
      When emitting serialized output meant for the same external format,
      call model_dump(by_alias=True) / .dict(by_alias=True).
    - Types: zone_keys accepts a mapping of string keys to either strings or
      integers. zone_arrays contains ZoneArray instances (each a mapping).
    - Defaults: If optional keys are missing from input, defaults (empty dict,
      empty list, False) are applied.
ZoneCollection
    Top-level container for a list of Zone objects.
    Attributes
    - zones (list[Zone])
        The collection of Zone instances.
    Methods
    - get_zone_by_name(name: str) -> Union[Zone, None]
        Return the Zone with the matching zone_name or None if not found.
        This performs a simple linear search over the zones in insertion
        order and returns the first match.
Examples
--------
Example input data (external representation):
{
    "zones": [
        {
            "zonename": "example.com",
            "zonekeys": { "owner": "admin", "ttl": 3600 },
            "zonearray": [
                { "zonearrayitem": { "key": "value" } }
            ],
            "zonedelete": False
        }
    ]
}
Usage notes
-----------
- To parse external data that uses the aliased keys, construct the container
  from the raw mapping (e.g. ZoneCollection.model_validate(data) in Pydantic v2
  or ZoneCollection.parse_obj(data) in older versions). When serializing back
  for export, use by_alias=True to preserve the original key names.
- The models are intentionally simple and focused on schema/validation. Business
  logic (e.g. merging, diffing, persistence) should live outside these models.
"""

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