import aiorun

def main(args):
    from applications.search_alert import app
    aiorun.run(app(), stop_on_unhandled_errors=True)

def init(subparsers):
    parser = subparsers.add_parser('search_alert')
    parser.set_defaults(func=main)

    

    

    

    

    