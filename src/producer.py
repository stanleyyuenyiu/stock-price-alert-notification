import aiorun
import argparse
from producer.stock_generator.app import app as producer_stock_generator


async def app(args):
    print(args.producer)
    if args.producer == "producer_stock_generator":
        await producer_stock_generator() 
    else:
        raise Exception("unknown producer")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer")

    parser.add_argument('-p', dest="producer", type=str, required=True,
                        help="producer handler name")
  
    aiorun.run(app(parser.parse_args()), stop_on_unhandled_errors=True)