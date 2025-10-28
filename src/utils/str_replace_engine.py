import re
from typing import Self


class StrReplaceEngine:
    """
    StrReplaceEngine
    A flexible, chainable string replacement engine built around configurable regular-expression
    pattern components.
    StrReplaceEngine helps construct complex match patterns composed of:
        - optional preceding sequence (preceeding_seq)
        - optional start tag (with configurable prefix)
        - a body (the main capture or literal to match)
        - optional end tag (with configurable prefix)
        - optional proceeding sequence (proceeding_seq)

    The engine is intended for templating/mail-merge-like workflows where keys or zones are
    wrapped in start/end tags and may need removal or substitution while optionally trimming
    surrounding newlines.

    Key features
    - Fluent API: most setters return self so calls can be chained.
    - Tag support: configure a tag prefix and distinct start/end tag names; inputs are safely
        escaped for use inside generated regular expressions.
    - Key matching: set_key() sets the body to match a literal key wrapped in double square
        brackets (e.g. [[KEY]]) with proper escaping.
    - Newline trimming: helpers to make patterns optionally strip a single surrounding newline
        before and/or after the matched region.
    - Replacement operations use re.sub with DOTALL so the body can match across multiple lines.
    - remove_zone returns the modified string after removing the matched region (ignores match count).

    Constructor parameters
    - body: str = "(.*?)"
            Default body pattern used when building the regex. By default matches any content lazily.
    - replacement: str = ""
            (Legacy/placeholder) default replacement text; actual replacement strings are passed to
            replace/replace_key/remove_zone as needed.
    - text_to_replace: str = ""
            (Optional) store text on the instance; replace methods accept text arguments directly.

    Important methods (summary)
    - clear_pattern() -> Self
            Reset pattern components to defaults.
    - with_default_global_pattern() -> Self
            Prepare a default global pattern (clears existing pattern components).
    - with_default_zone_pattern(tag_prefix: str, tag: str) -> Self
            Convenience to prepare a zone-style pattern: clears pattern, strips surrounding newlines,
            sets identical start/end tags and a tag prefix, and sets a generic body "(.*?)".
    - with_default_key_pattern() -> Self
            Clears pattern and prepares a key-style pattern placeholder.
    - strip_tags(string: str) -> str
            Remove the configured start/end tags (including the configured prefix) from the given string.
    - get_start_tag() -> str, get_end_tag() -> str
            Return the start/end tag portions that will be included in the final regex (escaped and
            wrapped appropriately). Returns an empty string if not configured.
    - get_pattern() -> str
            Build and return the final regular-expression pattern string by concatenating the
            preceding sequence, start tag, body, end tag, and proceeding sequence.
    - replace(text_to_replace: str, replacement: str) -> str
            Apply re.sub using the engine's pattern and the provided replacement text. Uses DOTALL.
    - replace_key(key: str, text_to_replace: str, replacement: str) -> str
            Convenience: call set_key(key) then perform replacement on the provided text.
    - remove_zone(text_to_replace: str) -> str
            Remove the matched region from the text. Uses re.subn and returns only the modified string.
    - set_text(text: str) -> Self
            Store text on the instance for potential chained operations.
    - set_key(key: str) -> Self
            Set the body to match a literal key wrapped with double square brackets (e.g. [[key]]),
            escaping the key for safe insertion into the regex.
    - set_body(pattern: str) -> Self
            Set the body (a regex fragment) directly.
    - set_tag_prefix(tag_prefix: str) -> Self
            Set the tag prefix (escaped for regex use). The prefix is prepended to both start and end tags.
    - set_start_end_tags(start_tag: Optional[str]=None, end_tag: Optional[str]=None) -> Self
            Set start and/or end tag names (escaped). If only one is provided, only that component is set.
    - strip_pre_newlines() / strip_post_newlines() -> Self
            Add optional single-newline trimming before/after the matched region by adjusting the
            preceding/proceeding sequence portions used in the generated regex.
    - strip_surrounding_newlines() -> Self
            Apply both pre- and post-newline stripping.

    Notes and behavior
    - Inputs passed to set_tag_prefix and set_start_end_tags are escaped using re.escape to avoid
        unintended regex metacharacter behavior.
    - The produced pattern is used with flags=re.DOTALL so '.' matches newlines inside the body.
    - strip_pre_newlines and strip_post_newlines insert non-capturing optional groups that match
        a single CRLF or LF sequence: (?:\r?\n)?.
    - remove_zone uses re.subn and returns only the modified string (the substitution count is
        discarded).
    - The class exposes internal pattern components (preceeding_seq, tag_prefix, start_tag, body,
        end_tag, proceeding_seq) which can be manipulated via the provided setters for precise control.
    Example (conceptual)
            engine = StrReplaceEngine().with_default_zone_pattern('ms-', 'zone')
            new_text = engine.replace_key('USERNAME', original_text, 'Alice')
            # Or to remove an entire tagged zone while trimming surrounding newlines:
            engine.with_default_zone_pattern('app-', 'block').strip_surrounding_newlines()
            stripped = engine.remove_zone(original_text)
    This class is intentionally minimal with a focus on reproducible, testable regex construction
    and safe escaping of externally provided tag/key inputs.
    """

    def __init__(
        self,
        body: str = "(.*?)",  # By default match any content):
        replacement: str = "",
        text_to_replace: str = "",
    ):

        # Initialize with default values
        self.preceeding_seq = ""  # The sequence before the matched pattern
        self.tag_prefix = ""  # The prefix for the start and end tags
        self.start_tag = ""  # The starting tag of the pattern
        self.body = body  # The main body of the pattern to match
        self.end_tag = ""  # The ending tag of the pattern
        self.proceeding_seq = ""  # The sequence after the matched pattern

        self.matched_string = ""  # The last matched string
        self.text_to_replace = ""  # The text where replacements will be made
        self.replacement_text = ""  # The text to replace the matched pattern with

    def clear_pattern(self) -> Self:
        """Resets the pattern components to default values"""
        self.preceeding_seq = ""
        self.tag_prefix = ""
        self.start_tag = ""
        self.body = ".*?"  # Default body matches any content lazily
        self.end_tag = ""
        self.proceeding_seq = ""
        return self

    def with_default_global_pattern(self) -> Self:
        """Builds the default global pattern with any start/end tags or newline stripping"""
        self.clear_pattern()
        return self

    def with_default_zone_pattern(self, tag_prefix: str, tag: str) -> Self:
        """Builds the default pattern with any start/end tags or newline stripping"""
        self.clear_pattern()
        # self.strip_surrounding_newlines()
        self.set_start_end_tags(start_tag=tag, end_tag=tag)
        self.set_tag_prefix(tag_prefix)
        self.set_body(".*?")
        return self

    def with_default_row_pattern(
        self, original_row_content, tag_prefix: str = "ls_", tag: str = "row"
    ) -> Self:
        """Builds the default pattern with any start/end tags or newline stripping"""
        self.clear_pattern()
        self.set_start_end_tags(start_tag=tag, end_tag=tag)
        self.set_tag_prefix(tag_prefix)
        self.set_body(re.escape(original_row_content))
        return self

    def with_default_key_pattern(self) -> Self:
        self.clear_pattern()
        return self

    def strip_tags(self, string) -> str:
        """Strips tags from the given string"""
        return string.replace(f"<{self.tag_prefix}{self.start_tag}>", "").replace(
            f"</{self.tag_prefix}{self.end_tag}>", ""
        )

    def get_start_tag(self) -> str:
        """Returns the start tag with prefix"""
        if self.tag_prefix and self.start_tag:
            return f"(<{self.tag_prefix}{self.start_tag}>)"
        return ""

    def get_end_tag(self) -> str:
        """Returns the end tag with prefix"""
        if self.tag_prefix and self.end_tag:
            return f"(</{self.tag_prefix}{self.end_tag}>)"
        return ""

    def get_pattern(self) -> str:
        """Returns the final regex pattern
        Pattern structure:
        preceeding_seq + (<{self.tag_prefix}{self.start_tag}>) + (body) + (<{self.tag_prefix}{self.start_tag}>) + proceeding_seq
        """

        pattern = ""
        pattern += self.preceeding_seq
        pattern += self.get_start_tag()
        pattern += self.body
        pattern += self.get_end_tag()
        pattern += self.proceeding_seq

        return pattern

    def replace(self, text_to_replace: str, replacement: str) -> str:
        """
        Replaces the matched pattern in the text

        """
        string = re.sub(
            self.get_pattern(), replacement, text_to_replace, flags=re.DOTALL
        )
        return string

    def replace_key(self, key: str, text_to_replace: str, replacement: str) -> str:
        """Replaces the matched pattern for the given key in the text"""
        self.set_key(key)

        string = re.sub(
            self.get_pattern(), replacement, text_to_replace, flags=re.DOTALL
        )

        return string

    def remove_zone(self, text_to_replace: str) -> str:
        """Removes the matched pattern from the text"""
        string = re.subn(self.get_pattern(), "", text_to_replace, flags=re.DOTALL)
        return string[0]  # Return only the modified string, ignore count [1]

    def set_text(self, text: str) -> Self:
        """Sets the text to perform replacements on"""
        self.text_to_replace = text
        return self

    def set_key(self, key: str) -> Self:
        """Sets the key for the pattern body"""
        self.body = r"\[\[" + re.escape(key) + r"\]\]"
        return self

    def set_body(self, pattern: str) -> Self:
        """Sets the body of the pattern"""
        self.body = f"({pattern})"
        return self

    def set_tag_prefix(self, tag_prefix: str) -> Self:
        """Sets the tag prefix for the start and end tags"""
        self.tag_prefix = re.escape(tag_prefix)
        return self

    def set_start_end_tags(self, start_tag: str = None, end_tag: str = None) -> Self:
        """Sets the start and end tags for the pattern"""
        if start_tag is not None:
            self.start_tag = re.escape(start_tag)
        if end_tag is not None:
            self.end_tag = re.escape(end_tag)
        return self

    def strip_pre_newlines(self) -> Self:
        """Strips newlines before the matched pattern"""
        self.preceeding_seq = r"(?:\r?\n)?" + self.preceeding_seq
        return self

    def strip_post_newlines(self) -> str:
        """Strips newlines after the matched pattern"""
        self.proceeding_seq = self.proceeding_seq + r"(?:\r?\n)?"
        return self

    def strip_surrounding_newlines(self) -> Self:
        """Strips newlines before and after the matched pattern"""
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

    str_replace = StrReplaceEngine().with_default_zone_pattern(
        tag_prefix="ls_", tag="sample_zone"
    )
    pattern = str_replace.get_pattern()

    output = str_replace.replace(
        text_to_replace=sample_text, replacement=replacement_text
    )

    print("Generated Pattern:")
    print(pattern)

    print("\nOriginal Text:")
    print(sample_text)

    print("\nOutput after Replacement:")
    print(output)
