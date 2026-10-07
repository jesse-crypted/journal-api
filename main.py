import os
import sqlite3
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Journal API")
db = sqlite3.connect(os.getenv("DB_PATH", "journal.db"), check_same_thread=False)
db.row_factory = sqlite3.Row
db.execute(
    """CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY, work TEXT, struggle TEXT, intention TEXT, created_at TEXT)"""
)


class Entry(BaseModel):
    work: str = Field(min_length=1, max_length=256)
    struggle: str = Field(min_length=1, max_length=256)
    intention: str = Field(min_length=1, max_length=256)


@app.post("/entries", status_code=201)
def create_entry(entry: Entry):
    row = (str(uuid.uuid4()), entry.work, entry.struggle, entry.intention,
           datetime.now(timezone.utc).isoformat())
    db.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", row)
    db.commit()
    return get_entry(row[0])


@app.get("/entries")
def list_entries():
    return [dict(r) for r in db.execute("SELECT * FROM entries ORDER BY created_at DESC")]


@app.get("/entries/{entry_id}")
def get_entry(entry_id: str):
    row = db.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Entry not found")
    return dict(row)


@app.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: str):
    if db.execute("DELETE FROM entries WHERE id = ?", (entry_id,)).rowcount == 0:
        raise HTTPException(404, "Entry not found")
    db.commit()