import numpy as np
import os
from pathlib import Path
from datetime import datetime,timedelta
from zipfile import ZipFile
from glob import glob
from spacetrack import SpaceTrackClient
from colorama import Fore
from time import sleep

from .try_download import wget_download

def download_satcat():
    """
    Download or update the satellite catalog CSV file from www.celestrak.com.
    This function checks whether the local satellite catalog exists and is up to date (within 7 days).
    If not, it downloads the latest version from CelesTrak.
=
    Returns:
        scfile -> [str] Path of the downloaded (or already up-to-date) satellite catalog CSV file.

    Notes:
        - Catalog is saved by default in '~/src/satcat-data/satcat.csv'.
        - File is refreshed if older than 7 days.
    """
    home = str(Path.home())
    direc = os.path.join(home, 'src/satcat-data')
    scfile = os.path.join(direc, 'satcat.csv')
    url = 'https://celestrak.com/pub/satcat.csv'

    os.makedirs(direc, exist_ok=True)
    if not os.path.exists(scfile):
        desc = 'Downloading the latest satellite catalog from CelesTrak'
        wget_out = wget_download(url,scfile,desc)
    else:
        modified_time = datetime.fromtimestamp(os.path.getmtime(scfile))
        if datetime.now() > modified_time + timedelta(days=7):
            os.remove(scfile)
            desc = 'Updating the satellite catalog from CELESTRAK'
            wget_out = wget_download(url,scfile,desc) 
        else:
            print(f'The satellite catalog in {direc} is already the latest.')
    return scfile

def download_qsmag():
    """
    Download or update the QS.MAG file (standard/intrinsic magnitudes for space objects) from https://www.mmccants.org/programs/qsmag.zip.
    The function checks whether the local qs.mag file exists and is up to date (within 180 days).
    If not, it downloads and extracts the latest archive.

    Returns:
        qsfile -> [str] Path to the extracted qs.mag file.
    Notes:
        - Data is saved by default in '~/src/satcat-data/qs.mag'.
        - File is refreshed if older than 180 days.
    """
    home = str(Path.home())
    direc = os.path.join(home, 'src/satcat-data/')
    qsfile_zip = os.path.join(direc, 'qsmag.zip')
    qsfile = os.path.join(direc, 'qs.mag')
    url = 'https://www.mmccants.org/programs/qsmag.zip'

    os.makedirs(direc, exist_ok=True)
    if not os.path.exists(qsfile):
        desc = 'Downloading the latest qs.mag data from Mike McCants Satellite Tracking Web Pages'
        wget_out = wget_download(url,qsfile_zip,desc)
    else:
        modified_time = datetime.fromtimestamp(os.path.getmtime(qsfile))
        if datetime.now() > modified_time + timedelta(days=180):
            os.remove(qsfile)
            desc = 'Updating the qs.mag data from Mike McCants Satellite Tracking Web Pages'
            wget_out = wget_download(url,qsfile_zip,desc) 
        else:
            print(f'The qs.mag data in {direc} is already the latest.')

    if os.path.exists(qsfile_zip):
        # Unzip qsmag file
        with ZipFile(qsfile_zip, 'r') as zip_ref:
            zip_ref.extractall(direc)
        os.remove(qsfile_zip)

    return qsfile

