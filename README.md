# Text-Based Mailmerge

A lightweight, text-based implementation of the company's Mailmerge (VIA) API pattern. This project focuses on processing text-like templates (plain text, Markdown, XML) by reading the entire document as a raw string, running the mailmerge replacement engine, and exporting the result in the requested format.

## Table of Contents
- Summary
- Features
- Supported formats
- Quick start
- Example usage
- Project structure
- File summaries
- Limitations & notes

## Summary
This repository provides a reusable, regex-driven mailmerge engine intended for simple text-based templates. It validates and casts input data to Pydantic models, applies zone-based replacements, and writes the resulting file in the chosen format.

## Features
- Simple, text-first mailmerge implementation
- Reusable regex replacement engine
- Pydantic models for input validation and casting
- Utilities for safe file handling and input validation
- Supports text, Markdown, and XML templates

## Supported formats
- .txt (plain text)
- .md (Markdown)
- .xml (text-based XML)
Note: Binary formats or templates requiring non-text parsing are outside the current scope.

## Quick start
1. Clone the repository:
    git clone /path/to/repo
2. (Optional) Create a virtual environment and install dependencies (example):
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
3. Use the provided classes and utilities to perform a mailmerge.
    Example use may be found in main.py

## Example usage (concept)
This example shows typical imports and flow; adapt to your CLI or application entrypoint.

```python
from utils.zones_processor import ZonesProcessor
from src.utils.get_input import extract_input_json
from src.mailmerge.text_mailmerge import TextMailMerge

mailmerge = TextMailMerge()
template_path ="/home/user/example/template/path/template.txt" #The Template to merge into
input_path = "/home/user/example/input/path/input.json" #The inputs to merge into the template

json_data = extract_input_json(input) #Helper method to safely extract JSON data (with validation)


mailmerge.load_input_data(json_data) #Loads the JSON Data 
mailmerge.load_template_from_path(template) #Loads the template (from path)

mailmerge.perform_merge() # Core merge entry point

mailmerge.save_output_from_buffer("output.md") #Save the output from the mailmerge class
```

## Project structure
The current project tree (excluding metadata):

| Path | Description |
|------|--------------|
| **src/mailmerge/base_mailmerge.py** | Abstract base class for Mailmerge implementations |
| **src/mailmerge/text_mailmerge.py** | Text (.txt) based implementation of Mailmerge |
| **src/models/schema.py** | Pydantic model declarations for input JSON |
| **src/utils/file_handler.py** | Loading, reading, and writing files (uses `.read()`) |
| **src/utils/get_input.py** | Safe opening and path/file validation helpers |
| **src/utils/zones_processor.py** | Validation and casting into the Zones Pydantic model |
| **src/utils/str_replace_engine.py** | Core reusable regex engine for mailmerge |


## File summaries
- src/mailmerge/base_mailmerge.py  
  Defines the abstract API (methods and behavior) the concrete mailmerge classes implement.

- src/mailmerge/text_mailmerge.py  
  Concrete implementation that takes a raw text block and applies the replacement engine.

- src/models/schema.py  
  Pydantic models and schemas used to validate and type the incoming JSON describing zones/values.

- src/utils/file_handler.py  
  Helpers to open, read and write files. Note: uses .read() and may be sensitive to non-standard encodings.

- src/utils/get_input.py  
  Functions to validate file paths and safely open files for processing.

- src/utils/zones_processor.py  
  Pre-processes and validates the JSON input then casts it into Pydantic models.

- src/utils/str_replace_engine.py  
  Central regex-driven engine that performs replacements in a safe reusable way.

## Limitations & notes
- The implementation is text-first: binary files, images, or format-specific parsing are out of scope.
- file_handler.py reads files using .read() — be explicit about encodings to avoid issues with non-UTF-8 sources.
- Raw-string manipulation is the primary, tested, and recommended path in this project; other approaches will need additional tests.
