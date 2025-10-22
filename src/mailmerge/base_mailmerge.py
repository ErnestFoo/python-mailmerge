# Import abstract base class
from abc import ABC, abstractmethod
from src.utils.file_handler import FileHandler, FileHandlerMode
from src.utils.input_processor import ZonesProcessor
from src.models.schema import ZoneCollection

class BaseMailMerge(ABC):
    @property
    def zone_collection(self) -> ZoneCollection:
        """ Returns the processed ZoneCollection from the InputProcessor. """
        pass
    
    @abstractmethod
    def load_template_from_path(self, template_path: str):
        """ Function to load the template file for mail merge operations. """
        pass
    
    @abstractmethod
    def load_input_data(self, input_json: dict):
        """ Function to load and process input JSON data into ZoneCollection. """
        pass
    
    @abstractmethod
    def save_output_from_buffer(self, output_path: str):
        """ Function to save the output of the mail merge operations. """
        pass

    @abstractmethod
    def validate_inputs(self):
        """ Function to validate the loaded template and input data for mail merge operations. """
        pass
        
    def perform_merge(self):
        """ Function to run all mail merge operations on the Zone Collection.
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