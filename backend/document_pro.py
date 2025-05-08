from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import fitz
import os
import re
import pandas as pd

# Use a multilingual model that works well with Dutch
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
kw_model = KeyBERT(model)


class Doc:
    def __init__(self, document):
        # Initialize private variables
        print("Initializing document named: ", str(document))
        self.__name = str(document)
        self.path_name = "uploads/" + self.__name
        self.__text = self.extract_text_from_pdf()
        self.__all_words = self.__extract_words()  # Changed from __extract_keywords to __extract_words
        self.__match_keywords = None
        self.__status = None
        self.__last_scan = None
        self.__df_matches = None

    def get_df_matches(self):
        return self.__df_matches
    
    def set_df_matches(self, df_matches):
        self.__df_matches = df_matches

    def get_text(self):
        return self.__text

    # Getter for name
    def get_name(self):
        return self.__name

    # Setter for name
    def set_name(self, name):
        self.__name = name

    # Getter for match_keywords
    def get_match_keywords(self):
        return self.__match_keywords

    # Setter for match_keywords
    def set_match_keywords(self, match_keywords):
        self.__match_keywords = match_keywords

    # Getter for status
    def get_status(self):
        return self.__status

    # Setter for status
    def set_status(self, status):
        self.__status = status

    # Getter for last_scan
    def get_last_scan(self):
        return self.__last_scan

    # Setter for last_scan
    def set_last_scan(self, last_scan):
        self.__last_scan = last_scan

    # Getter for all_words (formerly all_keywords)
    def get_all_words(self):
        return self.__all_words

    # Setter for all_words (formerly all_keywords)
    def set_all_words(self, all_words):
        self.__all_words = all_words

    # Method to display document details
    def display_details(self):
        return {
            "Document Name": self.__name,
            "Extracted Text": self.__text if self.__text else "No text extracted",
            "Matched Keywords": self.__match_keywords if self.__match_keywords else "No matched keywords",
            "Status": self.__status if self.__status else "Status not set",
            "Last Scan": self.__last_scan if self.__last_scan else "Not scanned yet",
            "All Extracted Words": self.__all_words if self.__all_words else "No words extracted",
        }

    def extract_text_from_pdf(self): # todo: look at 
        print("Extracting text from PDF...")
        all_text = ""  # Initialize the variable as an empty string
        try:
            doc = fitz.open(self.path_name)
            for page in doc:
                page_text = page.get_text()  # Extract text from the page
                all_text += page_text.replace("\n", " ")  # Replace newlines with spaces
            doc.close()  # Close the document after processing
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return all_text
    
    def text_splitter(self):
        """
        Split the text into smaller chunks of 2–3 sentences.
        """
        print("Splitting text into smaller chunks...")
        try:
            # Use a regular expression to split the text into sentences
            sentences = re.split(r'(?<=[.!?]) +', self.__text)

            # Group sentences into chunks of 2–3 sentences
            chunks = []
            for i in range(0, len(sentences), 2):  # Step by 2 sentences
                chunk = " ".join(sentences[i:i + 2])  # Combine 2–3 sentences into a chunk
                chunks.append(chunk)

            return chunks
        except Exception as e:
            print(f"Error splitting text: {e}")
            return []

    def __extract_words(self):  # Changed from __extract_keywords to __extract_words
        print("Extracting words...")
        word_count = len(self.__text.split())  # Split the text into words and count them
        # Calculate the top_n value as 70% of the total word count
        top_n = round(0.7 * word_count)
        keywords = kw_model.extract_keywords(self.__text, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=top_n)
        print("document pro file: ", keywords)
        return keywords
    
    def which_keywords_in_text(self, keywords):
        """
        Check if the keywords is present in the extracted text.
        """
        all_words = [keyword[0] for keyword in self.get_all_words()]
        matched_keywords = [keyword for keyword in keywords if keyword in all_words]
        self.set_match_keywords(matched_keywords)  # Set the matched keywords
         
        return matched_keywords

    def which_splits(self): # todo: el problema must be here
        """
        Check which splits contain the keywords and return a DataFrame with:
        - The split (chunk of text)
        - The matching keywords
        - Their corresponding cosine similarity values
        """
        matched_splits = []  # List to store results
        matched = self.get_match_keywords()  # Get matched keywords from text
        chunk_match = []

        print("Checking which splits contain the keywords...")
        for chunk in self.text_splitter():
            print(f" -------------- Checking chunk: {chunk}")
            chunk_match = []
            flag = False  # Flag to check if any keyword is found in the chunk
            # Find keywords that are in the current chunk
            for match in matched: 
                if match in chunk:
                    print(f" ------------- Keyword '{match}' found in chunk: {chunk}")
                    chunk_match.append(match)
                    flag = True

            if flag:
                # Add the chunk and matching keywords to the results
                matched_splits.append({
                    "Document Name": self.get_name(),
                    "Split": chunk,
                    "Matching Keywords": [kw for kw in chunk_match],  # Extract keywords
                })

        # Convert the results to a pandas DataFrame
        # 
        df = pd.DataFrame(matched_splits)
        self.set_df_matches(df)  # Set the DataFrame as an instance variable
            
