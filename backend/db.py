import sqlite3
import uuid
from datetime import datetime, timezone
import numpy as np
from typing import List, Tuple
import pickle
import logging
import ast
from ast import literal_eval

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkDatabase:
    def __init__(self, db_path="file_chunks.sqlite"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
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
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            raise

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

        # Now also selecting `distance`
        cursor.execute('''
                       SELECT chunk_text, page_number, keyword, distance
                       FROM file_chunks
                       WHERE project_name = ?
                         AND file_name = ?
                         AND keyword IS NOT NULL
                         AND keyword != ''
                       ''', (project_name, file_name))

        rows = cursor.fetchall()
        conn.close()

        # Group keywords+distances by (chunk_text, page_number)
        grouped = {}

        for chunk_text, page_number, keyword, distance in rows:
            key = (chunk_text, page_number)
            if key not in grouped:
                grouped[key] = set()

            if keyword:
                try:
                    parsed_keywords = ast.literal_eval(keyword)
                except Exception as e:
                    logger.warning(f"Failed to parse keyword: {keyword}, error: {e}")
                    parsed_keywords = [keyword.strip()]

                try:
                    parsed_distances = ast.literal_eval(distance) if distance else None
                except Exception as e:
                    logger.warning(f"Failed to parse distance: {distance}, error: {e}")
                    parsed_distances = None

                if (isinstance(parsed_keywords, list) and
                        isinstance(parsed_distances, list) and
                        len(parsed_keywords) == len(parsed_distances)):
                    for kw, dist in zip(parsed_keywords, parsed_distances):
                        grouped[key].add((kw.strip(), float(dist)))
                else:
                    dist_val = float(distance) if distance else 1.0
                    for kw in parsed_keywords:
                        grouped[key].add((kw.strip(), dist_val))

        results = [
            {
                "text": chunk_text,
                "page": page_number,
                "keywords": [[kw, round(dist, 4)] for kw, dist in sorted(keywords)]
            }
            for (chunk_text, page_number), keywords in grouped.items()
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
        logger.info(f"Fetching filenames and keywords for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT file_name, keyword, scanned, distance
                       FROM file_chunks
                       WHERE project_name = ?
                       ''', (project_name,))

        rows = cursor.fetchall()
        conn.close()

        grouped = {}

        for file_name, keyword, scanned, distance in rows:
            if file_name not in grouped:
                grouped[file_name] = set()

            if scanned == 0:
                # No keywords
                continue
            else:
                if keyword and keyword.strip() != "":
                    try:
                        # Parse keyword string into list
                        parsed_keywords = ast.literal_eval(keyword)
                    except Exception as e:
                        logger.warning(f"Failed to parse keyword: {keyword}, error: {e}")
                        parsed_keywords = [keyword.strip()]  # fallback

                    try:
                        # Parse distance, might be list or float string
                        parsed_distances = ast.literal_eval(distance) if distance else None
                    except Exception as e:
                        logger.warning(f"Failed to parse distance: {distance}, error: {e}")
                        parsed_distances = None

                    if (isinstance(parsed_keywords, list) and
                            isinstance(parsed_distances, list) and
                            len(parsed_keywords) == len(parsed_distances)):
                        for kw, dist in zip(parsed_keywords, parsed_distances):
                            grouped[file_name].add((kw.strip(), float(dist)))
                    else:
                        # Distance is single float or None, assign to all keywords
                        dist_val = float(distance) if distance else 1.0
                        for kw in parsed_keywords:
                            grouped[file_name].add((kw.strip(), dist_val))

        results = []
        for file_name, keyword_set in grouped.items():
            formatted_keywords = [[kw, round(score, 4)] for kw, score in keyword_set]
            results.append({
                "Document Name": file_name,
                "Keywords": formatted_keywords
            })

        logger.info(f"Fetched {len(results)} results for project: {project_name}")
        return results
    

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

    def get_project_time_and_status(self, project_name):
        logger.info(f"Checking upload time and scan status for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get one upload_date (for example, the earliest upload_date for the project)
        cursor.execute("""
            SELECT MIN(upload_date)
            FROM file_chunks
            WHERE project_name = ?
        """, (project_name,))
        upload_date_row = cursor.fetchone()
        upload_date = upload_date_row[0] if upload_date_row else None

        # Check if any file chunk in the project is not scanned (scanned == 0)
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM file_chunks WHERE project_name = ? AND scanned = 0
            )
        """, (project_name,))
        any_not_scanned_row = cursor.fetchone()
        any_not_scanned = bool(any_not_scanned_row[0]) if any_not_scanned_row else False
        conn.close()
        # Project scanned status: True if all scanned, False if any not scanned
        project_scanned = not any_not_scanned
        logger.info(f"Project '{project_name}' upload date: {upload_date}, scanned status: {project_scanned}")
        return upload_date, project_scanned

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
            FROM file_chunks WHERE project_name = ? AND scanned == 0
        ''', (project_name,))
        rows = cursor.fetchall()
        conn.close()
        embeddings = [(chunk_id, np.frombuffer(embedding_blob, dtype=np.float32)) for chunk_id, embedding_blob in rows]
        return embeddings

    def get_all_retrieved_keywords_and_distances_by_project(self, project_name):
        logger.info(f"Getting separate keyword and distance lists for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT DISTINCT keyword, distance
                       FROM file_chunks
                       WHERE project_name = ?
                         AND keyword IS NOT NULL
                         AND keyword != ''
                         AND distance IS NOT NULL
                         AND distance != ''
                       """, (project_name,))
        rows = cursor.fetchall()
        conn.close()

        keywords_list = []
        distances_list = []

        seen = set()

        for keyword_str, distance_str in rows:
            try:
                keywords = ast.literal_eval(keyword_str)
                distances = ast.literal_eval(distance_str)
            except Exception as e:
                logger.warning(f"Skipping row due to parsing error: {e}")
                continue

            if isinstance(keywords, list) and isinstance(distances, list) and len(keywords) == len(distances):
                for word, score in zip(keywords, distances):
                    word = word.strip()
                    if word not in seen:
                        seen.add(word)
                        keywords_list.append(word)
                        distances_list.append(float(score))

        return keywords_list, distances_list

    def get_all_retrieved_keywords_by_project(self, project_name):
        logger.info(f"Getting keywords for project: {project_name}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT DISTINCT keyword
                       FROM file_chunks
                       WHERE project_name = ?
                         AND keyword IS NOT NULL
                         AND keyword != ''
                       """, (project_name,))
        rows = cursor.fetchall()
        conn.close()
        keywords_found = [row[0].strip() for row in rows if row[0] and row[0].strip()]

        all_words = []

        for item in keywords_found:
            # Safely parse the string to a list object
            words_list = ast.literal_eval(item)
            # Clean each word and extend all_words
            cleaned_words = [word.strip() for word in words_list]
            all_words.extend(cleaned_words)

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in all_words:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        return unique_keywords

    def add_exact_keyword_matches_to_chunks(self, keyword: str, project_name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT chunk_id, chunk_text, keyword, distance 
                       FROM file_chunks
                       WHERE project_name = ? 
                       """, (project_name,))
        rows = cursor.fetchall()

        for chunk_id, text, keyword_str, distance_str in rows:
            if keyword.lower() in text.lower():  # Case-insensitive match

                # Parse existing keywords
                try:
                    keywords = ast.literal_eval(keyword_str) if keyword_str else []
                except Exception:
                    keywords = []
                if not isinstance(keywords, list):
                    keywords = [keywords]

                # Parse existing distances
                try:
                    distances = ast.literal_eval(distance_str) if distance_str else []
                except Exception:
                    distances = []
                if not isinstance(distances, list):
                    distances = [distances]

                # Only append if the keyword is not already in the list
                if keyword not in keywords:
                    keywords.append(keyword)
                    distances.append(0.99)  # Use 0.99 to indicate exact match

                    cursor.execute('''
                                   UPDATE file_chunks
                                   SET keyword  = ?,
                                       distance = ?
                                   WHERE chunk_id = ?
                                   ''', (str(keywords), str(distances), chunk_id))

        conn.commit()
        conn.close()
        print(f"[INFO] Exact keyword '{keyword}' added to matching chunks.")


if __name__ == "__main__":
    db = ChunkDatabase()  # This triggers init_db()
    #results = db.get_filename("test")
    results = db.get_chunks_by_project_and_file("test", "WAVE VSB.pdf")
    from pprint import pprint
    pprint(results)

