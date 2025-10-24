# Import abstract base class
from abc import ABC, abstractmethod
import argparse
import json
from src.utils.file_handler import FileHandler, FileHandlerMode
from src.models.schema import ZoneCollection
from src.utils.get_input import extract_input_json
from utils.zones_processor import ZonesProcessor


class BaseMailMerge(ABC):
    """Abstract base class for mail merge operations.

    properties
    ----------
    zone_collection : ZoneCollection
        The processed ZoneCollection from the InputProcessor.

    Methods
    -------
    load_template_from_path(template_path: str)
        Function to load the template file for mail merge operations.

    load_input_data(input_json: dict)
        Function to load and process input JSON data into ZoneCollection.

    save_output_from_buffer(output_path: str)
        Function to save the output of the mail merge operations.

    validate_inputs()
        Function to validate the loaded template and input data for mail merge operations.

    perform_merge()
        Core functionality of the mail merge process.
        Function to run all mail merge operations on the Zone Collection.
        This includes deleting zones, replacing global zones, and replacing non-global zones.

    delete_zones(template_path: str)
        Function to delete zones in the template marked with specific tags.

    replace_global()
        Function to replace global zones in the template.

    replace_zones()
        Function to replace non-global zones in the template.

    -------
    """

    @property
    def zone_collection(self) -> ZoneCollection:
        """Returns the processed ZoneCollection from the InputProcessor."""
        pass

    @abstractmethod
    def load_template_from_path(self, template_path: str):
        """Function to load the template file for mail merge operations."""
        pass

    @abstractmethod
    def load_input_data(self, input_json: dict):
        """Function to load and process input JSON data into ZoneCollection."""
        return False

    @abstractmethod
    def save_output_from_buffer(self, output_path: str):
        """Function to save the output of the mail merge operations."""
        pass

    @abstractmethod
    def validate_inputs(self):
        """Function to validate the loaded template and input data for mail merge operations."""
        pass

    def run_from_CLI(self):
        """The CLI implementation to run the mail merge process end to end."""
        parser = argparse.ArgumentParser(description="Mail Merge Processor")
        parser.add_argument(
            "--template", type=str, required=True, help="Path to the template file."
        )
        parser.add_argument(
            "--input", type=str, required=False, help="Path to the input JSON file."
        )
        parser.add_argument(
            "--input-data",
            type=str,
            required=False,
            help="Raw input JSON data as a string.",
        )
        parser.add_argument(
            "--output", type=str, required=True, help="Path to save the output file."
        )

        args = parser.parse_args()

        if not (bool(args.input) ^ bool(args.input_data)):
            parser.error(
                "Either --input or --input-data must be provided. Both cannot be used together."
            )
        data = {}
        if args.input_data:
            data = json.loads(args.input_data)

        elif args.input:
            data = extract_input_json(args.input)

        self.load_template_from_path(args.template)
        self.load_input_data(data)
        self.perform_merge()
        self.save_output_from_buffer(args.output)

        print(
            f"Mail merge operations completed successfully. Output saved to {args.output}"
        )

    def perform_merge(self):
        """Function to run all mail merge operations on the Zone Collection.
        This includes deleting zones, replacing global zones, and replacing non-global zones.
        - First deletes zones tagged with zonedelete=true
        - Then replace global zones
        - Finally replace non-global zones
        """
        self.validate_inputs()
        self.delete_zones()
        self.replace_global()
        self.replace_zones()

    @abstractmethod
    def delete_zones(self, template_path: str):
        """Function to delete zones in the template marked with specific tags."""
        pass

    @abstractmethod
    def replace_global(self):
        """Function to replace global zones in the template."""
        pass

    @abstractmethod
    def replace_zones(self):
        """Function to replace non-global zones in the template."""
        pass
