import aiorun
import argparse

async def main(args):
    print(args.consumer)
    if args.consumer == "consumer_search_alert":
        from applications.search_alert_consumer.main import app as search_consumer
        await search_consumer()
    elif args.consumer == "consumer_remove_alert":
        from applications.remove_alert_consumer.main import app as remove_consumer
        await remove_consumer()
    else:
        raise Exception("unknown consumer")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consumer")

    parser.add_argument('-c', dest="consumer", type=str, required=True,
                        help="consumer handler name")
  
    aiorun.run(main(parser.parse_args()), stop_on_unhandled_errors=True)


