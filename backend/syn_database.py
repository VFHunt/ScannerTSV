import json 
import os


class DataHandler:
    def __init__(self, filepath):
        print("...")
        self.filepath = filepath
        # Load database if exists, else initialize empty
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                print("Data base loaded correctly")
        else:
            self.data = {}
            print("Database successfully created")

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_synonyms(self, word):
        return self.data.get(word, [])

    def add_synonyms(self, word, synonyms):
        if word not in self.data:
            self.data[word] = []
        # Only add if not already present
        for syn in synonyms:
            if syn not in self.data[word]:
                self.data[word].append(syn)
        self.save()
        print(f"Synonyms for '{word}' updated: {self.data[word]}")

    def is_saved(self, word):
        if word in self.data:
            print("This keyword is saved in the database from " + self.filepath)
            return 1
        else:
            print("This keyword is not saved in the datbase from " + self.filepath)
            print("The generative model will give us the synonyms needed")
            return 0