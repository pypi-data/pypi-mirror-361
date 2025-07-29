from .tei_to_text_and_standoff import transform_xml_folder
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Flatten all TEI-XML-Files in a folder "
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="The source folder containg XML files.",
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="The target folder for the extractions in json.",
    )

    args = parser.parse_args()
    transform_xml_folder(Path(args.source), Path(args.target))


if __name__ == "__main__":
    main()
