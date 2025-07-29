from argparse import ArgumentParser, Namespace
import json
import os

from fissionbox.cli.utils.env import get_client


client = get_client()


def register(parser: ArgumentParser) -> None:
    """
    Register commands for the sample namespace.
    """
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Example command registration
    upload_parser = subparsers.add_parser("upload", help="Create a new sample")
    upload_parser.add_argument(
        "--path", type=str, help="Path to the sample(s)", required=True
    )
    upload_parser.add_argument(
        "--metadata",
        type=json.loads,
        help="Metadata for the sample in JSON format",
        default="{}",
    )
    upload_parser.add_argument(
        "--batch-id",
        type=str,
        help="Batch ID for the sample upload (optional)",
        default="default",
    )


def main(args: Namespace) -> None:
    """
    Main function for the sample namespace.
    This function handles the execution of commands based on the parsed arguments.
    """
    if args.command == "upload":
        if os.path.isdir(args.path):
            yes = input(
                f"The path {args.path} is a directory. Do you want to upload all samples in this folder? (y/n): "
            )
            if yes.lower() != "y":
                print("Upload cancelled.")
                return
            print(f"Uploading all samples in folder: {args.path}")
            response = client.sample.upload_folder(
                path=args.path,
                metadata=args.metadata,
                batch_id=args.batch_id,
            )
            print(response)
        else:
            response = client.sample.upload(
                path=args.path,
                metadata=args.metadata,
                batch_id=args.batch_id,
            )
            print(response)
    else:
        print(f"Unknown command: {args.command}")
