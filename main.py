import sys
from utils.zones_processor import ZonesProcessor
from src.utils.get_input import extract_input_json
from src.mailmerge.text_mailmerge import TextMailMerge


def main():
    mailmerge = TextMailMerge()
    print(f"Initialized TextMailMerge: {mailmerge}")
    template = (
        "/home/ernestfoo/Documents/python-mailmerge/Sample_Input/sample_contract.txt"
    )
    input = "/home/ernestfoo/Documents/python-mailmerge/Sample_Input/zones.json"
    output = "apple/output.txt"
    json_data = extract_input_json(input)

    mailmerge.load_input_data(json_data)
    mailmerge.load_template_from_path(template)
    mailmerge.perform_merge()
    mailmerge.save_output_from_buffer(output)

    print(
        f"Mail merge operations completed successfully." f" Output saved to: {output}"
    )


def CLI():
    TextMailMerge().run_from_CLI()


if __name__ == "__main__":
    print(f"sys.argv: {sys.argv}")
    if len(sys.argv) == 1:
        main()
    else:
        CLI()
