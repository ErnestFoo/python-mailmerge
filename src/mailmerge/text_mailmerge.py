import string
from src.mailmerge.base_mailmerge import BaseMailMerge
from src.models.schema import ZoneCollection
from src.utils.file_handler import FileHandler, FileHandlerMode
from utils.zones_processor import ZonesProcessor
from src.utils.get_input import extract_input_json
from src.utils.str_replace_engine import StrReplaceEngine

import re


TAG = "ls_"  # Zone tag prefix for Zone names
GLOBAL_TAG = "global"  # Prefix for global zones
CHUNK_SIZE = 1024  # Size of chunks to read/write files
INTEMEDIATE_FILE_TAG = "_temp_"


class TextMailMerge(BaseMailMerge):
    # Currently, all operations are done in memory. Future versions may stream operations for large files.
    # Shouldn't be an issue for text files unless they are extremely large.

    def __init__(
        self,
        zones_processor: ZonesProcessor = None,
        input_file_handler: FileHandler = None,
        output_file_handler: FileHandler = None,
    ):

        self.input_processor = zones_processor or ZonesProcessor()
        self.input_file_handler = input_file_handler or FileHandler()
        self.output_file_handler = output_file_handler or FileHandler(
            mode=FileHandlerMode.WRITE
        )
        self._temp_buffer: str = ""  # Intermediate buffer for processing
        self.str_replace_engine = StrReplaceEngine()

    @property
    def zone_collection(self) -> ZoneCollection:
        """Returns the processed ZoneCollection from the InputProcessor."""
        return self.input_processor.zone_collection

    def load_template_from_path(self, template_path: str):
        """Function to load the template file for mail merge operations."""
        self.input_file_handler.load_file(template_path)

        # Loads the whole file into memory - not optimal for large files
        self._temp_buffer = self.input_file_handler.read_file()
        return True

    def load_input_data(self, input_json: dict):
        """Function to load and process input JSON data into ZoneCollection."""
        return self.input_processor.process_input_into_collection(input_json)
        return True

    def save_output_from_buffer(self, output_path: str):
        """Function to save the output of the mail merge operations"""
        self.output_file_handler.save_file(output_path, self._temp_buffer)

    def validate_inputs(self):
        """Function to validate the loaded template and input data for mail merge operations."""
        if not self.input_processor.zone_collection:
            raise ValueError("Input data has not been processed into ZoneCollection.")
        if not self.input_file_handler.file_loaded:
            raise ValueError("Template file has not been loaded.")
        return True

    def delete_zones(self):
        """Function to delete zones in the template marked with specific tags."""
        # Uses Grep to pattern match the content within zone tags and remove them
        zones_to_delete = [
            zone for zone in self.zone_collection.zones if zone.zone_delete
        ]
        for zone in zones_to_delete:
            self.str_replace_engine.with_default_zone_pattern(
                tag_prefix=TAG, tag=zone.zone_name
            )
            self._temp_buffer = self.str_replace_engine.remove_zone(self._temp_buffer)

    def replace_global(self):
        """Function to replace global zones in the template."""
        global_zone = self.zone_collection.get_zone_by_name(GLOBAL_TAG)
        self.__base_replace(zone=global_zone)

    def replace_zones(self):
        """Function to replace non-global zones in the template."""
        zones_to_replace = [
            zone for zone in self.zone_collection.zones if zone.zone_name != GLOBAL_TAG
        ]
        for zone in zones_to_replace:
            self.__base_replace(zone=zone)

    def __base_replace(self, zone: dict):
        """Function to replace zones in the template."""
        # First perform key replacements
        self.__key_replace(zone)

        # Check if array keys exist to replace rows
        if self.__is_zone_array(zone):
            print(f"Processing list replacement for zone: {zone.zone_name}")
            # self.__list_replace(zone)

        # # Finally, remove the start and end tags from the template
        # self._temp_buffer = self.__remove_start_end_tags(
        #     self._temp_buffer, zone.zone_name
        # )

    def __is_zone_array(self, zone: dict) -> bool:
        """Check if the zone is an array type."""
        return True if zone.zone_arrays and len(zone.zone_arrays) > 0 else False

    def __key_replace(self, zone: dict):
        """Base function for replacing zones in the template."""
        # For global zones, replace all [[key]] with value in the whole content
        if zone.zone_name.upper() == GLOBAL_TAG.upper():
            self.replace_global_keys(zone)

        # For non-global zones, replace within the zone tags only
        else:
            # Function to prepare replacement within the zone tags
            def replace_in_zone(match: re.Match) -> str:
                zone_body = match.group(2)
                for key, value in zone.zone_keys.items():
                    placeholder = f"[[{key}]]"
                    zone_body = zone_body.replace(placeholder, str(value))
                return (
                    f"{match.group(1)}{zone_body}{match.group(3)}"  # Includes the tags
                )

            # Get zoned regions of text to replace
            self._temp_buffer = self.str_replace_engine.with_default_zone_pattern(
                tag_prefix=TAG, tag=zone.zone_name
            ).replace(replacement=replace_in_zone, text_to_replace=self._temp_buffer)
        return True

    def replace_global_keys(self, zone):
        for key, value in zone.zone_keys.items():
            # If value is not string, convert to string
            self._temp_buffer = (
                self.str_replace_engine.with_default_global_pattern().replace_key(
                    key=key,
                    text_to_replace=self._temp_buffer,
                    replacement=str(value),
                )
            )

    def __list_replace(self, zone: dict):
        """Replace list zones in the template."""
        zone_regions = self.__get_zone_regions(zone)
        print(f"Found {len(zone_regions)} regions for zone: {zone.zone_name}")

        for zone_region in zone_regions:
            row_regions = self.__get_row_regions(zone, zone_region)
            print(f"Found {len(row_regions)} row regions for zone: {zone.zone_name}")

            for row_region in row_regions:
                merged_items = self.__build_merged_region(zone, row_region)
                print(f"Merged items for zone {zone.zone_name}:\n{merged_items}")

                self.__replace_row_region(zone, row_region, merged_items)

    def __get_zone_regions(self, zone: dict) -> list[str]:
        """Function to get all zone regions within the content."""
        start_tag, end_tag = self.__get_start_end_tags(zone.zone_name)
        return self.__get_string_region(self._temp_buffer, start_tag, end_tag)

    def __get_start_end_tags(self, zone_name: str) -> tuple[str, str]:
        """Function to get start and end tags for a given zone name."""
        start_tag = f"<{TAG}{zone_name}>"
        end_tag = f"</{TAG}{zone_name}>"
        return start_tag, end_tag

    def __remove_start_end_tags(self, content: str, zone_name: str) -> str:
        """Function to remove start and end tags for a given zone name from content."""
        start_tag, end_tag = self.__get_start_end_tags(zone_name)
        content = content.replace(start_tag, "").replace(end_tag, "")
        return content

    def __get_row_regions(self, zone: dict, zone_region: str) -> list[str]:
        """Function to get all row regions within a list zone."""
        row_regions = []
        for region in self.__get_string_region(zone_region, start_tag, end_tag):
            row_start_tag = f"<{TAG}_row>"
            row_end_tag = f"</{TAG}_row>"
            row_regions.extend(
                self.__get_string_region(region, row_start_tag, row_end_tag)
            )
        return row_regions

    def __build_merged_region(self, zone: dict, region: str) -> str:
        """Function to build merged regions from zone arrays and row template."""
        merged_items = ""
        for i, array_item in enumerate(zone.zone_arrays):
            item_content = self.__replace_array_item_keys(region, array_item)
            if i < len(zone.zone_arrays) - 1:
                item_content += "\n"
            merged_items += item_content
        return merged_items

    def __replace_array_item_keys(self, region: str, array_item: dict) -> str:
        """Function to replace keys in a region for a specific array item."""
        item_content = region
        for key, value in array_item.root.items():
            item_content = (
                self.str_replace_engine.with_default_key_pattern().replace_key(
                    key=key,
                    text_to_replace=item_content,
                    replacement=str(value),
                )
            )
        return item_content

    def __replace_row_region(self, zone: dict, row_content: str, merged_items: str):
        """Function to replace the row region including tags with merged items."""
        print(f"Row content to replace:\n{row_content}")
        print(f"Merged items to replace with:\n{merged_items}")
        return self.str_replace_engine.with_default_row_pattern(
            original_row_content=row_content
        ).replace(text_to_replace=row_content, replacement=merged_items)

    # def __list_replace(self, zone: dict):
    #     """Function to replace list zones in the template.
    #     Build list of items from zone arrays and replace in the template.
    #     Find all regions of the zones in the template that match the zone name.
    #     Get the string between the zone tags, and for each item in the zone array,
    #     """
    #     template_regions = self.__get_zone_regions(zone)
    #     print(f"Found {len(template_regions)} regions for zone: {zone.zone_name}")

    #     for region in template_regions:
    #         merged_items = ""
    #         for array_item in zone.zone_arrays:
    #             item_content = region
    #             for key, value in array_item.root.items():
    #                 item_content = (
    #                     self.str_replace_engine.with_default_key_pattern().replace_key(
    #                         key=key,
    #                         text_to_replace=item_content,
    #                         replacement=str(value),
    #                     )
    #                 )
    #             # If not last item, add a newline for separation
    #             if array_item != zone.zone_arrays[-1]:
    #                 item_content += "\n"
    #             merged_items += item_content

    #         # Replace the whole region including tags with merged items
    #         self._temp_buffer = self.str_replace_engine.with_default_zone_pattern(
    #             tag_prefix=TAG, tag=zone.zone_name
    #         ).replace(text_to_replace=self._temp_buffer, replacement=merged_items)

    def __get_row_regions(self, zone: dict, content: str) -> list[str]:
        """Function to get all row regions within a list zone."""
        row_start_tag = f"<{TAG}row>"
        row_end_tag = f"</{TAG}row>"
        row_regions = []
        for region in self.__get_string_region(content, row_start_tag, row_end_tag):
            row_regions.append(region)
        return row_regions

    def __get_string_region(
        self, content: str, start_tag: str, end_tag: str
    ) -> list[str]:
        """Function to get all string regions between start and end tags."""
        pattern = rf"{re.escape(start_tag)}(.*?){re.escape(end_tag)}"
        matches = re.findall(pattern, content, flags=re.DOTALL)
        # regions = [match[1] for match in matches]
        return matches


