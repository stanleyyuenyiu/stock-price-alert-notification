import argparse
import cli.aggregator
import cli.consumer
def execute():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    cli.aggregator.init(subparsers)
    cli.consumer.init(subparsers)
    args = parser.parse_args()
    args.func(args)