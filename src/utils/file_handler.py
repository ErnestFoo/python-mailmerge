""" File Handler Module
Handles file reading and writing operations. (streaming wise to avoid loading entire files into memory)
- Takes in a template file and opens a file bytestream for reading.
- Writes output to a specified file via bytestream too.
"""

from enum import Enum 
from io import TextIOWrapper
import os
from src.utils.get_input import get_file_extension, file_exists

class FileHandlerMode(Enum):
    READ = 'r'
    WRITE = 'w'
    APPEND = 'a'

class validInputFileTypes(Enum):
    Text = '.txt'
    Markdown = '.md'
    XML = '.xml'

class FileHandler():
    
    def __init__(self, 
                 mode = FileHandlerMode.READ,
                 file_path: str= None):
        self.mode: FileHandlerMode = mode # Default mode is read
        self.file_path: str =  None # Path to the file
        self.file_loaded = False
        self.__file_IO: TextIOWrapper = None # File IO stream object
        self.__file_type: validInputFileTypes = None # Metadata on the extension/type of file

        if mode == FileHandlerMode.READ and file_path: self.load_file(file_path)

        if (mode == FileHandlerMode.WRITE or mode == FileHandlerMode.APPEND) and file_path:
               self.prepare_output_filepath(file_path)

    def __enter__(self):
        """ For context manager support. """
        if self.__file_IO is None:
            raise ValueError("File stream is not open.")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """ For context manager support. """
        self.close_file()

    def load_file(self, file_path:str):
        """ Validate and load the provided file path.
            - Raises FileNotFoundError if the path does not exist.
            - Infers and validates the extension using get_file_extension and
            - Opens the file stream via open_file_stream() and returns True on success.
        """
        self._read_mode_validation()
        if not file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.file_path = file_path
        extension = get_file_extension(file_path)
        
        # Map the extension to validInputFileTypes Enum
        try:
            self.__file_type = validInputFileTypes(extension)
        except ValueError:
            raise ValueError(f"Unsupported file type: {extension}"
                             f" Supported types are: {[e.value for e in validInputFileTypes]}")
        
        # Open the file stream 
        self.__file_IO = self.open_file_stream()
        self.file_loaded = True
        return True
    
    def prepare_output_filepath(self, file_path:str):
        """ Prepares the output file path for writing operations.
            - Infers and validates the extension using get_file_extension.
            - Sets the file_path attribute.
        """
        self._write_mode_validation()
        if (valid_filepath := self.validate_output_file(file_path)):
            self.open_file_stream()
        return True
    
    def _write_mode_validation(self):
        if self.mode is FileHandlerMode.WRITE or self.mode is FileHandlerMode.APPEND: return True
        else: raise ValueError(f"FileHandler is not in write/append mode, current mode: {self.mode}")   

    def _read_mode_validation(self):
        if self.mode is FileHandlerMode.READ: return True
        else: raise ValueError(f"FileHandler is not in read mode, current mode: {self.mode}")
    
    def validate_output_file(self, file_path:str):
        """ Validate the output file path and sets the file_path and file_type attribute.
            - Infers and validates the extension using get_file_extension.
            - Verifies that the directory exists and is writable.
            returns file_path if valid.
        """
        self._write_mode_validation()
        # Map the extension to validInputFileTypes Enum
        self.__map_extension_to_file_type__(file_path)
        # Check if the directory is writable
        self.__write_dir_check__(file_path)

        return file_path

    def __map_extension_to_file_type__(self, file_path: str):
        """ Map the file extension to the validInputFileTypes Enum. """
        extension = get_file_extension(file_path)
        try:
            self.__file_type = validInputFileTypes(extension)
        except ValueError:
            raise ValueError(f"Unsupported file type: {extension}"
                             f" Supported types are: {[e.value for e in validInputFileTypes]}")
        self.file_path = file_path
        return True
    
    def __write_dir_check__(self, directory: str) -> bool:
        extension = get_file_extension(directory)
        # Check if the directory is writable
        directory = os.path.dirname(directory) or '.'

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        if not os.access(directory, os.W_OK):
            raise ValueError(f"Directory is not writable: {directory}")
        
        return True
    
    def open_file_stream(self):
        if self.mode == FileHandlerMode.READ:
            self.__file_IO = open(self.file_path, 'r')
        elif self.mode == FileHandlerMode.WRITE:
            self.__file_IO = open(self.file_path, 'w')
        elif self.mode == FileHandlerMode.APPEND:
            self.__file_IO = open(self.file_path, 'a')
        return self.__file_IO
    
    def close_file(self):
        if self.__file_IO:
            self.__file_IO.close()
            self.__file_IO = None
            self.file_path = None
            self.__file_type = None
    
    def save_file(self, output_path: str, data: str):
        """ Save data to the specified output file path. """
        self._write_mode_validation()
        if not data:
            raise ValueError("No data provided to write to file.")
        
        # Validate and prepare the output file path
        self.prepare_output_filepath(output_path)
        
        # Write data to the file
        self.__file_IO.write(data)
        self.__file_IO.flush()  # flush ensures that data is written to disk
    
    def write_chunk(self, data: str):
        """Write a chunk of data to the open file stream without loading everything into memory."""
        self._write_mode_validation()
        if not self.__file_IO:
            raise ValueError("File stream is not open.")
        
        self.__file_IO.write(data)
        self.__file_IO.flush()  # flush ensures that data is written to disk

            
    def stream_chunks(self, chunk_size:int=1024):
        """ Generator to read file in chunks of specified size. """
        if not self.__file_IO:
            raise ValueError("File stream is not open.")
        
        while True:
            data = self.__file_IO.read(chunk_size)
            if not data:
                break
            yield data
            
    def read_file(self) -> str:
        """ Read the entire file content. """
        self._read_mode_validation()
        if not self.__file_IO:
            raise ValueError("File stream is not open.")
        
        self.__file_IO.seek(0)  # Ensure we're at the start of the file
        content = self.__file_IO.read()
        return content
            
    def __get_next_chunk__(self, chunk_size:int=1024):
        """ Helper method to get the next chunk from the file stream. """
        if not self.__file_IO:
            raise ValueError("File stream is not open.")
        
        data = self.__file_IO.read(chunk_size)
        return data

if __name__ == "__main__":
    file_path = '/home/ernestfoo/Documents/python-mailmerge/Sample_Input/sample.txt'
    file_handler = FileHandler(mode=FileHandlerMode.READ, file_path=file_path)

    # for _ in range (0, 5):
    #     file_stream = file_handler.__get_next_chunk__(chunk_size=50)
    #     print(f"Chunk: {file_stream}")
    

    # i = 0
    # with file_handler._file_IO as file_stream:
    #     for chunk in file_handler.stream_chunks(chunk_size=64):
    #         print(f"Chunk {i}: {chunk}")
    #         i += 1
        
    reader = FileHandler(mode=FileHandlerMode.READ, file_path=file_path)
    writer = FileHandler(mode=FileHandlerMode.WRITE, file_path="Sample_Input/output_path.md")

    i = 0   
    for chunk in reader.stream_chunks(chunk_size=1): 
        processed_chunk = chunk.upper()  # or apply any transformation
        writer.write_chunk(processed_chunk)
        print(f"Chunk {i}: {chunk}")
        i += 1
        
    
    
    print(f"Reader File type: {reader.__file_type}")
    print(f"Writer File type: {writer.__file_type}")
    #Read from the file stream
    reader.close_file()
    writer.close_file()
    