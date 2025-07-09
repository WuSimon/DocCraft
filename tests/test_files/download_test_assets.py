import os
import urllib.request

TEST_FILES_DIR = os.path.dirname(__file__)

def download_w3c_dummy_pdf():
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    path = os.path.join(TEST_FILES_DIR, "dummy.pdf")
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
    return path

def download_tesseract_phototest_tif():
    url = "https://github.com/tesseract-ocr/tesseract/raw/main/doc/images/phototest.tif"
    path = os.path.join(TEST_FILES_DIR, "phototest.tif")
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
    return path

if __name__ == "__main__":
    download_w3c_dummy_pdf()
    download_tesseract_phototest_tif()
    print("Test assets downloaded.") 