import logging
import os
import pickle
from backend_filepro import FileHandler
from document_pro import DocHandler, ProjectHandler


def main():
    upload_folder = "uploads"
    project_name = "my_ass"
    global handler

    doc_handler = DocHandler(project_name, upload_folder)  # Initialize the document handler with the project name
    doc_handler.process_files()  # Process all files in the upload folder
    
    file_names = [doc.get_path_name() for doc in doc_handler.get_documents()]
    handler = FileHandler(file_names)


    results = handler.process_all_files()  # Process all files in the upload folder

    print(results)  # Get the results

    handler.set_project_name(project_name)  # Set the project name

    print(f"Project name: {handler.get_project_name()}")  # Get the project name

if __name__ == "__main__":
    main()