def download_tle1(noradids,mode='keep',dir_TLE='TLE/'):
    """
    Download the TLE/3LE data from [SPACETRACK](https://www.space-track.org) automatically

    Usage: 
        tle_file = tle_download(noradids)
        tle_file = tle_download(noradids,'clear')
        tle_file = tle_download('satno.txt')

    Inputs:
        noradids -> [str, int, list of str/int] NORADID of space targets. 
        It can be a single NORADID, list of NORADID, or a file containing a set of NORADID.
        The form and format of the file is as follows:
        #satno
        12345
        23469
        ...

        mode -> [str,optional,default='keep'] Either 'keep' the files stored in TLE directory or 'clear' the TLE directory 
        dir_TLE -> [str,optional,default='TLE/'] Path to save TLE

    Outputs: 
        tle_file  -> [str] Path of TLE/3LE file.
    """
    # Check whether a list is empty or not
    if not noradids: raise Exception('noradids is empty.')

    if type(noradids) is list:
        if type(noradids[0]) is int: noradids = [str(i) for i in noradids]    
    else:
        noradids = str(noradids)
        if '.' in noradids: # noradids as a file
            noradids = list(set(np.loadtxt(noradids,dtype=str)))
        else:
            noradids = [noradids]    
    
    # Set the maximum of requested URL's length with a single access 
    # The setup prevents exceeding the capacity limit of the server
    n = 500
    noradids_parts = [noradids[i:i + n] for i in range(0, len(noradids), n)]  
    part_num = len(noradids_parts)    
    
    # username and password for Space-Track
    home = str(Path.home())
    direc = home + '/src/spacetrack-data/'
    loginfile = direc + 'spacetrack-login'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(loginfile):
        username = input('Please input the username for Space-Track(which can be created at https://www.space-track.org/auth/login): ')
        password = input('Please input the password for Space-Track: ')
        outfile = open(loginfile,'w')
        for element in [username,password]:
            outfile.write('{:s}\n'.format(element))
        outfile.close()
    else:
        infile = open(loginfile,'r')
        username = infile.readline().strip()
        password = infile.readline().strip()
        infile.close()
    
    # save TLE data to files  
    fileList_TLE = glob(dir_TLE+'*')
    if path.exists(dir_TLE):
        if mode == 'clear':
            for file in fileList_TLE:
                remove(file)
    else:
        makedirs(dir_TLE) 

    valid_ids,j = [],1
    date_str = datetime.utcnow().strftime("%Y%m%d")
    filename_tle = dir_TLE + 'tle_{:s}.txt'.format(date_str)
    file_tle = open(filename_tle,'w')  

    st = SpaceTrackClient(username, password)
    for part in noradids_parts:
        desc = 'Downloading TLE data: Part {:s}{:2d}{:s} of {:2d}'.format(Fore.BLUE,j,Fore.RESET,part_num)
        print(desc,end='\r')

        try:
            lines_tle = st.tle_latest(norad_cat_id=part,ordinal=1,iter_lines=True,format='tle')  
        except:       
            remove(loginfile)
            raise ConnectionError("401 Unauthorized: username or password entered incorrectly!")      

        for line in lines_tle:
            words = line.split()
            if words[0] == '2': valid_ids.append(words[1].lstrip('0'))
            file_tle.write(line+'\n')
        sleep(j+5) 
        j += 1   
    file_tle.close()
    print()

    missed_ids = list(set(noradids)-set(valid_ids))
    if missed_ids: 
        missed_ids_filename = dir_TLE + 'missed_ids_{:s}.txt'.format(date_str)
        desc = '{:s}Note: space objects with unavailable TLE are stored in {:s}.{:s} '.format(Fore.RED,missed_ids_filename,Fore.RESET)
        print(desc) 
        np.savetxt(missed_ids_filename,missed_ids,fmt='%s')

    return filename_tle

def _prepare_noradids(noradids):
    """
    Normalize and validate NORAD IDs.
    """
    if isinstance(noradids, list):
        if isinstance(noradids[0], int):
            noradids = [str(i) for i in noradids]
    else:
        noradids = str(noradids)
        if '.' in noradids:  # NORAD IDs provided as a file
            noradids = list(set(np.loadtxt(noradids, dtype=str)))
        else:
            noradids = [noradids]

    return noradids

def _prepare_tle_directory(dir_TLE, mode):
    """
    Handle the preparation of the TLE directory.
    """
    if not os.path.exists(dir_TLE):
        os.makedirs(dir_TLE)
    elif mode == 'clear':
        for file in glob(f"{dir_TLE}*"):
            os.remove(file)

