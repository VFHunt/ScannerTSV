import sqlite3
import uuid
from datetime import datetime, timezone
import numpy as np
from typing import List, Tuple
import pickle
import logging
from ast import literal_eval

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
                distance REAL,
                scanned BOOLEAN DEFAULT 0
            )
        ''')
        existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(file_chunks)").fetchall()]

        if "keyword" not in existing_columns:
            cursor.execute("ALTER TABLE file_chunks ADD COLUMN keyword TEXT")
        if "distance" not in existing_columns:
            cursor.execute("ALTER TABLE file_chunks ADD COLUMN distance REAL")
        if "scanned" not in existing_columns:
            cursor.execute("ALTER TABLE file_chunks ADD COLUMN scanned INTEGER DEFAULT 0")
        if "scanned_time" not in existing_columns:
            cursor.execute("ALTER TABLE file_chunks ADD COLUMN scanned_time TEXT")
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

    def get_chunks_by_project_and_file(self, project_name, file_name):
        logger.info(f"Fetching chunks for project: {project_name}, file: {file_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_text, page_number, keyword
            FROM file_chunks
            WHERE project_name = ? AND file_name = ? AND keyword IS NOT NULL AND keyword != ''
        ''', (project_name, file_name))

        rows = cursor.fetchall()
        conn.close()
        # Group keywords by (chunk_text, page_number)
        grouped = {}
        for chunk_text, page_number, keyword in rows:
            key = (chunk_text, page_number)
            if key not in grouped:
                grouped[key] = set()
            if keyword:
                grouped[key].add(keyword)
        results = [
            {
                "text": text,
                "page": page,
                "keywords": list(keywords)
            }
            for (text, page), keywords in grouped.items()
        ]
        logger.info(f"Fetched {len(results)} formatted chunks for file: {file_name} in project: {project_name}")
        return results

    def get_embeddings_by_project(self, project_name: str) -> List[Tuple[str, np.ndarray]]:
        logger.info(f"Fetching embeddings for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_id, embedding
            FROM file_chunks WHERE project_name = ?
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        embeddings = [(chunk_id, np.frombuffer(embedding_blob, dtype=np.float32)) for chunk_id, embedding_blob in rows]
        #logger.info(f"Fetched {type(embeddings)} embeddings for project '{project_name}'")
        return embeddings
    
    def add_keyword_and_distance(self, chunk_id: str, query: str, distance: float):
        #print(f"[DEBUG] Entering add_keyword_and_distance for chunk {chunk_id}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chunk_id FROM file_chunks WHERE chunk_id = ?", (chunk_id,))
        result = cursor.fetchone()
        #print(f"DEBUG: Checking if chunk_id exists — {chunk_id} => {result}")

        if result is None:
            print(f"[WARNING] Chunk ID '{chunk_id}' not found in the database.")
        else:
            # Update the row with matching chunk_id
            cursor.execute('''
            UPDATE file_chunks
            SET keyword = ?, distance = ?
            WHERE chunk_id = ?
            ''', (query, distance, chunk_id))
        #logger.info(f"Updated chunk {chunk_id} with keyword '{query}' and distance {distance}")
        conn.commit()
        conn.close()

    def get_filename(self, project_name):
        logger.info(f"Fetching filenames for project: {project_name} with non-empty keywords")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_name, keyword
            FROM file_chunks
            WHERE project_name = ? AND keyword IS NOT NULL AND keyword != ''
        ''', (project_name,))

        rows = cursor.fetchall()
        conn.close()
        # Group keywords by filename
        grouped = {}
        for file_name, keyword in rows:
            if file_name not in grouped:
                grouped[file_name] = set()
            grouped[file_name].add(keyword)
        # Format for frontend
        results = [
            {
                "Document Name": file,
                "Keywords": list(keywords)
            }
            for file, keywords in grouped.items()
        ]
        logger.info(f"Fetched {len(results)} results for project: {project_name}")
        return results

    def clean_results(self, results):
        cleaned_results = []

        for result in results:
            raw_keywords = result.get('Keywords', [])

            # Flatten all keywords into one list
            combined_keywords = []
            for kw_list in raw_keywords:
                # Convert string representation of list to actual list
                try:
                    kws = literal_eval(kw_list)  # Use literal_eval for safety
                    combined_keywords.extend(kws)
                except:
                    continue

            # Deduplicate and sort
            unique_keywords = sorted(set(combined_keywords))

            cleaned_results.append({
                'Document Name': result['Document Name'],
                'Keywords': unique_keywords  # now a clean list
            })

        return cleaned_results

    def get_projects(self):
        logger.info(f"Searching for existing projects")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT project_name
            FROM  file_chunks
            WHERE project_name IS NOT NULL AND project_name != ''
        ''')
        rows = cursor.fetchall()
        conn.close()
        projects = [row[0] for row in rows]  # unpack tuple to string
        logger.info(f"Fetched {len(projects)} unique projects")
        return projects

    def reset_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_chunks")
        conn.commit()
        conn.close()

    def get_upload_time_project(self, project_name):
        logger.info(f"Fetching upload time for distinct project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT upload_date
            FROM file_chunks
            WHERE project_name = ?
        """, (project_name,))
        rows = cursor.fetchall()
        conn.close()
        logger.info(f"Fetched {len(rows)} results for project: {project_name}")
        return [row[0] for row in rows]

    def delete_project(self, project_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM file_chunks
            WHERE project_name = ?
        """, (project_name,))
        conn.commit()
        conn.close()

    def delete_file(self, project_name, file_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM file_chunks
            WHERE project_name = ? AND file_name = ?
        """, (project_name, file_name))
        conn.commit()
        conn.close()

    def mark_project_chunks_scanned(self, project_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        scanned_time = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            UPDATE file_chunks
            SET scanned = 1, scanned_time = ?
            WHERE project_name = ?
        """, (scanned_time, project_name,))
        conn.commit()
        conn.close()

    def get_files_scanned_status_and_time(self, project_name):
        """
        For each file in a project, check if scanned, and if yes, get the latest scanned time.
        Returns a list of dicts: [{'file_name': ..., 'scanned': bool, 'scanned_time': str or None}, ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_name,
                   MAX(CASE WHEN scanned = 1 THEN upload_date ELSE NULL END) AS scanned_time,
                   MAX(scanned) as is_scanned
            FROM file_chunks
            WHERE project_name = ?
            GROUP BY file_name
        ''', (project_name,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for file_name, scanned_time, is_scanned in rows:
            results.append({
                "file_name": file_name,
                "scanned": bool(is_scanned),
                "scanned_time": scanned_time if scanned_time else None
            })
        return results

    def get_new_embeddings_by_project(self, project_name: str) -> List[Tuple[str, np.ndarray]]:
        logger.info(f"Fetching embeddings for project: {project_name}, not scanned")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chunk_id, embedding
            FROM file_chunks WHERE project_name = ? AND scanned  == 0
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        embeddings = [(chunk_id, np.frombuffer(embedding_blob, dtype=np.float32)) for chunk_id, embedding_blob in rows]
        return embeddings

    def get_all_retrieved_keywords_by_project(self, project_name):
        logger.info(f"Getting keywords for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT keyword
            FROM file_chunks 
            WHERE project_name = ? AND keyword IS NOT NULL AND keyword != ''
        """, (project_name,))
        rows = cursor.fetchall()
        conn.close()
        keywords_found = [row[0] for row in rows]
        return keywords_found



if __name__ == "__main__":
    db = ChunkDatabase()  # This triggers init_db()
    db.print_table_schema()
    db.get_filename(project_name='test')
    #db.add_keyword_and_distance(chunk_id='c262a5af-9e51-4aba-abfd-76e9e0391b62', query='requirements', distance=0.123)
    #results = db.get_chunks_by_project_and_file(project_name='test', file_name='ES10ST_1.pdf')
    #for result in results:
    #    print(result)
    db.get_projects()
    results = db.get_files_scanned_status_and_time(project_name='test')
    for r in results:
        print(r)
    keywords = db.get_all_retrieved_keywords_by_project(project_name='test')
    for k in keywords: print(k)
