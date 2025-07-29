from argparse import ArgumentParser, Namespace

# Import all submodules to register their commands
from fissionbox.cli.dataset import module as dataset_module
from fissionbox.cli.sample import module as sample_module
from fissionbox.cli.reactor import module as reactor_module


def main():
    parser = ArgumentParser(description="FissionBox CLI")
    subparsers = parser.add_subparsers(dest="namespace", required=True)
    namespace_modules = {
        "dataset": dataset_module,
        "sample": sample_module,
        "reactor": reactor_module,
    }
    for namespace_name, module in namespace_modules.items():
        subparser = subparsers.add_parser(namespace_name, help=module.__doc__)
        module.register(subparser)

    args = parser.parse_args()
    namespace_name = args.namespace
    namespace_modules[namespace_name].main(args)
    

if __name__ == "__main__":
    main()