def _get_spacetrack_credentials():
    """
    Retrieve for Space-Track credentials.
    """
    direc = os.path.join(Path.home(),"src/spacetrack-data")
    loginfile = os.path.join(direc,'spacetrack-login')

    os.makedirs(direc, exist_ok=True)

    if not os.path.exists(loginfile):
        username = input("Enter Space-Track username (create one at https://www.space-track.org/auth/login): ")
        password = input("Enter Space-Track password: ")
        with open(loginfile, 'w') as outfile:
            outfile.write(f"{username}\n{password}\n")
    else:
        with open(loginfile, 'r') as infile:
            username = infile.readline().strip()
            password = infile.readline().strip()

    return username, password

def download_tle(noradids, mode='keep', dir_TLE='TLE'):
    """
    Download TLE files from [SPACETRACK](https://www.space-track.org).

    Usage:
        >>> tlefile = TLE.download(noradids)
        >>> tlefile = TLE.download(noradids, mode='clear')
        >>> tlefile = TLE.download('satno.txt')
    Inputs:
        noradids -> [str, int, or list of str/int] NORAD IDs of space objects. Can be:
            - A single NORAD ID (str or int),
            - A list of NORAD IDs (str or int),
            - A filename (str) containing a set of NORAD IDs (one per line).
        mode -> [str, optional, default='keep']
            - 'keep': Retain existing files in the TLE directory.
            - 'clear': Remove existing files in the TLE directory before downloading.
        dir_TLE -> [str, optional, default='TLE'] Directory to store the TLE files.
    Returns:
        tlefile -> [str] Path to the downloaded TLE file.
    Outputs：
        The downloaded TLE file.
    Raises:
        ConnectionError: If Space-Track login credentials are invalid.
    """
    # Validate and normalize input NORAD IDs
    noradids = _prepare_noradids(noradids)

    # Handle the TLE directory
    _prepare_tle_directory(dir_TLE, mode)

    # Authenticate with Space-Track
    username, password = _get_spacetrack_credentials()

    # Divide NORAD IDs into manageable parts
    n = 500
    # Reason: The Space-Track API imposes limits on the amount of data that can be requested in a single query.
    # If too much data is requested at once, the API may respond with a "rate limit exceeded" or "request overload" error,
    # and the website will temporarily block further requests until the timeout period (usually a few minutes) has passed.
    # To prevent hitting these limits:
    # 1. Splits the NORAD IDs into chunks of manageable size (default n=500) to stay within the allowed limits.
    # 2. Introduces an incremental pause duration after processing each chunk to reduce the frequency of requests and allow the server to reset its rate limit.
    # This approach ensures that all requested data can be downloaded efficiently without triggering server protections.
    noradids_parts = [noradids[i:i + n] for i in range(0, len(noradids), n)]
    part_num = len(noradids_parts)

    # Prepare output TLE file
    date_str = datetime.utcnow().strftime("%Y%m%d")
    tlefile = os.path.join(dir_TLE, f"tle_{date_str}.txt")
    valid_ids = []

    with open(tlefile, 'w') as file_tle:
        st = SpaceTrackClient(username, password)

        for j, part in enumerate(noradids_parts, start=1):
            desc = f"Downloading TLE data: Part {Fore.BLUE}{j}{Fore.RESET} of {part_num}"
            print(desc, end='\r')

            try:
                lines_tle = st.tle_latest(norad_cat_id=part, ordinal=1, iter_lines=True, format='tle')
            except:
                direc = os.path.join(Path.home(), "src/spacetrack-data")
                loginfile = os.path.join(direc, 'spacetrack-login')
                os.remove(loginfile)
                raise ConnectionError("401 Unauthorized: Incorrect username or password!")

            for line in lines_tle:
                words = line.split()
                if words[0] == '2':
                    valid_ids.append(words[1].lstrip('0'))
                file_tle.write(line + '\n')
            sleep(j + 5)

    # Handle missing NORAD IDs
    missed_ids = list(set(noradids) - set(valid_ids))
    if missed_ids:
        missed_ids_filename = os.path.join(dir_TLE, f"missed_ids_{date_str}.txt")
        print(f"{Fore.RED}Note: Missing NORAD IDs are stored in {missed_ids_filename}.{Fore.RESET}")
        np.savetxt(missed_ids_filename, missed_ids, fmt='%s')

    return tlefile