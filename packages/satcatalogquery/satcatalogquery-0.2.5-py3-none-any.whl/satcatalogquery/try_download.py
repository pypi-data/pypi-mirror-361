import wget

def wget_download(url, dir_file, desc=None):
    """
    Download a file from a given URL and save it to a specified location using the wget library.

    Inputs:
        url -> [str] URL of the file to be downloaded.
        dir_file -> [str] Full path where the file should be saved.
        desc -> [str, optional, default=None] Optional description to print before starting the download.
    Returns:
        wget_out -> [str] Path of the downloaded file (should be the same as dir_file).
    """
    if desc: print(desc)
    wget_out = wget.download(url, dir_file)
    print()  # Ensure newline after wget progress bar
    return wget_out