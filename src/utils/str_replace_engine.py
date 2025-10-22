import re
from typing import Self

class str_replace_engine:
    """ Purpose: 
    A reusable string replacement engine that allows for flexible pattern matching and replacement.
    It supports setting custom start and end tags, stripping surrounding newlines, and performing replacements.
    Steps to use: 
        1. Initialize the engine with optional body pattern, replacement text, and text to replace.
        2. Configure the pattern using methods to set tags, body, and newline stripping.
        3. Call the replace_key() method to perform the replacement. """
    
    def __init__(self, 
                 body: str = "(.*?)", #By default match any content
                 ):

        # Initialize with default values
        self.preceeding_seq = "" # The sequence before the matched pattern  
        self.tag_prefix = "" # The prefix for the start and end tags
        self.start_tag = "" # The starting tag of the pattern
        self.body = body # The main body of the pattern to match
        self.end_tag = "" # The ending tag of the pattern
        self.proceeding_seq = "" # The sequence after the matched pattern
        

    def with_default_global_pattern(self) -> Self:
        """ Builds the default global pattern with any start/end tags or newline stripping """
        self.strip_surrounding_newlines()
        self.set_start_end_tags(start_tag="global", end_tag="global")
        self.set_tag_prefix("ls_")
        return self

    def with_default_zone_pattern(self, tag_prefix: str, tag: str) -> Self:
        """ Builds the default pattern with any start/end tags or newline stripping """
        self.strip_surrounding_newlines()
        self.set_start_end_tags(start_tag=tag, end_tag=tag)
        self.set_tag_prefix(tag_prefix)
        self.set_body("(.*?)")
        return self

    def get_pattern(self) -> str:
        """ Returns the final regex pattern """
        pattern = self.preceeding_seq

        if self.tag_prefix and self.start_tag:
            pattern += f"(<{self.tag_prefix}{self.start_tag}>)"

        pattern += self.body

        if self.tag_prefix and self.end_tag:
            pattern += f"(<\/{self.tag_prefix}{self.end_tag}>)"

        pattern += self.proceeding_seq
        
        return pattern

    def replace(self, text_to_replace: str, replacement: str) -> str:
        string = re.sub(
            self.get_pattern(),
            replacement,
            text_to_replace,
            flags=re.DOTALL
        )
        return string

    def replace_key(self, replacement: str) -> str:
        string = re.sub(
            self.get_pattern(),
            replacement,
            self.text_to_replace,
            flags=re.DOTALL
        )
    
    def set_text(self, text: str) -> Self:
        """ Sets the text to perform replacements on """
        self.text_to_replace = text
        return self

    def set_key(self, key: str) -> Self:
        """ Sets the key for the pattern body """
        self.body = r"\[\[" + re.escape(key) + r"\]\]"
        return self
    
    def set_body(self, pattern: str) -> Self:
        """ Sets the body of the pattern """
        self.body = pattern
        return self

    def set_tag_prefix(self, tag_prefix: str) -> Self:
        """ Sets the tag prefix for the start and end tags """
        self.tag_prefix = re.escape(tag_prefix)
        return self

    def set_start_end_tags(self, start_tag: str= None, end_tag: str = None) -> Self:
        """ Sets the start and end tags for the pattern """
        if start_tag is not None:
            self.start_tag = re.escape(start_tag)
        if end_tag is not None:
            self.end_tag = re.escape(end_tag)
        return self

    def strip_pre_newlines(self) -> Self:
        """ Strips newlines before the matched pattern """
        self.preceeding_seq = r"(?:\r?\n)?" + self.preceeding_seq
        return self

    def strip_post_newlines(self) -> str:
        """ Strips newlines after the matched pattern """
        self.proceeding_seq = self.proceeding_seq + r"(?:\r?\n)?"
        return self

    def strip_surrounding_newlines(self) -> Self:
        """ Strips newlines before and after the matched pattern """
        return self.strip_pre_newlines().strip_post_newlines()
    
    
if __name__ == "__main__":
    sample_text = """
Line before

<ls_sample_zone>
This is the content to be replaced.
It spans multiple lines.
</ls_sample_zone>

Line after"""

    replacement_text = "This content has been replaced."

    str_replace = str_replace_engine().with_default_zone_pattern(
        tag_prefix="ls_",
        tag="sample_zone"
    )
    pattern = str_replace.get_pattern()

    output = str_replace.replace(
        text_to_replace=sample_text,
        replacement=replacement_text
    )
    
    print("Generated Pattern:")
    print(pattern)
    
    print("\nOriginal Text:")
    print(sample_text)
    
    print("\nOutput after Replacement:")
    print(output)
    
    