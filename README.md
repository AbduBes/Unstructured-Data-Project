# Unstructured-Data-Project


## Project: Multi-Source Unstructured Literature Analysis

Project Idea

The **Literary Intelligence Pipeline** is an unstructured data project designed to extract, analyze, and compare thematic patterns between classic literature and modern critical discourse.
By processing raw text from public domain novels and semi-structured academic reviews, the project aims to identify "sentiment drift"—how the emotional perception of a book's themes has changed from its publication date to modern-day analysis.Data Sources

To ensure a robust analysis of unstructured data, this project utilizes:

* **Project Gutenberg:** A repository of over 70,000 free eBooks. We will extract raw `.txt` files of classic novels (e.g., *Pride and Prejudice*, *Moby Dick*).
* **Goodreads API / Open Library:** To fetch modern user-generated reviews and unstructured critical metadata to compare historical text against contemporary reception.

Data Types Handled

* **Unstructured Text:** Full-length novel chapters, prose, and dialogue.
* **Semi-Structured JSON:** API responses containing book metadata, ratings, and timestamped reviews.
* **Sequential Data:** Time-series sentiment scores extracted from the text.

Pipeline Architecture

The following diagram illustrates the flow from raw data ingestion to the final analytical dashboard.

Expected Challenges

* **Language Evolution:** Classic literature often uses archaic vocabulary and syntax that standard NLP libraries (like SpaCy or NLTK) may misclassify during Sentiment Analysis or POS (Part-of-Speech) tagging.
* **Data Volume & Cleaning:** Handling full-length novels requires significant memory management. Cleaning "OCR noise" (transcription errors) from older digital copies is essential for accuracy.
* **Sarcasm & Context:** Literary devices like irony or unreliable narrators are notoriously difficult for machine learning models to interpret correctly without deep contextual embeddings.

---
Success Criteria

The project will be considered successful if it meets the following benchmarks:

* **Accuracy:** Achieve at least **80% agreement** between the model’s thematic extraction and established literary benchmarks (e.g., SparkNotes or CliffsNotes themes).
* **Performance:** The pipeline can process a 100,000-word novel (ingestion to visualization) in under **60 seconds**.
* **Insight:** Successfully identify at least three significant "Sentiment Shifts" where modern reviews differ emotionally from the book's internal narrative tone.


sample_1.jpeg:
ImageWidth: 3072
ImageLength: 4080
GPSInfo: 3116
ResolutionUnit: 2
ExifOffset: 211
Make: Xiaomi
Model: 2201117TY
DateTime: 2025:09:29 12:44:54
Orientation: 1
YCbCrPositioning: 1
XResolution: 72.0
YResolution: 72.0
{
  "camera_make": "Xiaomi",
  "camera_model": "2201117TY",
  "date_taken": "2025:09:29 12:44:54",
  "exposure": "None",
  "aperture": "None",
  "iso": null,
  "focal_length": "None",
  "orientation": 1,
  "gps": {
    "GPSLatitudeRef": "\u0000",
    "GPSLatitude": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSLongitudeRef": "\u0000",
    "GPSLongitude": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSAltitudeRef": "b'\\x00'",
    "GPSAltitude": "nan",
    "GPSTimeStamp": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSProcessingMethod": "b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'",
    "GPSDateStamp": "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
  }
}


sample_2.jpeg:
GPSInfo: 1341
ExifOffset: 123
Make: Xiaomi
Model: 2201117TY
Orientation: 1
DateTime: 2026:04:01 02:55:51
{
  "camera_make": "Xiaomi",
  "camera_model": "2201117TY",
  "date_taken": "2026:04:01 02:55:51",
  "exposure": "None",
  "aperture": "None",
  "iso": null,
  "focal_length": "None",
  "orientation": 1,
  "gps": {
    "GPSLatitudeRef": "\u0000",
    "GPSLatitude": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSLongitudeRef": "\u0000",
    "GPSLongitude": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSTimeStamp": [
      "nan",
      "nan",
      "nan"
    ],
    "GPSDateStamp": "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
  }
}
