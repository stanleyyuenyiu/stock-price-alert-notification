import cli.dummy.stock_data_generator as stock_data_generator

def init(subparsers):
    consumer_parsers = subparsers.add_parser('dummy')
    nested_parsers = consumer_parsers.add_subparsers(required=True)
    stock_data_generator.init(nested_parsers)

    

    

    

    

    