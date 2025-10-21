from src.models.schema import ZoneCollection 
from src.utils.get_input import extract_input_json

class ZonesProcessor():
    def __init__(
        self, 
        input_json: dict= None):
        self.input_json: dict = input_json # Raw input JSON data
        self.zone_collection: ZoneCollection = None # Processed ZoneCollection object

    
    def get_zone_collection(self) -> ZoneCollection:
        if self.zone_collection is None and self.input_json:
            self.process_input_into_collection()
        return self.zone_collection
    
    def process_input_into_collection(self, json_data: dict= None) -> ZoneCollection:
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
    file_path = '/home/ernestfoo/Documents/python-mailmerge/Sample_Input/test.json'
    json_data = extract_input_json(file_path)
    
    processor = ZonesProcessor(input_json=json_data)
    zone_collection = processor.process_input_into_collection()
    
    print(type(zone_collection).__name__)
    print(zone_collection.model_dump())