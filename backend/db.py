import sqlite3
import uuid
from datetime import datetime
import numpy as np

class ChunkDatabase:
    def __init__(self, db_path="file_chunks.sqlite"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_chunks (
                chunk_id TEXT PRIMARY KEY,
                project_name TEXT,
                file_name TEXT,
                chunk_text TEXT,
                embedding BLOB,
                page_number INTEGER,
                upload_date TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_project ON file_chunks(project_name)')
        conn.commit()
        conn.close()

    def insert_chunks(self, project_name, file_name, chunks, embeddings):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk_text = chunk["content"]
            page_number = chunk["metadata"].get("page", None)
            upload_date = datetime.now().isoformat()
            embedding_bytes = embeddings[i].tobytes()

            cursor.execute('''
                INSERT INTO file_chunks (chunk_id, project_name, file_name, chunk_text, embedding, page_number, upload_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chunk_id, project_name, file_name, chunk_text, embedding_bytes, page_number, upload_date))
        conn.commit()
        conn.close()

    def get_chunks_by_project(self, project_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_id, file_name, chunk_text, page_number, embedding, upload_date
            FROM file_chunks WHERE project_name = ?
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        return rows

if __name__ == "__main__":
    db = ChunkDatabase()  # This triggers init_db()
