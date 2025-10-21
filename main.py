from src.utils.input_processor import ZonesProcessor
from src.utils.get_input import extract_input_json

def main():
    file_path = '/home/ernestfoo/Documents/python-mailmerge/Sample_Input/zones.json'
    json_data = extract_input_json(file_path)
    processor = ZonesProcessor(input_json=json_data)
    zone_collection = processor.process_input_into_collection()

    print(type(zone_collection).__name__)
    print(zone_collection)


if __name__ == "__main__":
    main()
