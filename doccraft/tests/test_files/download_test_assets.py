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

def download_benchmark_tiff():
    url = "https://upload.wikimedia.org/wikipedia/commons/8/89/26032u.tif"
    path = os.path.join(TEST_FILES_DIR, "benchmark.tif")
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
    return path

def download_lenna_png():
    url = "https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png"
    path = os.path.join(TEST_FILES_DIR, "lenna.png")
    if not os.path.exists(path):
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
    return path

if __name__ == "__main__":
    download_w3c_dummy_pdf()
    download_benchmark_tiff()
    download_lenna_png()
    print("Test assets downloaded.") 