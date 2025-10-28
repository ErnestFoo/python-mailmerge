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

## Mailmerge concepts

---
### Template Format

MailMerge templates are plain text files that define **zones** — sections of text where replacements can occur.  
Each zone is enclosed in start and end delimiters using the following format:

```code
<ls_{zonename}>
...text content or placeholders...
</ls_{zonename}>
```

### Zone Declarations

A **zone** is declared using the `<ls_zonename>` and `</ls_zonename>` tags.

Example:

```
<ls_body>
This is some text inside the "body" zone.
</ls_body>
```

Everything inside these tags is considered part of that zone and can include **placeholders (keys)** that will be replaced during processing.

---

### 🔹 Placeholders (Keys)
Keys are placeholders enclosed in double square brackets:  
```
[[KeyName]]
```

When a key appears **inside a zone**, its value will only be replaced if it is declared under that zone’s `zonekeys` in the Zone JSON file.

Example:
```
<ls_body>
Dear [[RecipientName]],

Your order #[[OrderID]] has been shipped.
</ls_body>

```

In this case, both `RecipientName` and `OrderID` must be listed inside the `zonekeys` for the `"body"` zone.

---

### Global Keys

Keys that appear **throughout the document** (for example, in headers, greetings, or signatures) must be defined under a special `"global"` section in the Zone JSON file. (See Zone JSON format section). If a global key shadows a zoned key, the key within the zone will be replaced by its global value.


Example:

```
Company: [[CompanyName]]

<ls_message>
Hello [[Name]], your report is ready.
</ls_message>

Sincerely,
[[SenderName]]
````


---


### Marking Zones for Deletion

If a zone is explicitly **marked for deletion** in the input JSON, the entire block of text enclosed by that zone’s tags will be **removed** from the output.

Example:

**Template:**

```
Thank you for your interest.

<ls_optional_note>
Please complete your profile to receive updates.
</ls_optional_note>

Best regards,
[[Sender]]
```

**Zone JSON:**

```json
{
  "zones": [
    {
      "zonename": "optional_note",
      ...
      "zonedelete": true
    }
  ]
}
```

**Resulting Output:**

```
Thank you for your interest.

Best regards,
Customer Service
```
---
### Lists / Zone Arrays

A Zone Array represents a repeating list of data that belongs to a specific zone.
When a zone includes a "zonearray" in the Zone JSON, the entire block of text inside that zone will be duplicated once per entry in the array — with all placeholder keys replaced by each item’s values.

This allows you to automatically generate repeating sections (such as lists of items, skills, experiences, etc.) within a single zone.
This only applies to sections within the zone, delimited by the <ls_row> tag.

Example:
```
Template:

<ls_skills>
  <ls_row>
  • [[SkillName]] — [[SkillLevel]]
  </ls_row>
</ls_skills>
```

Zone JSON:
```
{
  "zones": [
    {
      "zonename": "skills",
      "zonearray": [
        { "SkillName": "Python", "SkillLevel": "Advanced" },
        { "SkillName": "C#", "SkillLevel": "Intermediate" },
        { "SkillName": "React", "SkillLevel": "Advanced" }
      ]
    }
  ]
}
```

Resulting Output:
```
• Python — Advanced
• C# — Intermediate
• React — Advanced
```

If both zonearray and zonekeys are present, the system will prioritize zonearray for repetition but still allow single keys defined in zonekeys to appear within the same zone (for example, as section titles or summaries).

---

### Summary of Template Rules

| Element             | Syntax                     | Description                                              |
| ------------------- | -------------------------- | -------------------------------------------------------- |
| **Zone Start Tag**  | `<ls_zonename>`            | Marks the beginning of a zone                            |
| **Zone End Tag**    | `</ls_zonename>`           | Marks the end of a zone                                  |
| **Placeholder Key** | `[[Key]]`                  | Replaced with its corresponding value in the zone’s data |
| **Global Key**      | `[[Key]]` (outside zones)  | Replaced if defined under `globals` in JSON              |
| **Deleted Zone**    | Zone with `"delete": true` | Entire zone is removed from final output                 |

---

This format ensures templates are **modular, readable, and easily customizable**, allowing you to define reusable mail templates with clear data binding.

## Zones JSON format 

The Zones JSON file tells MailMerge **what zones exist in the template**, **what data to fill in**, and **whether to keep or remove** each section.

Each zone in the JSON matches a `<ls_zonename>...</ls_zonename>` block in your template.

---

### 🧱 Example

```json
{
  "zones": [
    {
      "zonename": "global",
      "zonekeys": {
        "section": "terms",
        "priority": 2
      },
      "zonearray": [],
      "zonedelete": false
    },
    {
      "zonename": "signatures",
      "zonekeys": {
        "section": "footer",
        "requires_date": true
      },
      "zonearray": [],
      "zonedelete": true
    }
  ]
}

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
