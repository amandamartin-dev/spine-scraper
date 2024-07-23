import os
import csv
import re
import easyocr
import numpy as np
from PIL import Image

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def extract_text_from_image(image_path):
    """Extract text from an image using EasyOCR, treating each spine as a single line."""
    image = Image.open(image_path)
    result = reader.readtext(np.array(image))
    
    if not result:
        print(f"No text detected in {image_path}")
        return ""

    # Sort detections by y-coordinate (top to bottom)
    sorted_result = sorted(result, key=lambda x: x[0][0][1])

    lines = []
    current_line = []
    prev_y = None
    y_threshold = image.size[1] * 0.03  # 3% of image height

    for detection in sorted_result:
        bbox, text, conf = detection
        current_y = (bbox[0][1] + bbox[2][1]) / 2  # Middle y-coordinate

        if prev_y is None or abs(current_y - prev_y) > y_threshold:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [text]
        else:
            current_line.append(text)

        prev_y = current_y

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

def categorize_text(text):
    """Categorize text into artist and album."""
    lines = text.split('\n')
    results = []

    for line in lines:
        print(f"Line to categorize: {line}")  # DEBUGGING
        
        # Try to split based on common separators or multiple spaces
        parts = re.split(r'\s{2,}|:|-', line, 1)
        
        if len(parts) >= 2:
            artist = parts[0].strip()
            album = parts[1].strip()
        else:
            # If we can't split, use more sophisticated heuristics
            words = line.split()
            if len(words) > 2:
                # Assume last half is the album title
                mid = len(words) // 2
                artist = ' '.join(words[:mid])
                album = ' '.join(words[mid:])
            else:
                artist = line
                album = ""

        # Handle special cases
        if "PRESENTS:" in line:
            artist, album = line.split("PRESENTS:", 1)
            artist = artist.strip()
            album = "PRESENTS: " + album.strip()

        print(f"Categorized Artist: {artist}, Album: {album}")  # DEBUG
        results.append((artist, album))
    
    return results

def process_image(image_path):
    """Process a single image and return results."""
    text = extract_text_from_image(image_path)
    return categorize_text(text)

def write_to_csv(all_results, output_file):
    """Write all results to a single CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image', 'Artist', 'Album'])  # Header
        for image, results in all_results:
            for artist, album in results:
                writer.writerow([image, artist, album])
    print(f"Results written to {output_file}")

def process_folder(folder_path, output_file):
    """Process all images in a folder and write results to CSV."""
    all_results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing {image_path}")
            results = process_image(image_path)
            print(f"Results for {filename}: {results}")  # Debug print
            all_results.append((filename, results))
    
    print(f"Total images processed: {len(all_results)}")  # Debug print
    for image, results in all_results:
        print(f"{image}: {len(results)} results")  # Debug print
    
    write_to_csv(all_results, output_file)

# Main execution
if __name__ == "__main__":
    folder_path = "path/to/your/image/folder"  # Replace with your folder path
    output_file = "album_data.csv"  # Replace with your desired output file name
    process_folder(folder_path, output_file)
