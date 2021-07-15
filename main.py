from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from deta import Deta

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


deta = Deta()
db = deta.Base("notebooks")


class Record(BaseModel):
    key: str
    active: bool
    content: str
    name: str
    public: Optional[bool] = False

class DeleteRecord(BaseModel):
    key: str

class NewRecord(BaseModel):
    name: str
    content: str

@app.get("/")
def render_app():
    return FileResponse("./static/index.html")

@app.put("/update")
def update_record(r: Record):
    res = db.put(r.dict())
    return r.dict()

@app.delete("/delete")
def delete_record(dr: DeleteRecord):
    res = db.delete(dr.key)
    return res

@app.post("/create")
def create_record(r: NewRecord):
    res = db.put(r.dict())
    return res

@app.get("/list")
def list_records():
    res = db.fetch()
    all_items = res.items

    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items
    return all_items

@app.get("/public/{key}")
def render_public(key: str):
    r = db.get(key)
    if r == None:
        return "404 not found" 
    if "public" in r:
        if not r["public"]:
            return "404 not found"
        else:
            return FileResponse("./static/public.html")
    return "404 not found"


@app.get("/public/raw/{key}")
def raw_public_content(key: str):
    res = db.get(key)
    return [res]