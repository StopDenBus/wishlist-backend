
import enum

from classy_fastapi import Routable, delete, get, post, put
from databases import Database
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Enum, Float, Integer, String, Table, Text, UniqueConstraint, asc, desc, text
from typing import List

class OrderBy(enum.Enum):
    asc = "ascending"
    desc = "descending"

class PriorityEnum(enum.Enum):
    high = "Hoch"
    middle = "Mittel"
    low = "Niedrig"

class SortBy(enum.Enum):
    product = "product"
    price =  "price"
    url = "url"
    priority = "priority"

class WishIn(BaseModel):
    product: str
    price: float
    url: str
    priority: PriorityEnum

class Wish(BaseModel):
    id: int
    product: str
    price: float
    url: str
    priority: PriorityEnum

class WishRoutes(Routable):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__database: Database = kwargs.get('database', None)
        self.__metadata = kwargs.get('metadata', None)
        self.__table: Table = None

        self.setup()

    def setup(self):
        self.__table = Table(
            "wish",
            self.__metadata,
            Column("id", Integer, primary_key=True),
            Column("product", String(256), nullable=False),
            Column("price", Float, server_default = text("0")),
            Column("url", Text, nullable=False),
            Column("priority", Enum(PriorityEnum)),
            UniqueConstraint("product", name="uix_product")
        )

    @delete("/wish/by_id/{id}", status_code=status.HTTP_200_OK, response_model=Wish, tags=["wish"])
    async def delete_wish_by_id(self, id: int):
        """
        id: Your item ID description will be here
        """    
        query = self.__table.select().where(self.__table.columns.id == id)
        result = await self.__database.fetch_one(query)
        if result != None:
            query = self.__table.delete().where(self.__table.columns.id == id)
            delete_result = await self.__database.execute(query=query)
            if delete_result == 1:
                return result

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wish with id {id} not found.")

    @delete("/wish/by_name/{wish}", response_model=Wish, tags=["wish"])
    async def delete_wish_by_name(self, wish: str):
        query = self.__table.select().where(self.__table.columns.product == wish)
        result = await self.__database.fetch_one(query)
        if result != None:
            query = self.__table.delete().where(self.__table.columns.product == wish)
            delete_result = await self.__database.execute(query=query)
            if delete_result == 1:
                return result

        raise HTTPException(status_code=404, detail=f"Wish {wish} not found.")

    @get('/wishes', response_model=List[Wish], tags=["wish"])
    async def get_wishes(self, sort_by: SortBy = SortBy.product, order_by: OrderBy = OrderBy.asc) -> List:
        if order_by == OrderBy.asc:
            query = self.__table.select().order_by(asc(self.__table.columns[sort_by.value]))
        else:
            query = self.__table.select().order_by(desc(self.__table.columns[sort_by.value]))
        return await self.__database.fetch_all(query) 

    @get("/wish/by_id/{id}", response_model=Wish, tags=["wish"])
    async def get_wish_by_id(self, id: int):        
        query = self.__table.select().where(self.__table.columns.id == id)
        result = await self.__database.fetch_one(query)
        if result != None:
            return result
        
        raise HTTPException(status_code=404, detail=f"Wish with ID {id} not found.")

    @get("/wish/by_name/{wish}", response_model=Wish, tags=["wish"])
    async def get_wish_by_name(self, wish: str):
        query = self.__table.select().where(self.__table.columns.product == wish)
        result = await self.__database.fetch_one(query)
        if result != None:
            return result
        
        raise HTTPException(status_code=404, detail=f"Wish {wish} not found.")

    @post("/wish", status_code=status.HTTP_201_CREATED, response_model=Wish, tags=["wish"])
    async def create_wish(self, wish: WishIn):
        print(wish)
        query = self.__table.insert().values(
            product=wish.product,
            price = wish.price,
            url = wish.url,
            priority = wish.priority
        )
        last_record_id = await self.__database.execute(query)
        return {**wish.model_dump(), "id": last_record_id}

    @put("/wish/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=Wish, tags=["wish"])
    async def update_wish(self, id: int, wish: WishIn):
        query = self.__table.update().values(
            product=wish.product,
            price = wish.price,
            url = wish.url,
            priority = wish.priority
        ).where(self.__table.columns.id == id)
        result = await self.__database.execute(query=query)
        if result in [0, 1]:
            query = self.__table.select().where(self.__table.columns.id == id)
            result = await self.__database.fetch_one(query)
            if result != None:
                return result
            
        raise HTTPException(status_code=404, detail=f"Wish with ID {id} not found.")   


    
