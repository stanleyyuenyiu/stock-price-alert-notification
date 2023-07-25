import cli.consumers.search_alert as search_alert
import cli.consumers.remove_alert as remove_alert


def init(subparsers):
    consumer_parsers = subparsers.add_parser('consumer')
    nested_parsers = consumer_parsers.add_subparsers(required=True)
    search_alert.init(nested_parsers)
    remove_alert.init(nested_parsers)

    

    

    

    

    