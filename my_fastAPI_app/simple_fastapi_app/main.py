from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return [{"item_id": 1, "name": "Item One"}, {"item_id": 2, "name": "Item Two"}]

@app.post("/items/")
async def create_item(item: dict):
    return {"item_id": 3, "name": item['name']}