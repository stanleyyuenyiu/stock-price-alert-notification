from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Date, table, column
from sqlalchemy.exc import DuplicateColumnError
from . import foreach_sink_operator

engine = create_engine('postgresql://postgres:postgres@localhost:5432/kafka')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

stockAgg = table("stock_agg",
        column("id"),
        column("value"),
)

class DbSinkOperator(foreach_sink_operator.ForEachOperator):
    def open(self, partition_id, epoch_id):
        self.session = Session
        return True

    def process(self, row):
        try:
            stmt = insert(stockAgg).values(value=row.value)
            with engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()
        except DuplicateColumnError as e:
            print(str(e))
        except Exception  as e:
            print("unknown error {}".format(e))

    def close(self, err):
        if err:
            raise err