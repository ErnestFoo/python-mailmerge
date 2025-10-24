from src.models.schema import ZoneCollection
from src.utils.get_input import extract_input_json


class ZonesProcessor:
    """
    ZonesProcessor
    A helper class that converts raw JSON input into a ZoneCollection instance and caches
    the result for subsequent access.
    Parameters
    ----------
    input_json : dict, optional
        Raw JSON-like mapping containing the data used to construct a ZoneCollection.
        If omitted, the processor starts without input and must be provided one before
        processing.
    Attributes
    ----------
    input_json : dict or None
        The raw input JSON data currently held by the processor.
    zone_collection : ZoneCollection or None
        Cached ZoneCollection produced from input_json. Initially None until processing
        succeeds.
    Methods
    -------
    get_zone_collection() -> ZoneCollection
        Return the cached ZoneCollection if available. If not cached and input_json is set,
        process the input into a ZoneCollection, cache it, and return it.
    process_input_into_collection(json_data: dict = None) -> ZoneCollection
        Convert json_data (if provided) or the processor's input_json into a ZoneCollection
        by calling ZoneCollection(**input_json). Caches and returns the created
        ZoneCollection.
    Raises
    ------
    ValueError
        If no input JSON is available when attempting to process, or if constructing
        the ZoneCollection raises an exception. Any underlying exception raised during
        ZoneCollection construction is wrapped with a ValueError including the original
        error message.
    Notes
    -----
    - This class uses ZoneCollection model and accepts the JSON fields as keyword arguments.
    - The processor is intentionally simple and performs no validation beyond relying
      on ZoneCollection to validate/construct the domain object.
    """

    def __init__(self, input_json: dict = None):
        self.input_json: dict = input_json  # Raw input JSON data
        self.zone_collection: ZoneCollection = None  # Processed ZoneCollection object

    def get_zone_collection(self) -> ZoneCollection:
        """Retrieve the ZoneCollection instance.

        Returns:
            ZoneCollection: The processed ZoneCollection instance.
        """
        if self.zone_collection is None and self.input_json:
            self.process_input_into_collection()
        return self.zone_collection

    def process_input_into_collection(self, json_data: dict = None) -> ZoneCollection:
        """Process the input JSON data into a ZoneCollection instance.

        Args:
            json_data (dict, optional): New JSON data to process. Defaults to None.

        Raises:
            ValueError: If no input JSON is available when attempting to process.
            ValueError: If constructing the ZoneCollection raises an exception.

        Returns:
            ZoneCollection: The processed ZoneCollection instance.
        """
        if json_data:
            self.input_json = json_data

        if self.input_json:
            try:
                self.zone_collection = ZoneCollection(**self.input_json)

            except Exception as e:
                raise ValueError(f"Error Zone Collection schema for input errors: {e}")

            return self.zone_collection
        else:
            raise ValueError("Input JSON data is not set.")


if __name__ == "__main__":
    file_path = "/home/ernestfoo/Documents/python-mailmerge/Sample_Input/test.json"
    json_data = extract_input_json(file_path)

    processor = ZonesProcessor(input_json=json_data)
    zone_collection = processor.process_input_into_collection()

    print(type(zone_collection).__name__)
    print(zone_collection.model_dump())
