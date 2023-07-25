import aiorun
def main(args):
    pass
   

    # if args.consumer == "consumer_search_alert":
    #     from applications.search_alert_consumer.main import app as search_consumer
    #     await search_consumer()
    # elif args.consumer == "consumer_remove_alert":
    #     from applications.remove_alert_consumer.main import app as remove_consumer
    #     await remove_consumer()
    # elif args.consumer == "outbox":
    #     from applications.outbox_rule_consumer.main import app as outbox_rule_consumer
    #     await outbox_rule_consumer()
    # else:
    #     raise Exception("unknown consumer")


def init(subparsers):
    parser = subparsers.add_parser('stock_data_generator')
    parser.set_defaults(func=main)

    

    

    

    

    