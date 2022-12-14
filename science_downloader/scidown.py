# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_core.ipynb.

# %% auto 0
__all__ = ['VOLUME', 'ISSUE', 'base_url', 'issue_url', 'urls_list', 'extract_science_pdf_urls_from_toc_page', 'download_wait',
           'download_pdfs_from_list_of_urls', 'remove_extra_page']

# %% ../00_core.ipynb 3
import requests
from bs4 import BeautifulSoup

def extract_science_pdf_urls_from_toc_page(toc_url, return_dois=False):
    """
    Given a TOC in the form 'https://www.science.org/toc/science//377/6609'
    returns a list of links to every pdf in the page with a DOI.
    if `return_dois`, return a list of DOIs instead of web links
    """
    reqs = requests.get(toc_url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    doi_list = []
    for link in soup.find_all('a'):
        href_link = link.get('href')
        if '/doi/epdf/' in href_link:
            split_link = href_link.split('/')
            #manually extract the DOI from the link
            doi = split_link[-2] + '/' + split_link[-1]
            doi_list.append(doi)

    if return_dois:
        return(doi_list)
    else:
        urls_list = ['https://www.science.org/doi/pdf/'+ doi + '?download=true' for doi in doi_list]
        return(urls_list)

# %% ../00_core.ipynb 4
VOLUME = 377
ISSUE = 6609

base_url = 'https://www.science.org/toc/science' 
issue_url = '/'.join([base_url, str(VOLUME), str(ISSUE)])
print('Issue URL for this volume and issue is:', issue_url)

urls_list = extract_science_pdf_urls_from_toc_page(issue_url)

print('Some links to pdfs in this issue')
urls_list[:3]

# %% ../00_core.ipynb 5
def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    import time
    import os
    
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(2)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            dl_wait = False
            #if any file in list is temporary, wait!
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds

# %% ../00_core.ipynb 6
def download_pdfs_from_list_of_urls(list_of_urls, download_path = '~/Downloads/'):
    """
    Download pdfs from a given list of pdf urls.

    Args
    ----
    list_of_urls : list of str
        A list of string paths to each pdf.
    download_path : str
        Path to where pdfs will be downloaded.

    """
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager

    import os, sys, time
    
    #fix path in case path contains ~
    download_path = os.path.expanduser(download_path)

    if not os.path.isdir(download_path):
        sys.exit('Download path does not exist')

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        "download.default_directory": download_path, #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": False #It will not show PDF directly in chrome
    })
    # options.add_argument("--headless")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    for url in list_of_urls:
        driver.get(url)

    download_wait(download_path, timeout=10, nfiles=len(list_of_urls))
    
    driver.close()

# %% ../00_core.ipynb 7
# Testing how to download 1 pdf file
download_pdfs_from_list_of_urls(urls_list[:4])

# %% ../00_core.ipynb 8
def remove_extra_page(path_to_pdf):
    """
    Removes last page from a pdf
    Saves on top of same pdf
    """
    from PyPDF2 import PdfWriter, PdfReader
    
    infile = PdfReader(path_to_pdf, 'rb')
    output = PdfWriter()

    #loop over all pages except last
    for i in range(len(infile.pages)-1):
        p = infile.pages[i] 
        output.add_page(p)

    with open(path_to_pdf, 'wb') as f:
        output.write(f)
