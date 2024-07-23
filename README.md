# spine-scraper
This is a python script to utilize ocr and the spacy model to extract artist and album names from images into a csv

## Required imports

```pip install easyocr pillow numpy```

## Notes

This is a personal project and is currently a work in progress.  
To test, take a clear and high contrast image of album spines. Reccomend no more than a few at this current iteration.

This script will attempt to treat each album as one line and extract the text from the image.
Then it will attempt to classify the resultiing text into Artist and Album.
It works with limited accuracy at the moment.

