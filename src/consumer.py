import aiorun
import argparse



async def main(args):
    print(args.consumer)
    if args.consumer == "consumer_search_alert":
        from consumer.search_alert_consumer import app as search_alert
        await search_alert.App()
    elif args.consumer == "consumer_remove_alert":
        from consumer.remove_alert_consumer import app as remove_alert
        await remove_alert.App()
        pass
    else:
        raise Exception("unknown consumer")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consumer")

    parser.add_argument('-c', dest="consumer", type=str, required=True,
                        help="consumer handler name")
  
    aiorun.run(main(parser.parse_args()), stop_on_unhandled_errors=True)


