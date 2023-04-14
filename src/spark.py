from spark.stock_aggreate.app import app as stock_aggreate_app
import argparse

def app(args):
    if args.app == "stock_aggreate_app":
        stock_aggreate_app() 
    else:
        raise Exception("unknown spark app")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark app")

    parser.add_argument('-a', dest="app", type=str, required=True,
                        help="app")
  
    app(parser.parse_args())

#spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.apache.spark:spark-avro_2.12:3.3.2 --jars ./bin/postgresql-42.5.4.jar spark.py -a stock_aggreate_app 