if __name__ == "__main__":
    # mailmerge = TextMailMerge().run_from_CLI()

    mailmerge = TextMailMerge()
    print(f"Initialized TextMailMerge: {mailmerge}")
    template = (
        "/home/ernestfoo/Documents/python-mailmerge/Sample_Input/sample_contract.txt"
    )

    input = "/home/ernestfoo/Documents/python-mailmerge/Sample_Input/zones.json"
    json_data = extract_input_json(input)

    mailmerge.load_input_data(json_data)
    mailmerge.load_template_from_path(template)

    mailmerge.perform_merge()
    mailmerge.save_output_from_buffer("Banana.txt")

# # Methods for chunk-based zone deletion processing
#
# def delete_zones_streaming(self):
#  """Function to delete zones in the template marked with specific tags."""
#     # Build a list of zones to delete based on the tag
#     print(self.zone_collection)
#     zones_to_delete = [zone for zone in self.zone_collection.zones if zone.zone_delete]
#     print(f"Total zones to delete: {len(zones_to_delete)}")
#     print(f"Zones to delete: {[zone.zone_name for zone in zones_to_delete]}")
#     # Logic to delete zones from the template

#     # Build list of zone names tags to delete
#     start_zone_tags = [f"<{TAG}{zone.zone_name}>" for zone in zones_to_delete]
#     end_zone_tags = [f"</{TAG}{zone.zone_name}>" for zone in zones_to_delete]

