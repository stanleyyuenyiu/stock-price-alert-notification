from pydantic import BaseModel
class StockAggreateModel(BaseModel):
    symbol:str
    min_price:float
    max_price:float