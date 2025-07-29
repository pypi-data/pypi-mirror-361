from argparse import ArgumentParser, Namespace
import json
import os

from fissionbox.cli.utils.env import get_client
from fissionbox.core.reactor import Reactor, DetectionTaskGoal


client = get_client()


def register(parser: ArgumentParser) -> None:
    """
    Register commands for the reactor namespace.
    """
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new reactor")
    create_parser.add_argument(
        "--name",
        type=str,
        help="Name of the reactor (e.g., My-Reactor-42)",
        required=True,
    )
    create_parser.add_argument(
        "--description", type=str, help="Description of the reactor", default=""
    )
    create_parser.add_argument(
        "--tags", type=str, nargs="*", help="Tags for the reactor", default=[]
    )
    create_parser.add_argument(
        "--metadata",
        type=json.loads,
        help="Metadata for the reactor in JSON format",
        default="{}",
    )
    create_parser.add_argument(
        "--n-goals", type=int, help="Number of goals for the reactor", required=True
    )

    list_parser = subparsers.add_parser("list", help="List all reactors")

    delete_parser = subparsers.add_parser("delete", help="Delete a reactor")
    delete_parser.add_argument(
        "--id", type=str, help="ID of the reactor to delete", required=True
    )


def main(args: Namespace) -> None:
    """
    Main function for the sample namespace.
    This function handles the execution of commands based on the parsed arguments.
    """
    if args.command == "create":
        goals = []
        while len(goals) < args.n_goals:
            goal = DetectionTaskGoal(
                prompt=input("Enter the goal prompt (e.g., ripe strawberries): "),
                reason=input(
                    "Enter the reason/goal why you want this prompt (e.g., take out unripe strawberries out): "
                ),
                label=input("Enter the label for the goal (e.g., ripe_strawberry): "),
            )
            goals.append(goal)
        reactor = Reactor(
            name=args.name,
            description=args.description,
            tags=args.tags,
            metadata=args.metadata,
            goals=goals,
        )
        response = client.reactor.create(reactor)
        print(json.dumps(response, indent=2))

    if args.command == "list":
        response = client.reactor.list()
        if response:
            reactors = [reactor.model_dump() for reactor in response.values()]
            print(json.dumps(reactors, indent=2))
        else:
            print("No reactors found.")

    if args.command == "delete":
        if not args.id:
            print("Please provide the reactor ID to delete.")
            return
        response = client.reactor.delete(args.id)
        if response:
            print(f"Reactor with ID {args.id} deleted successfully.")
        else:
            print(f"Failed to delete reactor with ID {args.id}.")