#     # Map the tags to zone names for easy reference
#     zone_tag_map = self.__build_zone_tag_map__(zones_to_delete)

#     zone_stack = []  # Stack to keep track of nested zones

#     # Read the template content
#     with self.input_file_handler as reader:
#         for chunk in reader.stream_chunks(chunk_size=CHUNK_SIZE):
#             lines = chunk.splitlines(keepends=True)
#             for line in lines:
#                 first_popped_tag_pos = self.__process_start_tags_in_line__(line, start_zone_tags, zone_tag_map, zone_stack)
#                 last_popped_tag_pos = self.__process_end_tags_in_line__(line, end_zone_tags, zone_tag_map, zone_stack)


#                 if not self.inside_deletion_zone(zone_stack) and last_popped_tag_pos >= 0:
#                     # If outside of the deletion zones and all tags was just closed, write the remaining part of the line

#                     # Write the line from the position after the last end tag to the end of the line
#                         self._temp_buffer += line[last_popped_tag_pos:]
#
# def __process_start_tags_in_line__(self, line: str, start_zone_tags: list, zone_tag_map:dict, zone_stack: list) -> bool:
#     # Finds tags in line and pushes tags into the zone stack, returns the position of the first found tag
#     found_tags = self.__get_tag_in_line__(line, start_zone_tags)
#     print(f"Found start tags in line: {found_tags}")
#     for tag in found_tags:
#         if zone_name := self.__map_zone_tag_to_name__(zone_tag_map, tag):
#             print(f"Mapping tag {tag} to zone name {zone_name}")
#             self.__push_zone_stack__(zone_stack, zone_name)
#             print(f"Entering deletion zone: {zone_name}")
#             print(f"Current zone stack: {zone_stack}")

