from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from . import curd, models, schemas
from .database import create_table, conn, cur
from typing import List


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await create_table(None)
    yield


app = FastAPI(lifespan=lifespan)


@app.on_event("shutdown")
async def shutdown_event():
    cur.close()
    conn.close()


# Create an item
@app.post("/items")
def create_item(items: List[schemas.ItemCreate]):
    return curd.create_items(items=items)


# Read all items
@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    items = curd.get_items(skip=skip, limit=limit)
    return items


# Read a single item by ID
@app.get("/items/{p_key}", response_model=schemas.Item)
def read_item(p_key: int):
    db_item = curd.get_item(p_key=p_key)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
