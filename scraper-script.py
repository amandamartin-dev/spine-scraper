import os
import easyocr
import pandas as pd
import spacy

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_image(image_path):
    """Extract text from an image using EasyOCR."""
    result = reader.readtext(image_path, detail=0)
    text = ' '.join(result)
    print(f"Extracted text from {image_path}: {text}")  # DEBUGGING
    return text


def categorize_text_spacy(text):
    """Categorize text using spaCy's Named Entity Recognition (NER)."""
    doc = nlp(text)
    artist = ""
    album = ""
    
    print(f"Text to categorize: {text}")  # DEBUGGING
    
    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE"}:  # Assuming artists/bands can be PERSON, ORG, or GPE
            if not artist:  # Prioritize the first match as the artist
                artist = ent.text
        elif ent.label_ in {"WORK_OF_ART", "PRODUCT", "EVENT"}:  # Albums might be WORK_OF_ART, PRODUCT, or EVENT
            if not album:  # Prioritize the first match as the album
                album = ent.text
    
    # Fallback rules if NER fails to identify correctly
    if not artist and text:
        lines = text.split('\n')
        if len(lines) > 0:
            artist = lines[0]  # Assume the first line is the artist/band name
        if len(lines) > 1:
            album = lines[1]  # Assume the second line is the album title
    
    print(f"Categorized Artist: {artist}, Album: {album}")  # DEBUG
    
    return artist, album


def process_images_in_directory(directory):
    """Process all images in a directory and return a list of dictionaries with artist and album information."""
    records = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(directory, filename)
            text = extract_text_from_image(image_path)
            artist, album = categorize_text_spacy(text)
            if artist or album:  # Ensure at least one is found
                records.append({'Filename': filename, 'Artist': artist, 'Album': album})
    return records

def save_to_csv(records, output_file):
    """Save the records to a CSV file."""
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)

# Main script
if __name__ == "__main__":
    input_directory = "images"  # Update with the path to your image directory
    output_file = "vinyl_collection.csv"
    
    records = process_images_in_directory(input_directory)
    save_to_csv(records, output_file)
    
    print(f"CSV file '{output_file}' has been created with the vinyl collection data.")
