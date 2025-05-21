import sqlite3
import uuid
from datetime import datetime
import numpy as np
from typing import List, Tuple
import pickle
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkDatabase:
    def __init__(self, db_path="file_chunks.sqlite"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        logger.info("Initializing the database.")
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
                upload_date TEXT,
                keyword TEXT,
                distance REAL
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_project ON file_chunks(project_name)')
        conn.commit()
        conn.close()

    def print_all_rows(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM file_chunks')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.close()

    def print_table_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(file_chunks)")
        columns = cursor.fetchall()
        print("Table schema:")
        for column in columns:
            print(column)
        conn.close()


    def insert_chunks(self, project_name, results):
        logger.info(f"Inserting chunks for project: {project_name}")
        """Insert chunks and embeddings into the database."""
        if not isinstance(results, list) or not all(isinstance(result, dict) for result in results):
            raise TypeError("Expected 'results' to be a list of dictionaries.")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for result in results:
            chunk_id = str(uuid.uuid4())
            file_name = result["file_name"]
            chunk_text = result["content"]
            page_number = result["metadata"].get("page", None)
            upload_date = datetime.now().isoformat()
            embedding_bytes = result["embedding"].tobytes()

            cursor.execute('''
                INSERT INTO file_chunks (chunk_id, project_name, file_name, chunk_text, embedding, page_number, upload_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chunk_id, project_name, file_name, chunk_text, embedding_bytes, page_number, upload_date))
            logger.info(f"Inserted chunk {chunk_id} from file '{file_name}' (page {page_number})")
        conn.commit()
        conn.close()

    def get_chunks_by_project(self, project_name):
        logger.info(f"Fetching chunks for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_id, file_name, chunk_text, page_number, embedding, upload_date
            FROM file_chunks WHERE project_name = ?
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_embeddings_by_project(self, project_name: str) -> List[Tuple[int, np.ndarray]]:
        logger.info(f"Fetching embeddings for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_id, embedding
            FROM file_chunks WHERE project_name = ?
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        embeddings = [(chunk_id, pickle.loads(embedding_blob)) for chunk_id, embedding_blob in rows]
        return embeddings
    
    def add_keyword_and_distance(self, chunk_id: str, query: str, distance: float): 
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update the row with matching chunk_id
        cursor.execute('''
            UPDATE file_chunks
            SET keyword = ?, distance = ?
            WHERE chunk_id = ?
        ''', (query, distance, chunk_id))
        logger.info(f"Updated chunk {chunk_id} with keyword '{query}' and distance {distance}")
        conn.commit()
        conn.close()
        
    #retireve 


if __name__ == "__main__":
    db = ChunkDatabase()  # This triggers init_db()
    db.print_table_schema()