#     return self.__get_tag_position_in_line__(line, found_tags[0]) if found_tags else -1

# def __process_end_tags_in_line__(self, line: str, end_zone_tags: list, zone_tag_map:dict, zone_stack: list) -> bool:
#     # Finds tags in line and pops tags from the zone stack
#     # returns the last found tag position + the position of the tag in line
#     found_tags = self.__get_tag_in_line__(line, end_zone_tags)

#     print(f"Found end tags in line: {found_tags}")
#     for tag in found_tags:
#         if zone_name := self.__map_zone_tag_to_name__(zone_tag_map, tag):
#             print(f"Mapping tag {tag} to zone name {zone_name}")
#             if self.__top_of_stack__(zone_stack) == tag:
#                 last_popped_tag = self.__pop_zone_stack__(zone_stack)

#     return (self.__get_tag_in_line__(line, last_popped_tag) + len(last_popped_tag)) if found_tags else -1

# def inside_deletion_zone(self, zone_stack: list) -> bool:
#     return len(zone_stack) != 0


# def __get_tag_in_line__(self, line: str, tag_list: list) -> list[str]:
#     found_tags = []  # To obtain all tags in line, in order
#     for tag in tag_list:
#         if tag in line:
#             found_tags.append(tag)
#     return found_tags

# def __get_tag_position_in_line__(self, line: str, tag: str) -> int:
#     # Returns the position of the tag in the line
#     return line.find(tag)

# def __build_zone_tag_map__(self, zones_to_delete: list) -> dict:
#     zone_tag_map = {
#         zone.zone_name: (f"<{TAG}{zone.zone_name}>", f"</{TAG}{zone.zone_name}>")
#         for zone in zones_to_delete
#     }
#     return zone_tag_map

# def __map_zone_tag_to_name__(self, zone_tag_map: dict, tag: str) -> str:
#     for zone_name, (start_tag, end_tag) in zone_tag_map.items():
#         if tag == start_tag or tag == end_tag:
#             return zone_name
#     return None #  Tag not found

# def __top_of_stack__(self, zone_stack: list) -> str:
#     if zone_stack:
#         return zone_stack[-1]
#     return None

# def __push_zone_stack__(self, zone_stack: list, zone_name: str):
#     zone_stack.append(zone_name)

# def __pop_zone_stack__(self, zone_stack: list) -> str:
#     if zone_stack:
#         return zone_stack.pop()
#     return None
