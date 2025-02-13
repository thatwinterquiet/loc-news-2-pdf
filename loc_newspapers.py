import os
import requests
from pathlib import Path
from PyPDF2 import PdfMerger

# Example: https://chroniclingamerica.loc.gov/lccn/sn83045462/
print("""Past the newspaper issue url.
Example: https://chroniclingamerica.loc.gov/lccn/sn83045462/
Make sure to leave the final number out of the pasted url. 
""")
base_url = input("What is the url: ")
paper_name = input("What is the paper name: ")
date = input("What is the date (YYYY-MM-DD): ")

def download(url: str):
    if not os.path.exists("temp_news"):
        os.makedirs("temp_news")  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join("temp_news", filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    # else:  # HTTP status code 4XX/5XX
    #     # print("Download failed: status code {}\n{}".format(r.status_code, r.text))
    #     print("Download failed: status code {}\n".format(r.status_code))

    return r.status_code

def multiPage(base_url: str, date: str, paper_name):
    status = 200
    i = 1

    # while i < (max_page):
    while status == 200:
        num = str(i)

        # For Library of Congress
        # Example: https://chroniclingamerica.loc.gov/lccn/sn83045462/1946-09-08/ed-1/seq-1.pdf
        url = base_url + date + "/ed-1/seq-" + num + ".pdf"
        print(url)
        status = download(url)

        # Iterate counters
        i += 1
    
    combine_pdfs(date, paper_name)

def delete_folder(pth):
    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)  # Recursively delete subdirectories
        else:
            sub.unlink()  # Delete individual files
    pth.rmdir()  # Remove the directory itself

def combine_pdfs(date, paper_name):
    root_directory = Path(".")  # The root directory is the directory of the script
    
    # Combines all pdfs in the directory "news_temp"
    pdf_files = list(root_directory.glob("temp_news/*.pdf"))
    merger = PdfMerger()

    for pdf in pdf_files:
        merger.append(pdf)  

    file_name = date + " " + paper_name +  ".pdf"
    merger.write(file_name)
    merger.close()

    # Delete the temp directory and its contents
    temp_directory = Path("temp_news")
    delete_folder(temp_directory)

multiPage(base_url, date, paper_name)
