from rdflib import Dataset, Namespace, Literal
import pandas as pd

file_path = "commodities.trig"
ds = Dataset()
ds.parse(file_path, format="trig")

# Define SKOS namespace
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

data = []
# Iterate over each named graph (context) in the dataset
for ctx in ds.contexts():
    # Iterate over all triples with predicate skos:prefLabel in this context
    for subj, pred, obj in ctx.triples((None, SKOS.prefLabel, None)):
        # Check if the literal's language is Dutch ("nl")
        if isinstance(obj, Literal) and obj.language == "nl":
            word = str(obj).strip()
            synonyms = set()
            # Look for synonyms using skos:altLabel in the same context
            for _, p, syn in ctx.triples((subj, SKOS.altLabel, None)):
                if isinstance(syn, Literal) and syn.language == "nl":
                    synonyms.add(str(syn).strip())
            if synonyms:
                data.append([word, ", ".join(synonyms)])

if not data:
    print("No data extracted. Check RDF structure.")
else:
    print(f"Extracted {len(data)} words with synonyms!")

# Save extracted data as CSV
df = pd.DataFrame(data, columns=["word", "synonyms"])
df.to_csv("formatted_synonyms.csv", index=False)
print("Dataset saved as formatted_synonyms.csv")

"""
 Read the first 50 lines of the file
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()[:50]  # Read first 50 lines

 Print lines to inspect
print("\n".join(lines))
"""
"""
g = Graph()
g.parse(file_path, format="turtle")

# Print a sample of RDF triples
# Check total number of triples
print(f"Loaded {len(g)} triples from the RDF file.")

# Print all unique predicates to understand the file's structure
predicates = set()
for _, pred, _ in g:
    predicates.add(pred)

print("Unique predicates found in the file:")
for i, pred in enumerate(predicates, 1):
    print(f"{i}. {pred}")

# Define SKOS predicates
PREF_LABEL = "http://www.w3.org/2004/02/skos/core#prefLabel"  # Main word
ALT_LABEL = "http://www.w3.org/2004/02/skos/core#altLabel"  # Synonyms
CLOSE_MATCH = "http://www.w3.org/2004/02/skos/core#closeMatch"  # Related words

# Extract data
data = []
for subj, pred, obj in g:
    if pred == PREF_LABEL and "@nl" in obj:  # Only Dutch words
        main_word = str(obj).split("@")[0]  # Remove language tag
        synonyms = set()

        # Find all related words
        for s, p, o in g:
            if s == subj and p in {ALT_LABEL, CLOSE_MATCH} and "@nl" in o:
                synonyms.add(str(o).split("@")[0])

        if synonyms:
            data.append([main_word, ", ".join(synonyms)])

# Convert to DataFrame
df = pd.DataFrame(data, columns=["word", "synonyms"])

# Save to CSV
df.to_csv("formatted_synonyms.csv", index=False)
print("Dataset saved as formatted_synonyms.csv")

df = pd.read_csv("formatted_synonyms.csv")

# Display first few rows
print(df.head())

# Check if the DataFrame is empty
if df.empty:
    print("No data found in the CSV file. Check the extraction process.")
else:
    print(f"Data loaded successfully! {len(df)} rows found.")
"""