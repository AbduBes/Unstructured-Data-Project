from io_utils import read_json, setup_logging

if __name__ == "__main__":
    
   setup_logging("pipeline.log")

   book_data = read_json("data/raw/book_1.json")


   if book_data:
       print("Book title:", book_data["title"])