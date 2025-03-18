from transformers import pipeline

generator = pipeline('text-generation', model='ml6team/mt5-small-nl', device_map="auto")

def generate_related_terms(keyword):
    """
    Generate related words
    """

    prompt = f"Geef alleen een lijst met synoniemen en gerelateerde termen voor '{keyword}', gescheiden door komma's."
    output = generator(prompt, max_length=100, truncation=True, num_return_sequences=1)

    print("Raw output:", output)

    generated_text = output[0]['generated_text']

    # Extract list of related terms
    if ":" in generated_text:
        related_terms = generated_text.split(":")[1].strip().split(",")
        related_terms = [term.strip() for term in related_terms]
    else:
        related_terms = [generated_text.strip()]

    return related_terms