class DocHandler:
    def __init__(self, upload_path):
        # Initialize private variables
        self.__upload_folder = upload_path  # Path to the upload folder
        self.__documents = []  # List to store all Doc objects
        self.__keywords_per_doc = None

        
    def get_keywords_per_doc(self):
        return self.__keywords_per_doc
    
    def set_keywords_per_doc(self, keywords_per_doc):
        self.__keywords_per_doc = keywords_per_doc

    def process_files(self):
        """
        Process all files in the upload folder by creating Doc objects.
        """
        try:
            # List all files in the upload folder
            for filename in os.listdir(self.__upload_folder):
                file_path = os.path.join(self.__upload_folder, filename)

                if any(doc.get_name() == filename for doc in self.__documents): # todo: check this works
                    print(f"File '{filename}' is already processed. Skipping...")
                    continue

                # Check if it's a file
                if os.path.isfile(file_path):
                    print(f"Processing file: {filename}")
                    # Create a Doc object and add it to the documents list
                    doc = Doc(filename)
                    self.__documents.append(doc)
        except Exception as e:
            print(f"Error processing files: {e}")

    def get_doc(self, name):
        """
        Get a specific Doc object by its name.
        """
        for doc in self.__documents:
            if doc.get_name() == name:
                return doc
        return None

    def get_documents(self):
        """
        Get the list of all processed Doc objects.
        """
        return self.__documents

    def display_all_documents(self):
        """
        Display details of all processed documents.
        """
        for doc in self.__documents:
            print(doc.get_name())

    def keywords_in_documents(self, keywords):
        """
        Save the keywords related to each document name in a pandas DataFrame.
        Returns a DataFrame with two columns: 'Document Name' and 'Keywords'.
        """
        document_keywords = []  # List to store document names and their keywords

        for doc in self.__documents:
            # Set the matched keywords for the document
            doc.which_keywords_in_text(keywords)

            # Append the document name and matched keywords to the list
            document_keywords.append({
                "Document Name": doc.get_name(),
                "Keywords": doc.get_match_keywords()
            })

        # Convert the list to a pandas DataFrame
        df = pd.DataFrame(document_keywords, columns=["Document Name", "Keywords"])

        self.set_keywords_per_doc(df)  # Set the DataFrame as an instance variable

        # Print the DataFrame for debugging
        print("\nGenerated DataFrame:")
        print(df)

        return df
    
class MaxProjectsReachedError(Exception):
    """Custom exception raised when too many projects are added."""
    pass

class ProjectHandler:
    def __init__(self, name, max_projects=10):
        # Initialize private variables
        self.__name = name  # Project name
        self.__projects = []  # List to store all Doc objects
        self.__max_projects = max_projects  # Maximum number of projects allowed

    def set_projects(self, projects):
        self.__projects = projects

    def get_projects(self):
        return self.__projects
    
    def add_project(self, project: DocHandler):
        if len(self.__projects) == self.__max_projects:
            raise MaxProjectsReachedError("Maximum number of projects reached. Cannot add more.")
        self.__projects.append(project)

    def delete_project(self, project_name):
        """
        Delete a project by its name.
        """
        for project in self.__projects:
            if project.get_name() == project_name:
                self.__projects.remove(project)
                break
    
    def new_max_projects(self, new_max):
        """
        Set a new maximum number of projects allowed.
        """
        self.__max_projects = new_max

# # Initialize the DocHandler with the path to the upload folder
# upload_folder = "uploads"  # Replace with your actual folder path
# handler = DocHandler(upload_folder)

# print("=== Starting File Processing ===")
# handler.process_files()  # Process all files in the upload folder

# print("\n=== Displaying All Processed Documents ===")
# handler.display_all_documents()  # Display the names of all processed documents

# print("\n=== Testing Individual Document ===")
# # Get the list of processed documents
# documents = handler.get_documents()

# if documents:
#     # Test the first document
#     doc = documents[1]
#     print(f"\n--- Document: {doc.get_name()} ---")

#     # Extracted text
#     print("\nExtracted Text:")
#     print(doc.get_text())

#     # Extracted keywords
#     print("\nExtracted Keywords:")
#     print(doc.get_all_words())

#     # Check which keywords are in the text
#     print("\nMatched Keywords in Text:")
#     keywords = ["intelligence", "ai", "cow", "chamber", "discrimination"]
#     matched_keywords = doc.which_keywords_in_text(keywords)
#     print(matched_keywords)

#     # Check which splits contain the keywords
#     print("\nSplits Containing Keywords:")
#     splits_df = doc.which_splits()
#     print(splits_df)
#     splits_df.to_csv("splits_output.csv", index=False)
# else:
#     print("No documents were processed. Please check the upload folder.")