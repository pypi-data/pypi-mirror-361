import numpy as np
import pandas as pd
import os,requests
from pathlib import Path
from time import sleep
from colorama import Fore

from . import Const
from . import data_prepare

def calculate_hbr(df):
    """
    Calculate the Hard-Body Radius (HBR) for each object in the input DataFrame,
    following the logic used in the NASA CARA MATLAB implementation.

    The HBR is a characteristic size metric that approximates the "radius" of a debris object
    for collision risk analysis, and is defined based on the geometric dimensions and shape of the object.
    The logic applies different formulas depending on shape and the available size parameters.

    Inputs:
        df -> [pandas.DataFrame] Input DataFrame with one row per object, and the following columns:
                - 'SHAPE' (str): Description of object shape (e.g., 'Box', 'Cylinder', 'Sphere', etc.).
                - 'HEIGHT' (float): Height of the object.
                - 'LENGTH' (float): Length of the object (corresponds to Width in some datasets).
                - 'DEPTH' (float): Depth of the object.
                - 'DIAMETER' (float): Diameter (for spherical/cylindrical/conic objects).
                - 'SPAN' (float): Span (for objects with extended features, e.g., solar panels).
            Columns can contain missing values (NaN) if a parameter is not applicable.
    Returns:
        df -> [pandas.DataFrame] The same DataFrame with an additional column 'HBR' containing the computed hard-body radius (in the same units as the input dimensions).

    Notes:
        - The method attempts to use the most comprehensive formula available for each row,
          prioritizing use of all three dimensions plus span when available,
          and falls back to simpler estimates if data is missing.
        - For boxes, if the span is the limiting dimension, the shape is optionally updated to reflect this.
        - For spheres and ellipsoids, HBR is set to half the maximum dimension available.
    """
    HBR = pd.Series(np.nan, index=df.index) # Initialize HBR as NaN for all rows
    df['SHAPE_LOWER'] = df['SHAPE'].str.lower() # Create lower-case version of SHAPE for easier matching

    shape = df['SHAPE_LOWER']
    x = df['LENGTH']
    y = df['HEIGHT']
    z = df['DEPTH']
    diam = df['DIAMETER']
    span = df['SPAN']

    mask_shape_empty = shape.isna() | (shape == '') # Missing or empty shape
    mask_non_sphere = ~shape.str.startswith('sphere', na=False) & ~mask_shape_empty  # Object is not a sphere and has a shape

    # CASE 1: For non-spheres, all dimensions and span are available
    mask1 = mask_non_sphere & x.notna() & y.notna() & z.notna() & span.notna()
    val1 = np.sqrt(x ** 2 + y ** 2 + z ** 2) / 2    # Half of 3D diagonal
    val2 = span / 2                                 # Half span
    HBR[mask1] = np.maximum(val1[mask1], val2[mask1])

    # Optionally update shape label for box-like objects with dominant span
    mask_box = mask1 & (shape == 'box') & (val2 > val1)
    df.loc[mask_box, 'SHAPE'] = 'Box with extra span'

    # CASE 2: Cone or cylinder, height (y) and diameter are available
    mask2 = mask_non_sphere & (shape.str.contains('cone', na=False) | shape.str.contains('cyl', na=False)) & y.notna() & diam.notna()
    mask_cone = mask2 & shape.str.contains('cone', na=False)
    mask_cyl = mask2 & shape.str.contains('cyl', na=False)

    # For cones: use sqrt(y^2 + (d/2)^2)/2, for cylinders: sqrt(y^2 + d^2)/2
    val1_cone = np.sqrt(y ** 2 + (diam / 2) ** 2) / 2
    val1_cyl = np.sqrt(y ** 2 + diam ** 2) / 2

    val1_mask2 = pd.Series(np.nan, index=df.index)
    val1_mask2[mask_cone] = val1_cone[mask_cone]
    val1_mask2[mask_cyl] = val1_cyl[mask_cyl]

    # If span is available, use the maximum; otherwise, use calculated value
    mask2_span_notna = mask2 & span.notna()
    HBR[mask2_span_notna] = np.maximum(val1_mask2[mask2_span_notna], span[mask2_span_notna] / 2)
    mask2_span_na = mask2 & span.isna()
    HBR[mask2_span_na] = val1_mask2[mask2_span_na]

    # CASE 3: All three dimensions available, but not already covered above
    mask3 = mask_non_sphere & x.notna() & y.notna() & z.notna() & ~mask1 & ~mask2
    HBR[mask3] = np.sqrt(x[mask3] ** 2 + y[mask3] ** 2 + z[mask3] ** 2) / 2

    # CASE 4: Span only, as fallback (not already used)
    mask4 = mask_non_sphere & span.notna() & ~mask1 & ~mask2 & ~mask3
    HBR[mask4] = span[mask4] / 2

    # CASE 5: Spheres (or ellipsoids): use half the largest available dimension
    mask_sphere = shape.str.startswith('sphere', na=False) & ~mask_shape_empty
    max_dim = df[['LENGTH', 'HEIGHT', 'DEPTH', 'DIAMETER', 'SPAN']].max(axis=1, skipna=True)
    HBR[mask_sphere] = max_dim[mask_sphere] / 2

    df['HBR'] = HBR
    df.drop(columns=['SHAPE_LOWER'], inplace=True)

    return df

def parseQSMagFile():
    """
    Parse the QS.MAG file to obtain NORAD IDs and standard (intrinsic) magnitudes for space objects.

    Returns:
        df_qsmag -> [pandas.DataFrame] DataFrame with columns:
            'NORAD_ID' -> [int] NORAD catalog number of the object.
            'StdMag' -> [float] Standard (intrinsic) optical magnitude of the object.
    Notes:
        - See https://www.prismnet.com/~mmccants/programs/qsmag.zip for source format details.
    """
    # Ensure the QS.MAG file is present and updated
    data_prepare.qsmag_load()
    qsfile = data_prepare.qs_file

    # Read file using fixed-width fields: 5 chars (NORAD_ID), 28 chars (object name), 5 chars (magnitude)
    # Skip the header/footer lines, extract only id and magnitude fields
    try:
        qsmag = np.genfromtxt(
            qsfile, skip_header=1, skip_footer=1,
            delimiter=[5, 28, 5], dtype=(int, str, float)
        )
    except Exception as e:
        raise RuntimeError(f"Error reading QS.MAG file: {e}")

    # Convert to DataFrame, drop the name column, and rename appropriately
    df_qsmag = pd.DataFrame(qsmag).drop(columns=['f1']).rename(columns={"f0": "NORAD_ID", "f2": "StdMag"})
    return df_qsmag

def _discos_buildin_filter(params,expr):
    """
    A build-in function associated to the function discos_query.

    Inputs:
        params -> [dictionary] Parameters in function discos_query
        expr -> [str] Filter expressions for DISCOS database query, for example, "eq(reentry.epoch,null)".
    Returns:
        params_upgrade -> [dictionary] Upgraded parameters in function discos_query

    For more information, please reference to https://discosweb.esoc.esa.int/apidocs
    """
    if 'filter' in params.keys(): 
        params['filter'] += '&(' + expr + ')'
    else:
        params['filter'] = expr 
    return params

def _discos_query(
    NORAD_ID=None, COSPAR_ID=None, OBJECT_CLASS=None, MISSION_TYPE=None,
    PAYLOAD=None, DECAYED=None, DECAY_DATE=None, FIRST_EPOCH=None, MASS=None,
    SHAPE=None, LENGTH=None, HEIGHT=None, DEPTH=None, DIAMETER=None, SPAN=None,
    RCSMin=None, RCSMax=None, RCSAvg=None, ACTIVE=None, sort=None):
    """
    Query the ESA DISCOS (Database and Information System Characterising Objects in Space) catalog
    for space objects matching specified geometric, physical, and status constraints.

    Inputs:
        NORAD_ID -> [int, str, list, or str (filename), optional] One or more NORAD IDs, or a filename (e.g. 'satno.txt') containing NORAD IDs (one per line).
        COSPAR_ID -> [str or list, optional] One or more COSPAR IDs (International Designators).
        OBJECT_CLASS -> [str or list, optional] Classification of objects.
            Available options include:
                'Payload', 'Payload Debris', 'Payload Fragmentation Debris',
                'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris',
                'Rocket Fragmentation Debris', 'Rocket Mission Related Object',
                'Other Mission Related Object', 'Other Debris', 'Unknown'.
            Any combination is supported (e.g. ['Rocket Body', 'Rocket Debris']).
        MISSION_TYPE -> [str or list, optional] Mission type(s).
            Supported options include:
                'Civil Calibration', 'Civil Technology', 'Civil Planetary', 'Civil Science',
                'Defense Calibration', 'Defense Technology', 'Defense Communications', 'Defense Science', 'Defense Sigint',
                'Commercial Technology','Commercial Communications', 'Commercial Weather', 'Commercial Radar Imaging',
                'Commercial Imaging', 'Commercial Misc', 'Commercial Astronomy', 'Commercial Science',
                'Amateur Sigint','Amateur Imaging', 'Amateur Edu/Com', 'Amateur Tech/Com', 'Amateur Science',
                'Amateur Calibration', 'Amateur Technology', 'Amateur Communications', 'Amateur Astronomy'.
            Multiple types can be given as a list.
        PAYLOAD -> [bool, optional] If True, select only payloads; if False, select only non-payloads.
        DECAYED -> [bool, optional] If True, select only decayed (re-entered) objects; if False, only still-orbiting objects.
        DECAY_DATE -> [list of str, optional] Date range for decay epoch, as ['YYYY-MM-DD','YYYY-MM-DD'].
        FIRST_EPOCH -> [list of str, optional] Date range for first epoch (launch), as ['YYYY-MM-DD','YYYY-MM-DD'].
        MASS -> [list of float, optional] Range of mass in kg, as [min, max].
        SHAPE -> [str or list of str, optional] Object shape(s).
            Supported values include:
                'Cyl', 'Sphere', 'Cone', 'Dcone', 'Pan', 'Ell', 'Dish', 'Cable', 'Box',
                'Rod', 'Poly', 'Sail', 'Ant', 'Hex', 'Tether', 'Frust', 'Truss', 'Nozzle', 'lrr'.
            If provided as a list and the last element is '+', all must be satisfied ("and");
            otherwise, any is sufficient ("or").
        LENGTH -> [list of float, optional] Range of length in meters, as [min, max].
        HEIGHT -> [list of float, optional] Range of height in meters, as [min, max].
        DEPTH -> [list of float, optional] Range of depth in meters, as [min, max].
        DIAMETER -> [list of float, optional] Range of diameter in meters, as [min, max].
        SPAN -> [list of float, optional] Range of span in meters, as [min, max].
        RCSMin -> [list of float, optional] Range for minimum radar cross-section (RCS) in m^2, as [min, max].
        RCSMax -> [list of float, optional] Range for maximum radar cross-section (RCS) in m^2, as [min, max].
        RCSAvg -> [list of float, optional] Range for average radar cross-section (RCS) in m^2, as [min, max].
        ACTIVE -> [bool, optional] If True, select only active satellites; if False, only inactive; if None, no filtering.
        sort -> [str, optional] Sort the results by an attribute.
            Supported values:
                'COSPAR_ID', 'NORAD_ID', 'OBJECT_CLASS', 'MISSION_TYPE', 'MASS',
                'SHAPE', 'LENGTH', 'HEIGHT', 'DEPTH', 'DIAMETER', 'SPAN', 'RCSMin',
                'RCSMax', 'RCSAvg', 'DECAY_DATE', 'FIRST_EPOCH'.
            Prefix with '-' for descending order (e.g., '-MASS'). Default is ascending by NORAD_ID.
    Returns:
        df -> [pandas.DataFrame] DataFrame containing the selected objects and their physical/geometric parameters.
    Notes:
        - If too many pages are requested, automatic throttling is applied (30s pause after every 20 pages).
        - See https://discosweb.esoc.esa.int for catalog field definitions.
    """
    # Token Management for DISCOS API
    # Token file is stored in ~/src/discos-data/discos-token.
    home = str(Path.home())
    data_dir = os.path.join(home, 'src', 'discos-data')
    token_file = os.path.join(data_dir, 'discos-token')
    os.makedirs(data_dir, exist_ok=True)

    if not os.path.exists(token_file):
        token = input('Please input your DISCOS API token (available from https://discosweb.esoc.esa.int/tokens): ')
        with open(token_file, 'w') as outfile:
            outfile.write(token)
    else:
        with open(token_file, 'r') as infile:
            token = infile.readline().strip()

    URL = 'https://discosweb.esoc.esa.int'
    params = {}

    # Object Class
    if PAYLOAD is not None:
        if PAYLOAD is True:
            object_classes = [
                'Payload', 'Payload Mission Related Object',
                'Rocket Mission Related Object', 'Other Mission Related Object', 'Unknown'
            ]
        elif PAYLOAD is False:
            object_classes = [
                'Payload Debris', 'Payload Fragmentation Debris', 'Rocket Body',
                'Rocket Debris', 'Rocket Fragmentation Debris', 'Other Debris'
            ]
        else:
            raise Exception("PAYLOAD must be None, True, or False.")

        filter_exprs = [f"eq(objectClass,'{cls}')" for cls in object_classes]
        params = _discos_buildin_filter(params, '(' + '|'.join(filter_exprs) + ')')
    elif OBJECT_CLASS is not None:
        if isinstance(OBJECT_CLASS, str):
            filter_expr = f"eq(objectClass,'{OBJECT_CLASS}')"
        elif isinstance(OBJECT_CLASS, list):
            filter_exprs = [f"eq(objectClass,'{cls}')" for cls in OBJECT_CLASS]
            filter_expr = '(' + '|'.join(filter_exprs) + ')'
        else:
            raise Exception('OBJECT_CLASS should be a string or list of strings.')
        params = _discos_buildin_filter(params, filter_expr)

    # Decayed Filters
    if DECAYED is not None:
        if DECAYED is False:
            filter_expr = "eq(reentry.epoch,null)"
        elif DECAYED is True:
            filter_expr = "ne(reentry.epoch,null)"
        else:
            raise Exception("DECAYED must be True, False, or None.")
        params = _discos_buildin_filter(params, filter_expr)

    if DECAY_DATE is not None:
        filter_expr = f"ge(reentry.epoch,epoch:'{DECAY_DATE[0]}')&le(reentry.epoch,epoch:'{DECAY_DATE[1]}')"
        params = _discos_buildin_filter(params, filter_expr)

    if FIRST_EPOCH is not None:
        filter_expr = f"ge(firstEpoch,epoch:'{FIRST_EPOCH[0]}')&le(firstEpoch,epoch:'{FIRST_EPOCH[1]}')"
        params = _discos_buildin_filter(params, filter_expr)

    # ID Filtering
    if COSPAR_ID is not None:
        if isinstance(COSPAR_ID, str):
            filter_expr = f"eq(cosparId,'{COSPAR_ID}')"
        elif isinstance(COSPAR_ID, list):
            filter_expr = f"in(cosparId,{str(tuple(COSPAR_ID)).replace(' ', '')})"
        else:
            raise Exception('COSPAR_ID should be a string or list of strings.')
        params = _discos_buildin_filter(params, filter_expr)

    if NORAD_ID is not None:
        # If a filename is provided, load list from file
        if isinstance(NORAD_ID, str) and '.' in NORAD_ID:
            NORAD_ID = list(np.loadtxt(NORAD_ID, dtype=str))
        if isinstance(NORAD_ID, list):
            filter_expr = f"in(satno,{str(tuple(NORAD_ID)).replace(' ', '')})"
        elif isinstance(NORAD_ID, str):
            filter_expr = f"eq(satno,{NORAD_ID})"
        elif isinstance(NORAD_ID, int):
            filter_expr = f"eq(satno,{NORAD_ID})"
        else:
            raise Exception('NORAD_ID must be int, str, or list of int/str.')
        params = _discos_buildin_filter(params, filter_expr)

    # Physical & Geometric Attribute Filtering
    if MASS is not None:
        filter_expr = f'ge(mass,{MASS[0]:.2f})&le(mass,{MASS[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if SHAPE is not None:
        if isinstance(SHAPE, str):
            filter_expr = f"icontains(shape,'{SHAPE}')"
        elif isinstance(SHAPE, list):
            end_symbol = SHAPE[-1]
            if end_symbol == '+':
                filter_expr = '&'.join([f"icontains(shape,'{el}')" for el in SHAPE[:-1]])
            else:
                filter_expr = '|'.join([f"icontains(shape,'{el}')" for el in SHAPE])
        else:
            raise Exception('SHAPE should be a string or list.')
        params = _discos_buildin_filter(params, filter_expr)
    if MISSION_TYPE is not None:
        if isinstance(MISSION_TYPE, str):
            filter_expr = f"icontains(mission,'{MISSION_TYPE}')"
        elif isinstance(MISSION_TYPE, list):
            filter_expr = '|'.join([f"icontains(mission,'{el}')" for el in MISSION_TYPE])
        else:
            raise Exception('MISSION_TYPE should be a string or list.')
        params = _discos_buildin_filter(params, filter_expr)
    if LENGTH is not None:
        filter_expr = f'ge(length,{LENGTH[0]:.2f})&le(length,{LENGTH[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if HEIGHT is not None:
        filter_expr = f'ge(height,{HEIGHT[0]:.2f})&le(height,{HEIGHT[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if DEPTH is not None:
        filter_expr = f'ge(depth,{DEPTH[0]:.2f})&le(depth,{DEPTH[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if DIAMETER is not None:
        filter_expr = f'ge(diameter,{DIAMETER[0]:.2f})&le(diameter,{DIAMETER[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if SPAN is not None:
        filter_expr = f'ge(span,{SPAN[0]:.2f})&le(span,{SPAN[1]:.2f})'
        params = _discos_buildin_filter(params, filter_expr)
    if RCSMin is not None:
        filter_expr = f'ge(xSectMin,{RCSMin[0]:.4f})&le(xSectMin,{RCSMin[1]:.4f})'
        params = _discos_buildin_filter(params, filter_expr)
    if RCSMax is not None:
        filter_expr = f'ge(xSectMax,{RCSMax[0]:.4f})&le(xSectMax,{RCSMax[1]:.4f})'
        params = _discos_buildin_filter(params, filter_expr)
    if RCSAvg is not None:
        filter_expr = f'ge(xSectAvg,{RCSAvg[0]:.4f})&le(xSectAvg,{RCSAvg[1]:.4f})'
        params = _discos_buildin_filter(params, filter_expr)
    if ACTIVE is not None:
        filter_expr = 'eq(active,"true")' if ACTIVE else 'eq(active,"false")'
        params = _discos_buildin_filter(params, filter_expr)

    # Sorting
    sort_map = {
        'COSPAR_ID': 'cosparId',
        'NORAD_ID': 'satno',
        'OBJECT_CLASS': 'objectClass',
        'MISSION_TYPE': 'mission',
        'MASS': 'mass',
        'SHAPE': 'shape',
        'LENGTH': 'length',
        'HEIGHT': 'height',
        'DEPTH': 'depth',
        'DIAMETER': 'diameter',
        'SPAN': 'span',
        'RCSMin': 'xSectMin',
        'RCSMax': 'xSectMax',
        'RCSAvg': 'xSectAvg',
        'DECAY_DATE': 'reentry.epoch',
        'FIRST_EPOCH': 'firstEpoch'
    }
    if sort is None:
        params['sort'] = 'satno'
    else:
        desc = sort[0] == '-'
        sort_key = sort[1:] if desc else sort
        sort_key = sort_key.upper()
        if sort_key not in sort_map:
            raise Exception("Sort key not recognized. Valid options: " + ', '.join(sort_map.keys()))
        params['sort'] = ('-' if desc else '') + sort_map[sort_key]

    # Query API
    params['page[number]'] = 1
    extract = []

    while True:
        params['page[size]'] = 100  # Number of entries per page
        response = requests.get(f'{URL}/api/objects',
            headers={
                'Authorization': f'Bearer {token}',
                'DiscosWeb-Api-Version': '1',
            },
            params=params
        )
        doc = response.json()
        if response.ok:
            if not doc['data']:
                raise Exception('No entries found. Adjust your filter parameters.')
            data = doc['data']
            extract.extend([item['attributes'] for item in data])
            currentPage = doc['meta']['pagination']['currentPage']
            totalPages = doc['meta']['pagination']['totalPages']
            print(f"\rCurrentPage {currentPage:3d} in TotalPages {totalPages:3d}", end='')
            if currentPage < totalPages:
                params['page[number]'] += 1
            else:
                break
            # Prevent rate limiting: pause after every 20 pages
            if currentPage % 20 == 0:
                sleep(30)
        else:
            return doc.get('errors', 'Unknown API error')

    # DataFrame Construction & Reordering
    old_column = [
        'height', 'xSectMax', 'name', 'satno', 'objectClass', 'mass', 'xSectMin',
        'depth', 'xSectAvg', 'length', 'shape', 'cosparId', 'diameter', 'span',
        'mission', 'firstEpoch', 'active'
    ]
    new_column = [
        'HEIGHT', 'RCSMax', 'OBJECT_NAME', 'NORAD_ID', 'OBJECT_CLASS', 'MASS', 'RCSMin',
        'DEPTH', 'RCSAvg', 'LENGTH', 'SHAPE', 'COSPAR_ID', 'DIAMETER', 'SPAN',
        'MISSION_TYPE', 'FIRST_EPOCH', 'ACTIVE'
    ]
    # Desired final column order (including HBR)
    new_column_reorder = [
        'OBJECT_NAME', 'COSPAR_ID', 'NORAD_ID', 'OBJECT_CLASS', 'MISSION_TYPE', 'SHAPE', 'MASS', 'HBR',
        'HEIGHT', 'LENGTH', 'DEPTH', 'DIAMETER', 'SPAN',
        'RCSMin', 'RCSMax', 'RCSAvg', 'DECAY_DATE', 'FIRST_EPOCH', 'ACTIVE'
    ]

    df = pd.DataFrame.from_dict(extract, dtype=object).rename(columns=dict(zip(old_column, new_column)), errors='raise')
    df = calculate_hbr(df)
    df = df.reindex(columns=new_column_reorder)
    df = df.reset_index(drop=True)
    return df

def _celestrak_query(
    NORAD_ID=None, COSPAR_ID=None, PAYLOAD=None, DECAYED=None, DECAY_DATE=None,
    PERIOD=None, INCLINATION=None, APOGEE=None, PERIGEE=None, MEAN_ALT=None, ECC=None,
    OWNER=None, TLE_STATUS=None, sort=None):
    """
    Query the Celestrak satellite catalog for space objects that match specified orbital, physical, and status constraints.

    Inputs:
        NORAD_ID -> [int, str, list of int/str, or str (filename), optional] One or more NORAD catalog IDs, e.g., 43205 or [25544,43205], or a filename (e.g., 'noradids.txt') containing IDs (one per line).
        COSPAR_ID -> [str or list of str, optional] One or more COSPAR (International Designator) IDs, e.g., '2018-099A' or ['2018-099A','1998-067A'].
        PAYLOAD -> [bool, optional] If True, select only payloads; if False, only non-payloads.
        DECAYED -> [bool, optional] If True, select only decayed (re-entered) objects; if False, only objects still in orbit.
        DECAY_DATE -> [list of str, optional] Range of decay dates as ['YYYY-MM-DD','YYYY-MM-DD'], e.g., ['2019-01-05','2020-05-30'].
        PERIOD -> [list of float, optional] Range of orbital period in minutes, as [min, max], e.g., [90.0,120.0]. If None, ignored.
        INCLINATION -> [list of float, optional] Range of orbital inclination in degrees, as [min, max], e.g., [45.0,98.0].
        APOGEE -> [list of float, optional] Range of apogee altitude in kilometers, as [min, max], e.g., [800.0,1400.0].
        PERIGEE -> [list of float, optional] Range of perigee altitude in kilometers, as [min, max], e.g., [300.0,400.0].
        MEAN_ALT -> [list of float, optional] Range of mean altitude in kilometers, as [min, max], e.g., [300.0,800.0].
        ECC -> [list of float, optional] Range of orbital eccentricity, as [min, max], e.g., [0.01,0.2].
        OWNER -> [str or list of str, optional] One or more owner country codes or names (e.g., 'USA', 'RUS', or ['USA','CHN']).
            For codes, see: http://www.fao.org/countryprofiles/iso3list/en/.
        TLE_STATUS -> [bool, optional] Whether TLE is valid.
            If True, select only objects with valid/current TLEs;
            if False, only those without current TLEs ("No Current Elements", etc);
        sort -> [str, optional] Attribute to sort the output DataFrame by.
            Supported values include:
                'COSPAR_ID', 'NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE',
                'PERIGEE', 'MEAN_ALT', 'ECC', 'LAUNCH_DATE', 'LAUNCH_SITE', 'RCS', 'OWNER'.
            Prefix with '-' for descending order (e.g., '-MEAN_ALT').
            If None, sorts by NORAD_ID in ascending order.
    Returns:
        df -> [pandas.DataFrame]
            DataFrame containing the filtered space objects and their main catalog attributes.
    Notes:
        - 'PERIOD' is in minutes, 'INCLINATION' in degrees, 'APOGEE'/'PERIGEE'/'MEAN_ALT' in km, 'ECC' is dimensionless.
        - Input ranges [min, max] are inclusive.
        - See https://celestrak.com/satcat/ for catalog field definitions and value conventions.
        - For best results, provide as many constraints as possible to narrow the query.
    """
    # Load and update the satcat file from Celestrak
    data_prepare.satcat_load()
    satcat_file = data_prepare.sc_file

    data = pd.read_csv(satcat_file)
    columns_dict = {'OBJECT_ID': 'COSPAR_ID', 'NORAD_CAT_ID': 'NORAD_ID'}
    data.rename(columns=columns_dict, inplace=True)

    # Calculate derived fields: MEAN_ALT and ECC
    data['MEAN_ALT'] = (data['APOGEE'] + data['PERIGEE']) / 2
    # Earth's mean equatorial radius in km for ECC computation (WGS-84): 6378.137 km
    Re = getattr(Const, 'Re_V', 6378.137)
    data['ECC'] = (data['APOGEE'] - data['PERIGEE']) / (data['MEAN_ALT'] + Re) / 2

    # Pre-allocate filter masks as all True
    N = len(data)
    mask = np.ones(N, dtype=bool)

    # Filter by COSPAR_ID
    if COSPAR_ID is not None:
        if isinstance(COSPAR_ID, str):
            ids = [COSPAR_ID]
        elif isinstance(COSPAR_ID, list):
            ids = COSPAR_ID
        else:
            raise Exception('COSPAR_ID should be str or list of str.')
        mask &= data['COSPAR_ID'].isin(ids)

    # Filter by NORAD_ID (accept int, str, list, or filename)
    if NORAD_ID is not None:
        if isinstance(NORAD_ID, int):
            ids = [NORAD_ID]
        elif isinstance(NORAD_ID, list):
            ids = [int(i) for i in NORAD_ID]
        elif isinstance(NORAD_ID, str):
            if NORAD_ID.strip().endswith('.txt'):  # filename
                try:
                    with open(NORAD_ID, 'r') as f:
                        lines = [int(line.strip()) for line in f if line.strip()]
                    ids = lines
                except Exception as e:
                    raise Exception(f"Failed to read NORAD_ID file: {e}")
            else:
                try:
                    ids = [int(NORAD_ID)]
                except ValueError:
                    raise Exception("NORAD_ID string must be an integer or a valid filename.")
        else:
            raise Exception('NORAD_ID should be int, str, or list of int/str.')
        mask &= data['NORAD_ID'].isin(ids)

    # Filter by payload status
    if PAYLOAD is not None:
        # In CelesTrak, 'OBJECT_TYPE' is 'PAY' for payload, otherwise not payload
        is_payload = data['OBJECT_TYPE'] == 'PAY'
        mask &= is_payload if PAYLOAD else ~is_payload

    # Filter by decayed status
    if DECAYED is not None:
        is_decayed = data['OPS_STATUS_CODE'] == 'D'
        mask &= is_decayed if DECAYED else ~is_decayed

    # Filter by DECAY_DATE range (closed interval)
    if DECAY_DATE is not None:
        date0, date1 = DECAY_DATE
        # 'DECAY_DATE' is string; convert and compare as dates for reliability
        decay_dates = pd.to_datetime(data['DECAY_DATE'], errors='coerce')
        mask &= (decay_dates >= pd.to_datetime(date0)) & (decay_dates <= pd.to_datetime(date1))

    # Filter by orbital period [min, max]
    if PERIOD is not None:
        period0, period1 = PERIOD
        mask &= (data['PERIOD'] >= period0) & (data['PERIOD'] <= period1)

    # Filter by inclination [min, max]
    if INCLINATION is not None:
        inc0, inc1 = INCLINATION
        mask &= (data['INCLINATION'] >= inc0) & (data['INCLINATION'] <= inc1)

    # Filter by apogee altitude [min, max]
    if APOGEE is not None:
        apo0, apo1 = APOGEE
        mask &= (data['APOGEE'] >= apo0) & (data['APOGEE'] <= apo1)

    # Filter by perigee altitude [min, max]
    if PERIGEE is not None:
        peri0, peri1 = PERIGEE
        mask &= (data['PERIGEE'] >= peri0) & (data['PERIGEE'] <= peri1)

    # Filter by mean altitude [min, max]
    if MEAN_ALT is not None:
        ma0, ma1 = MEAN_ALT
        mask &= (data['MEAN_ALT'] >= ma0) & (data['MEAN_ALT'] <= ma1)

    # Filter by eccentricity [min, max]
    if ECC is not None:
        e0, e1 = ECC
        mask &= (data['ECC'] >= e0) & (data['ECC'] <= e1)

    # Filter by owner/country code
    if OWNER is not None:
        if isinstance(OWNER, str):
            owners = [OWNER]
        elif isinstance(OWNER, list):
            owners = OWNER
        else:
            raise Exception('OWNER should be str or list of str.')
        mask &= data['OWNER'].isin(owners)

    # Filter by TLE_STATUS: True for valid/current TLE, False for invalid
    if TLE_STATUS is not None:
        # In Celestrak, 'OPS_STATUS_CODE' is null for valid/current elements
        valid_tle = data['OPS_STATUS_CODE'].isnull()
        mask &= valid_tle if TLE_STATUS else ~valid_tle

    # Apply combined mask to select records
    df = data[mask]

    # Reorder or drop columns as needed
    column_reorder = [
        'OBJECT_NAME', 'COSPAR_ID', 'NORAD_ID', 'OBJECT_TYPE', 'OPS_STATUS_CODE', 'DECAY_DATE',
        'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC',
        'LAUNCH_DATE', 'LAUNCH_SITE', 'RCS', 'OWNER', 'OPS_STATUS_CODE', 'ORBIT_CENTER', 'ORBIT_TYPE'
    ]
    # Only keep columns that exist in the DataFrame (in case of field variation)
    column_reorder = [col for col in column_reorder if col in df.columns]
    df = df.reindex(columns=column_reorder)

    # If TLE_STATUS is True, drop 'OPS_STATUS_CODE' from output
    if TLE_STATUS is True and 'OPS_STATUS_CODE' in df.columns:
        df = df.drop(columns=['OPS_STATUS_CODE'])

    # Sort the DataFrame
    if sort is None:
        df = df.sort_values(by='NORAD_ID', ascending=True)
    else:
        ascending_flag = not (isinstance(sort, str) and sort.startswith('-'))
        sort_key = sort[1:] if not ascending_flag else sort
        sort_key = sort_key.upper()
        # Map user keys to actual DataFrame columns (if needed)
        sort_map = {
            'COSPAR_ID': 'COSPAR_ID',
            'NORAD_ID': 'NORAD_ID',
            'DECAY_DATE': 'DECAY_DATE',
            'PERIOD': 'PERIOD',
            'INCLINATION': 'INCLINATION',
            'APOGEE': 'APOGEE',
            'PERIGEE': 'PERIGEE',
            'MEAN_ALT': 'MEAN_ALT',
            'ECC': 'ECC',
            'LAUNCH_DATE': 'LAUNCH_DATE',
            'LAUNCH_SITE': 'LAUNCH_SITE',
            'RCS': 'RCS',
            'OWNER': 'OWNER'
        }
        if sort_key not in sort_map:
            raise Exception("Available sort options: " + ', '.join(sort_map.keys()))
        if sort_map[sort_key] not in df.columns:
            raise Exception(f"Sort column '{sort_map[sort_key]}' is not available in the DataFrame.")
        df = df.sort_values(by=sort_map[sort_key], ascending=ascending_flag)

    df = df.reset_index(drop=True)
    return df

def _objects_query(
    NORAD_ID=None, COSPAR_ID=None, PAYLOAD=None, OBJECT_CLASS=None,
    DECAYED=None, DECAY_DATE=None, PERIOD=None, INCLINATION=None, APOGEE=None,
    PERIGEE=None, MEAN_ALT=None, ECC=None, TLE_STATUS=None, MASS=None, SHAPE=None,
    LENGTH=None, HEIGHT=None, DEPTH=None, RCSMin=None, RCSMax=None, RCSAvg=None,
    OWNER=None, sort=None):
    """
    Query space object catalogs for objects matching specified geometric, physical, and orbital constraints.
    This function automatically combines the results of [DISCOS](https://discosweb.esoc.esa.int)
    and [CELESTRAK](https://celestrak.com), and attaches standard magnitudes from QSMAG.

    Inputs:
        NORAD_ID -> [int, str, list of int/str, or str (filename), optional] One or more NORAD catalog IDs, e.g., 43205 or [25544,43205], or a filename (e.g., 'noradids.txt') containing IDs (one per line).
        COSPAR_ID -> [str or list of str, optional] One or more COSPAR (International Designator) IDs, e.g., '2018-099A' or ['2018-099A','1998-067A'].
        PAYLOAD -> [bool, optional] If True, select only payloads; if False, only non-payloads.
        OBJECT_CLASS -> [str or list of str, optional] Object class (as defined in DISCOS), e.g.:
                'Payload', 'Payload Debris', 'Payload Fragmentation Debris',
                'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris',
                'Rocket Fragmentation Debris', 'Rocket Mission Related Object',
                'Other Mission Related Object', 'Other Debris', 'Unknown'.
            Any combination is supported as a list.
        DECAYED -> [bool, optional] If True, select only decayed (re-entered) objects; if False, only still-orbiting objects.
        DECAY_DATE -> [list of str, optional] Range of decay dates as ['YYYY-MM-DD','YYYY-MM-DD'], e.g., ['2019-01-05','2020-05-30'].
        PERIOD -> [list of float, optional] Orbital period range in minutes, as [min, max], e.g., [100.0,200.0].
        INCLINATION -> [list of float, optional] Orbital inclination range in degrees, as [min, max], e.g., [45.0,98.0].
        APOGEE -> [list of float, optional] Apogee altitude range in kilometers, as [min, max], e.g., [800.0,1400.0].
        PERIGEE -> [list of float, optional] Perigee altitude range in kilometers, as [min, max], e.g., [300.0,400.0].
        MEAN_ALT -> [list of float, optional] Mean altitude range in kilometers, as [min, max], e.g., [300.0,800.0].
        ECC -> [list of float, optional] Eccentricity range, as [min, max], e.g., [0.01,0.2].
        TLE_STATUS -> [bool, optional] Whether the object has a valid/current TLE (Two-Line Element set).
            If True, select only objects with valid/current TLEs;
            if False, only those without current TLEs;
        MASS -> [list of float, optional] Mass range in kg, as [min, max], e.g., [5.0, 10.0].
        SHAPE -> [str or list of str, optional]
            Shape of the object (as defined in DISCOS), e.g.:
                'Cyl', 'Sphere', 'Cone', 'Dcone', 'Pan', 'Ell', 'Dish', 'Cable', 'Box',
                'Rod', 'Poly', 'Sail', 'Ant', 'Frust', 'Truss', 'Nozzle', 'lrr', etc.
            As a list, all must be satisfied if the last element is '+', otherwise any is sufficient ("or").
        LENGTH -> [list of float, optional] Length range in meters, as [min, max], e.g., [5.0, 10.0].
        HEIGHT -> [list of float, optional] Height range in meters, as [min, max], e.g., [5.0, 10.0].
        DEPTH -> [list of float, optional] Depth range in meters, as [min, max], e.g., [5.0, 10.0].
        RCSMin -> [list of float, optional] Minimum radar cross section (RCS) range in m^2, as [min, max].
        RCSMax -> [list of float, optional] Maximum radar cross section (RCS) range in m^2, as [min, max].
        RCSAvg -> [list of float, optional] Average radar cross section (RCS) range in m^2, as [min, max].
        OWNER -> [str or list of str, optional] Owner or country code/name (e.g., 'USA', 'RUS', or ['USA','CHN']).
        sort -> [str, optional] Attribute to sort the results by.
            Supported values include:
                'COSPAR_ID', 'NORAD_ID', 'DECAY_DATE', 'SHAPE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC',
                'MASS', 'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RCSMax', 'RCSAvg', 'HBR', 'StdMag', 'LAUNCH_DATE', 'OWNER'.
            Prefix with '-' for descending order (e.g., '-RCSAvg').
            If None, sorts by NORAD_ID ascending.
    Returns:
        df -> [pandas.DataFrame]
            DataFrame containing objects and their key orbital, geometric, and photometric properties.
            The merged catalog combines attributes from CELESTRAK, DISCOS, and QSMAG standard magnitude files.
    Notes:
        - The function first queries Celestrak by orbital constraints, then uses the matching NORAD_IDs to query DISCOS for geometric/physical data,
          and merges the result. Standard optical magnitudes from QSMAG are attached via NORAD_ID (if available).
        - Ranges [min, max] are inclusive; all units are SI (km, deg, min, kg, m^2, etc).
        - See https://discosweb.esoc.esa.int and https://celestrak.com/satcat/ for field definitions.
    """
    # Query Celestrak database based on orbital constraints
    df_celestrak = _celestrak_query(
        COSPAR_ID, NORAD_ID, PAYLOAD, DECAYED, DECAY_DATE, PERIOD,
        INCLINATION, APOGEE, PERIGEE, MEAN_ALT, ECC, OWNER, TLE_STATUS
    ).drop('OBJECT_NAME', axis=1)

    # Determine the list of NORAD IDs to use for DISCOS query
    noradids = list(df_celestrak['NORAD_ID'])
    if len(noradids) > 1000: noradids = None # If too many objects (>1000)

    print('Querying the DISCOS database ...')

    # Query DISCOS database for geometric and physical parameters
    df_discos = _discos_query(
        COSPAR_ID, noradids, OBJECT_CLASS, PAYLOAD, DECAYED, DECAY_DATE,
        MASS, SHAPE, LENGTH, HEIGHT, DEPTH, RCSMin, RCSMax, RCSAvg
    ).dropna(subset=['NORAD_ID'])

    # Merge Celestrak and DISCOS data on COSPAR_ID and NORAD_ID (one-to-one)
    try:
        df = pd.merge(
            df_celestrak, df_discos,
            on=['COSPAR_ID', 'NORAD_ID'],
            validate="one_to_one"
        )
    except Exception as e:
        raise RuntimeError(f"Error merging Celestrak and DISCOS data: {e}")

    # Merge QSMAG standard magnitude database (optional, left join)
    try:
        df_qsmag = parseQSMagFile()
        df = pd.merge(df, df_qsmag, on=['NORAD_ID'], how='left', validate="one_to_one")
    except Exception as e:
        print(f"Warning: Unable to merge with QSMAG file: {e}")

    # Remove unwanted columns and reorder for output consistency
    if 'RCS' in df.columns:
        df = df.drop(['RCS'], axis=1)

    column_reorder = [
        'OBJECT_NAME', 'COSPAR_ID', 'NORAD_ID', 'OBJECT_CLASS', 'OPS_STATUS_CODE', 'DECAY_DATE',
        'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', 'OPS_STATUS_CODE',
        'ORBIT_CENTER', 'ORBIT_TYPE', 'MASS', 'SHAPE', 'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin',
        'RCSMax', 'RCSAvg', 'HBR', 'StdMag', 'LAUNCH_DATE', 'LAUNCH_SITE', 'OWNER'
    ]
    # Only keep columns present in df
    column_reorder = [col for col in column_reorder if col in df.columns]
    df = df.reindex(columns=column_reorder)

    # If only current TLEs are requested, drop the status code column
    if TLE_STATUS and 'OPS_STATUS_CODE' in df.columns:
        df = df.drop(columns=['OPS_STATUS_CODE'])

    # Sort the final DataFrame as requested
    if sort is None:
        df = df.sort_values(by=['NORAD_ID'])
    else:
        ascending_flag = not (isinstance(sort, str) and sort.startswith('-'))
        sort_key = sort[1:] if not ascending_flag else sort
        # Map user sort key to DataFrame column if needed
        sort_map = {
            'COSPAR_ID': 'COSPAR_ID',
            'NORAD_ID': 'NORAD_ID',
            'DECAY_DATE': 'DECAY_DATE',
            'PERIOD': 'PERIOD',
            'INCLINATION': 'INCLINATION',
            'APOGEE': 'APOGEE',
            'PERIGEE': 'PERIGEE',
            'MEAN_ALT': 'MEAN_ALT',
            'ECC': 'ECC',
            'MASS': 'MASS',
            'LENGTH': 'LENGTH',
            'HEIGHT': 'HEIGHT',
            'DEPTH': 'DEPTH',
            'RCSMin': 'RCSMin',
            'RCSMax': 'RCSMax',
            'RCSAvg': 'RCSAvg',
            'HBR': 'HBR',
            'StdMag': 'StdMag',
            'LAUNCH_DATE': 'LAUNCH_DATE',
            'OWNER': 'OWNER'
        }
        if sort_key not in sort_map:
            raise Exception(
                "Available options for sorting: " + ', '.join(sort_map.keys()) +
                ". Add '-' for descending order."
            )
        if sort_map[sort_key] not in df.columns:
            raise Exception(f"Sort column '{sort_map[sort_key]}' is not present in the DataFrame.")
        df = df.sort_values(by=sort_map[sort_key], ascending=ascending_flag)

    df = df.reset_index(drop=True)
    return df

def _discos_query1(NORAD_ID=None,COSPAR_ID=None,OBJECT_CLASS=None,MISSION_TYPE=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,FIRST_EPOCH=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,DIAMETER=None,SPAN=None,RCSMin=None,RCSMax=None,RCSAvg=None,ACTIVE=None,sort=None):
    """
    Given the geometric constraints of a spatial object, query the qualified spatial objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.

    Inputs:
        NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
        COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored.
        OBJECT_CLASS -> [str, list of str, optional, default = None] Classification of objects; available options are 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
        'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
        for example, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.
        MISSION_TYPE -> [str, list of str, optional, default = None] Type of mission; available options are
        'Civil Calibration', 'Civil Technology', 'Civil Planetary', 'Civil Science',
        'Defense Calibration', 'Defense Technology', 'Defense Communications', 'Defense Science', 'Defense Sigint',
        'Commercial Technology','Commercial Communications', 'Commercial Weather', 'Commercial Radar Imaging', 'Commercial Imaging', 'Commercial Misc','Commercial Astronomy', 'Commercial Science',
        'Amateur Sigint','Amateur Imaging', 'Amateur Edu/Com', 'Amateur Tech/Com', 'Amateur Science','Amateur Calibration', 'Amateur Technology', 'Amateur Communications', 'Amateur Astronomy',
        or any combination of them,
        for example, ['Civil Technology', 'Defense Technology', 'Amateur Tech/Com']; If None, this option is ignored.
        PAYLOAD -> [bool, optional, default = None] Whether an object is payload or not. If True, the object is a payload; if False, not a payload; if None, this option is ignored.
        DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
        DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
        FIRST_EPOCH -> [list of str, optional, default = None] 首次发射的日期; it must be in form of ['date1','date2'], such as ['2011-01-05','2020-05-30']; if None, then this option is ignored.
        MASS -> [list of float, optional, default = None] Mass[kg] range of an object; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
        SHAPE -> [str or list of str, optional, default = None] Shape of an object; the usual choices include
        'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 'Hex', 'Tether'
        'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combination of them is also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
        LENGTH -> [list of float, optional, default = None] Length[m] range of an object; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
        HEIGHT -> [list of float, optional, default = None] Height[m] range of an object; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
        DEPTH -> [list of float, optional, default = None] Depth[m] range of an object; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
        DIAMETER ->
        SPAN ->
        RCSMin -> [list of float, optional, default = None] Minimum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        RCSMax -> [list of float, optional, default = None] Maximum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        RCSAvg -> [list of float, optional, default = None] Average Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        ACTIVE -> [list of bool, optional, default = None] 卫星是否为
        sort -> [str, optional, default = None] Sort according to attributes of spatial objects, such as mass; available options include 'COSPARID', NORADID', 'ObjectClass', 'DecayDate', 'Mass', 'Shape', 'Length', 'Height', 'Depth', 'RCSMin', 'RSCMax', and 'RCSAvg'.
        If the attribute is prefixed with a '-', such as '-Mass', it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    Returns:
        satcatalog_df -> Data frame containing the selected spatial objects
    """
    # DISCOS tokens
    home = str(Path.home())
    direc = home + '/src/discos-data/'
    tokenfile = direc + 'discos-token'

    if not path.exists(direc): makedirs(direc)
    if not path.exists(tokenfile):
        token = input('Please input the DISCOS tokens(which can be achieved from https://discosweb.esoc.esa.int/tokens): ')
        outfile_token = open(tokenfile,'w')
        outfile_token.write(token)
        outfile_token.close()
    else:
        infile = open(tokenfile,'r')
        token = infile.readline().strip()
        infile.close()   
    
    URL = 'https://discosweb.esoc.esa.int'
    params = {}

    # Set Payload based on ObjectClass
    if PAYLOAD is not None:
        if PAYLOAD is True:
            PayloadtoObjectClass = ['Payload','Payload Mission Related Object','Rocket Mission Related Object','Other Mission Related Object','Unknown']
        elif PAYLOAD is False:
            PayloadtoObjectClass = ['Payload Debris', 'Payload Fragmentation Debris','Rocket Body','Rocket Debris','Rocket Fragmentation Debris','Other Debris']
        else:
            raise Exception('Type of Payload should be either None, True or False.')  

        params_filter = []
        for element in PayloadtoObjectClass:
            params_filter.append("eq(objectClass,'{:s}')".format(element))
        temp = '(' + '|'.join(params_filter) + ')'
        params = _discos_buildin_filter(params,temp)

    else:
        # Filter parameters for 'ObjectClass'
        if OBJECT_CLASS is not None:
            if type(OBJECT_CLASS) is str:
                temp = "eq(objectClass,'{:s}')".format(OBJECT_CLASS)
            elif type(OBJECT_CLASS) is list:
                params_filter = []
                for element in OBJECT_CLASS:
                    params_filter.append("eq(objectClass,'{:s}')".format(element))
                temp = '(' + '|'.join(params_filter) + ')'
            else:
                raise Exception('Type of ObjectClass should be either string or list.')
            params = _discos_buildin_filter(params, temp)

    # Set Decayed based on reentry.epoch
    if DECAYED is not None:
        if DECAYED is False:
            temp = "eq(reentry.epoch,null)"
        elif DECAYED is True:
            temp = "ne(reentry.epoch,null)"
        else:
            raise Exception("'Decayed' must be one of 'False', 'True', or 'None'.")  
        params = _discos_buildin_filter(params,temp)     

    # Filter parameters for 'DECAY_DATE'
    if DECAY_DATE is not None:
        temp = "ge(reentry.epoch,epoch:'{:s}')&le(reentry.epoch,epoch:'{:s}')".format(DECAY_DATE[0],DECAY_DATE[1])
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'DECAY_DATE'
    if FIRST_EPOCH is not None:
        temp = "ge(firstEpoch,epoch:'{:s}')&le(firstEpoch,epoch:'{:s}')".format(FIRST_EPOCH[0], FIRST_EPOCH[1])
        params = _discos_buildin_filter(params, temp)
    
    # Filter parameters for 'COSPAR_ID'
    if COSPAR_ID is not None:
        if type(COSPAR_ID) is str:
            temp = "eq(cosparId,'{:s}')".format(COSPAR_ID)
        elif type(COSPAR_ID) is list:    
            temp = 'in(cosparId,{:s})'.format(str(tuple(COSPAR_ID))).replace(' ', '')
        else:
            raise Exception('Type of COSPAR_ID should be in str or list of str.')
        params = _discos_buildin_filter(params,temp)    
            
    # Filter parameters for 'NORAD_ID'        
    if NORAD_ID is not None:
        if type(NORAD_ID) is list:   
            temp = 'in(satno,{:s})'.format(str(tuple(NORAD_ID))).replace(' ', '')  
        elif type(NORAD_ID) is str:  
            if '.' in NORAD_ID: 
                NORAD_ID = list(np.loadtxt(NORAD_ID,dtype = str))
                temp = 'in(satno,{:s})'.format(str(tuple(NORAD_ID))).replace(' ', '')  
            else:    
                temp = 'eq(satno,{:s})'.format(NORAD_ID)  
        elif type(NORAD_ID) is int: 
            temp = 'eq(satno,{:s})'.format(str(NORAD_ID))           
        else:
            raise Exception('Type of NORAD_ID should be in int, str, list of int, or list of str.') 
        params = _discos_buildin_filter(params,temp)  
            
    # Filter parameters for 'Mass'            
    if MASS is not None:
        temp = 'ge(mass,{:.2f})&le(mass,{:.2f})'.format(MASS[0],MASS[1])
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'Shape' 
    if SHAPE is not None:
        if type(SHAPE) is str:
            temp = "icontains(shape,'{:s}')".format(SHAPE)
        elif type(SHAPE) is list:
            shape_filter = []
            end_symbol = SHAPE[-1]
            if end_symbol == '+':
                for element in SHAPE[:-1]:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '&'.join(shape_filter)
            else:
                for element in SHAPE:
                    shape_filter.append("icontains(shape,'{:s}')".format(element))
                temp = '|'.join(shape_filter)
        else:
            raise Exception('Type of Shape should either be string or list.')
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'Mission'
    if MISSION_TYPE is not None:
        if type(MISSION_TYPE) is str:
            temp = "icontains(mission,'{:s}')".format(MISSION_TYPE)
        elif type(MISSION_TYPE) is list:
            mission_filter = []
            for element in MISSION_TYPE:
                mission_filter.append("icontains(mission,'{:s}')".format(element))
            temp = '|'.join(mission_filter)
        else:
            raise Exception('Type of MISSION should either be string or list.')
        params = _discos_buildin_filter(params, temp)

    # Filter parameters for 'Length'
    if LENGTH is not None:
        temp = 'ge(length,{:.2f})&le(length,{:.2f})'.format(LENGTH[0],LENGTH[1])
        params = _discos_buildin_filter(params,temp)  
            
    # Filter parameters for 'Height'            
    if HEIGHT is not None:
        temp = 'ge(height,{:.2f})&le(height,{:.2f})'.format(HEIGHT[0],HEIGHT[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'Depth'            
    if DEPTH is not None:
        temp = 'ge(depth,{:.2f})&le(depth,{:.2f})'.format(DEPTH[0],DEPTH[1])   
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'Diameter'
    if DIAMETER is not None:
        temp = 'ge(diameter,{:.2f})&le(diameter,{:.2f})'.format(DIAMETER[0], DIAMETER[1])
        params = _discos_buildin_filter(params, temp)

    # Filter parameters for 'Span'
    if SPAN is not None:
        temp = 'ge(span,{:.2f})&le(span,{:.2f})'.format(SPAN[0], SPAN[1])
        params = _discos_buildin_filter(params, temp)

    # Filter parameters for 'RCSMin'
    if RCSMin is not None:
        temp = 'ge(xSectMin,{:.4f})&le(xSectMin,{:.4f})'.format(RCSMin[0],RCSMin[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSMax'     
    if RCSMax is not None:
        temp = 'ge(xSectMax,{:.4f})&le(xSectMax,{:.4f})'.format(RCSMax[0],RCSMax[1])
        params = _discos_buildin_filter(params,temp)
            
    # Filter parameters for 'RCSAvg'     
    if RCSAvg is not None:
        temp = 'ge(xSectAvg,{:.4f})&le(xSectAvg,{:.4f})'.format(RCSAvg[0],RCSAvg[1])
        params = _discos_buildin_filter(params,temp)

    # Filter parameters for 'ACTIVE'
    if ACTIVE is not None:
        if ACTIVE:
            temp = 'eq(active,"true")'
        else:
            temp = 'eq(active,"false")'
        params = _discos_buildin_filter(params, temp)

    # Sort in ascending order       
    if sort is None:    
        params['sort'] = 'satno'  
    else:
        if sort.__contains__('COSPAR_ID'):
            params['sort'] = 'cosparId'
        elif sort.__contains__('NORAD_ID'):
            params['sort'] = 'satno'    
        elif sort.__contains__('OBJECT_CLASS'):
            params['sort'] = 'objectClass'
        elif sort.__contains__('MISSION_TYPE'):
            params['sort'] = 'mission'
        elif sort.__contains__('MASS'):
            params['sort'] = 'mass'    
        elif sort.__contains__('SHAPE'):
            params['sort'] = 'shape'
        elif sort.__contains__('LENGTH'):
            params['sort'] = 'length'   
        elif sort.__contains__('HEIGHT'):
            params['sort'] = 'height'
        elif sort.__contains__('DEPTH'):
            params['sort'] = 'depth'
        elif sort.__contains__('DIAMETER'):
            params['sort'] = 'diameter'
        elif sort.__contains__('SPAN'):
            params['sort'] = 'span'
        elif sort.__contains__('RCSMin'):
            params['sort'] = 'xSectMin'
        elif sort.__contains__('RSCMax'):
            params['sort'] = 'xSectMax' 
        elif sort.__contains__('RCSAvg'):
            params['sort'] = 'xSectAvg'  
        elif sort.__contains__('DECAY_DATE'):
            params['sort'] = 'reentry.epoch'
        elif sort.__contains__('FIRST_EPOCH'):
            params['sort'] = 'firstEpoch'
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAID', 'OBJECT_CLASS', 'MASS', 'SHAPE', 'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RSCMax', 'RCSAvg', and 'DECAY_DATE'. Also, a negative sign '-' can be added to the option to sort in descending order.")        
                
        # Sort in descending order
        if sort[0] == '-': params['sort'] = '-' + params['sort']

    # Initialize the page parameter 
    params['page[number]'] = 1
    extract = []
    
    while True:
        params['page[size]'] = 100 # Number of entries on each page   
        response = requests.get(f'{URL}/api/objects',
            headers = {
            'Authorization': f'Bearer {token}',
            'DiscosWeb-Api-Version': '1',
            },params = params)

        doc = response.json()

        if response.ok:
            if not doc['data']: raise Exception('No entries found, please reset the filter parameters.')
            data = doc['data']
            for element in data:
                extract.append(element['attributes'])
            currentPage = doc['meta']['pagination']['currentPage']
            totalPages = doc['meta']['pagination']['totalPages']
            desc = 'CurrentPage {:s}{:3d}{:s} in TotalPages {:3d}'.format(Fore.GREEN,currentPage,Fore.RESET,totalPages)
            print(desc,end='\r')
            
            if currentPage < totalPages: 
                params['page[number]'] += 1
            else:
                break

            # If too much data is requested within a query, the website will respond with a
            # "TOO MANY REQUESTS" response and will not allow the token to be used
            # until the request timeout has occurred. 
            # In order to prevent this from happening, the tool will automatically pause
            # processing for half a minute after 20 pages of data have been requested. 
            # It will then resume downloading another 20 pages of data and pause again.
            # This will continue until all pages have been downloaded from the DISCOS website.
            if currentPage%20 == 0: sleep(30)    
        else:
            return doc['errors']
    
    # Rename the columns and readjust the order of the columns  
    old_column = ['height', 'xSectMax', 'name', 'satno', 'objectClass','mass', 'xSectMin', 'depth', 'xSectAvg', 'length', 'shape', 'cosparId','diameter', 'span','mission','firstEpoch','active']
    new_column = ['HEIGHT', 'RCSMax', 'OBJECT_NAME', 'NORAD_ID', 'OBJECT_CLASS', 'MASS', 'RCSMin[m2]', 'DEPTH', 'RCSAvg', 'LENGTH', 'SHAPE', 'COSPAR_ID','DIAMETER','SPAN','MISSION_TYPE','FIRST_EPOCH','ACTIVE']
    # units: MASS in [kg]; RCS in [m2]; DEPTH, LENGTH, and HEIGHT in [m]
    new_column_reorder = ['OBJECT_NAME','COSPAR_ID', 'NORAD_ID','OBJECT_CLASS','MISSION_TYPE','SHAPE','MASS','HBR','HEIGHT','LENGTH','DEPTH','DIAMETER','SPAN','RCSMin','RCSMax','RCSAvg','DECAY_DATE','FIRST_EPOCH','ACTIVE']
    print(extract)
    df = pd.DataFrame.from_dict(extract,dtype=object).rename(columns=dict(zip(old_column, new_column)), errors='raise')
    df = calculate_hbr(df)
    df = df.reindex(columns=new_column_reorder) 
    df = df.reset_index(drop=True)
    
    return df

def calculate_hbr1(df):
    """
    计算硬体半径（HBR），并将结果添加为 DataFrame 的一列。

    参数：
    df: pandas DataFrame，包含以下列：
        - 'SHAPE': 物体的形状描述
        - 'HEIGHT': 高度
        - 'LENGTH': 长度（对应于 MATLAB 代码中的 Width）
        - 'DEPTH': 深度
        - 'DIAMETER': 直径
        - 'SPAN': 跨距

    返回：
    df: pandas DataFrame，包含新增的 'HBR' 列。
    """
    # 创建一个新的 Series，用于存储 HBR，初始值为 NaN
    HBR = pd.Series(np.nan, index=df.index)

    # 将形状转换为小写，便于比较
    df['SHAPE_LOWER'] = df['SHAPE'].str.lower()

    # 提取所需的列
    shape = df['SHAPE_LOWER']
    x = df['LENGTH']
    y = df['HEIGHT']
    z = df['DEPTH']
    diam = df['DIAMETER']
    span = df['SPAN']

    # 创建掩码，标记形状为空的行
    mask_shape_empty = shape.isna() | (shape == '')

    # 创建掩码，标记非球形物体
    mask_non_sphere = ~shape.str.startswith('sphere', na=False) & ~mask_shape_empty

    # 第一种情况：x, y, z, span 都已知
    mask1 = mask_non_sphere & x.notna() & y.notna() & z.notna() & span.notna()
    val1 = np.sqrt(x**2 + y**2 + z**2) / 2
    val2 = span / 2
    HBR[mask1] = np.maximum(val1[mask1], val2[mask1])

    # 可选：如果需要更新形状描述（例如 'box' 变为 'Box with extra span'）
    mask_box = mask1 & (shape == 'box') & (val2 > val1)
    df.loc[mask_box, 'SHAPE'] = 'Box with extra span'

    # 第二种情况：形状包含 'cone' 或 'cyl'，且 y 和 diam 已知
    mask2 = mask_non_sphere & (shape.str.contains('cone', na=False) | shape.str.contains('cyl', na=False)) & y.notna() & diam.notna()
    mask_cone = mask2 & shape.str.contains('cone', na=False)
    mask_cyl = mask2 & shape.str.contains('cyl', na=False)

    val1_cone = np.sqrt(y**2 + (diam/2)**2) / 2
    val1_cyl = np.sqrt(y**2 + diam**2) / 2
    val1_mask2 = pd.Series(np.nan, index=df.index)
    val1_mask2[mask_cone] = val1_cone[mask_cone]
    val1_mask2[mask_cyl] = val1_cyl[mask_cyl]

    # 如果 span 已知，取较大值；否则，使用计算的 val1
    mask2_span_notna = mask2 & span.notna()
    HBR[mask2_span_notna] = np.maximum(val1_mask2[mask2_span_notna], span[mask2_span_notna]/2)
    mask2_span_na = mask2 & span.isna()
    HBR[mask2_span_na] = val1_mask2[mask2_span_na]

    # 第三种情况：x, y, z 已知，但不符合前两种情况
    mask3 = mask_non_sphere & x.notna() & y.notna() & z.notna() & ~mask1 & ~mask2
    HBR[mask3] = np.sqrt(x[mask3]**2 + y[mask3]**2 + z[mask3]**2) / 2

    # 第四种情况：span 已知，但不符合前三种情况
    mask4 = mask_non_sphere & span.notna() & ~mask1 & ~mask2 & ~mask3
    HBR[mask4] = span[mask4] / 2

    # 对于球形和椭球形物体
    mask_sphere = shape.str.startswith('sphere', na=False) & ~mask_shape_empty
    max_dim = df[['LENGTH', 'HEIGHT', 'DEPTH', 'DIAMETER', 'SPAN']].max(axis=1, skipna=True)
    HBR[mask_sphere] = max_dim[mask_sphere] / 2

    # 将 HBR 列添加到 DataFrame 中
    df['HBR'] = HBR

    # 删除辅助列
    df.drop(columns=['SHAPE_LOWER'], inplace=True)

    return df

def _celestrak_query1(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,OWNER=None,TLE_STATUS=None,sort=None):
    """
    Given the orbital constraints of a space object, query the qualified space objects from the [CELESTRAK](https://celestrak.com) database.

    Usage:
        satcatalog_df = celestrak_query(DECAYED=False,MEAN_ALT=[400,900])

    Inputs:
        COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored. 
        NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
        PAYLOAD -> [bool, optional, default = None] Whether an object is payload or not. If True, the object is a payload; if False, not a payload; if None, this option is ignored.
        DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
        DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
        PERIOD -> [list of float, optional, default = None] Orbital period[minutes] range of a space object; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
        INCLINATION -> [list of float, optional, default = None] Range of inclination[degrees] of a space object; it must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
        APOGEE -> [list of float, optional, default = None] Range of Apogee Altitude[km]; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
        PERIGEE -> [list of float, optional, default = None] Range of Perigee Altitude[km]; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
        MEAN_ALT -> [list of float, optional, default = None] Mean Altitude[km] of objects; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
        ECC -> [list of float, optional, default = None] Range of Eccentricity; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
        OWNER -> [str or list of str, optional, default = None] Ownership of a space object; and country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
        TLE_STATUS -> [bool, optional, default = None] Whether a TLE is valid. If False, it means No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
        sort -> [str, optional, default = None] Sort according to attributes of a spatial object, such as MEAN_ALT; available options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC',and 'OWNER'.
        If the attribute is prefixed with a '-', such as '-DecayDate', it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    
    Outputs:
        satcatalog_df -> Data frame containing the selected spatial objects
    """  

    # Load and update the satcat files from the [CELESTRAK](https://celestrak.com) database.
    data_prepare.satcat_load()
    satcat_file = data_prepare.sc_file

    data = pd.read_csv(satcat_file) 
    columns_dict = {'OBJECT_ID': 'COSPAR_ID', 'NORAD_CAT_ID': 'NORAD_ID'}
    data.rename(columns=columns_dict, inplace=True)
    # unit description : 'PERIOD' in [min],'INCLINATION' in [deg], 'APOGEE' in [km],'PERIGEE' in [km],'RCS' in [m2]

    Mean_Alltitude = (data['APOGEE'] + data['PERIGEE'])/2 # Compute the mean altitude
    Eccentricity = (data['APOGEE'] - data['PERIGEE'])/(Mean_Alltitude + Const.Re_V)/2 

    # Add column to dataframe
    data['MEAN_ALT'] = Mean_Alltitude
    data['ECC'] = Eccentricity
    full_of_true = np.ones_like(Mean_Alltitude,dtype=bool)
    
    # Set filter for 'COSPAR_ID' 
    if COSPAR_ID is not None:
        if type(COSPAR_ID) in [str,list]:
            COSPARID_flag = np.in1d(data['COSPAR_ID'],COSPAR_ID,assume_unique=True)
        else:
            raise Exception('Type of COSPAR_ID should be in str or list of str.')             
    else:
        COSPARID_flag = full_of_true
    
    # Set filter for 'NORADID' 
    if NORAD_ID is not None:
        if type(NORAD_ID) is int:
            NORADID_flag = np.in1d(data['NORAD_ID'],NORAD_ID,assume_unique=True)
        elif type(NORAD_ID) is str: 
            if '.' in NORAD_ID: 
                NORAD_ID = np.loadtxt(NORAD_ID,dtype = int)  
            else:
                NORAD_ID = int(NORAD_ID)
            NORADID_flag = np.in1d(data['NORAD_ID'],NORAD_ID,assume_unique=True)
        elif type(NORAD_ID) is list:
            NORADID_list = np.array(NORAD_ID).astype(int)       
            NORADID_flag = np.in1d(data['NORAD_ID'],NORADID_list,assume_unique=True)        
        else:
            raise Exception('Type of NORAD_ID should be in int, str, list of int, or list of str.')             
    else:
        NORADID_flag = full_of_true   
    
    # Set filter for 'OBJECT_TYPE'
    Payload_flag = data['OBJECT_TYPE'] == 'PAY'

    if PAYLOAD is None:
        Payload_flag = full_of_true
    else:
        if not PAYLOAD: Payload_flag = ~Payload_flag
        
    # Set filter for 'DECAYED' 
    Decayed_flag = data['OPS_STATUS_CODE'] == 'D'

    if DECAYED is None:
        Decayed_flag = full_of_true
    else:
        if not DECAYED: Decayed_flag = ~Decayed_flag  
        
    # Set filter for 'DECAY_DATE'
    if DECAY_DATE is not None:
        DecayDate_flag = (data['DECAY_DATE'] > DECAY_DATE[0]) & (data['DECAY_DATE'] < DECAY_DATE[1])
    else:
        DecayDate_flag = full_of_true

    # Set filter for 'PERIOD'
    if PERIOD is not None:
        OrbitalPeriod_flag = (data['PERIOD'] > PERIOD[0]) & (data['PERIOD'] < PERIOD[1])
    else:
        OrbitalPeriod_flag = full_of_true   

    # Set filter for 'INCLINATION'
    if INCLINATION is not None:
        Inclination_flag = (data['INCLINATION'] > INCLINATION[0]) & (data['INCLINATION'] < INCLINATION[1])
    else:
        Inclination_flag = full_of_true
       
    # Set filter for 'APOGEE'
    if APOGEE is not None:
        ApoAlt_flag = (data['APOGEE'] > APOGEE[0]) & (data['APOGEE'] < APOGEE[1])
    else:
        ApoAlt_flag = full_of_true
        
    # Set filter for 'PERIGEE'
    if PERIGEE is not None:
        PerAlt_flag = (data['PERIGEE'] > PERIGEE[0]) & (data['PERIGEE'] < PERIGEE[1])
    else:
        PerAlt_flag = full_of_true
        
    # Set filter for 'MEAN_ALT'
    if MEAN_ALT is not None:
        MeanAlt_flag = (Mean_Alltitude > MEAN_ALT[0]) & (Mean_Alltitude < MEAN_ALT[1])
    else:
        MeanAlt_flag = full_of_true    

    # Set filter for 'ECC'
    if ECC is not None:
        Ecc_flag = (Eccentricity > ECC[0]) & (Eccentricity < ECC[1])
    else:
        Ecc_flag = full_of_true       

    # Set filter for 'Country'
    if OWNER is not None:
        if type(OWNER) in [str,list]:
            Owner_flag = np.in1d(data['OWNER'],OWNER)
        else:
            raise Exception('Type of OWNER should be in str or list of str.') 
    else:
        Owner_flag = full_of_true   

    # Set filter for TLE status
    OrbitalStatus_flag = data['OPS_STATUS_CODE'].isnull()

    if TLE_STATUS is None:
        OrbitalStatus_flag = full_of_true
    else:
        if not TLE_STATUS: OrbitalStatus_flag = ~OrbitalStatus_flag

    # Combine filters
    combined_flag = COSPARID_flag & NORADID_flag & Payload_flag & Decayed_flag & DecayDate_flag & OrbitalPeriod_flag & Inclination_flag & ApoAlt_flag & PerAlt_flag & MeanAlt_flag & Ecc_flag & Owner_flag & OrbitalStatus_flag
    df = data[combined_flag]

    # Eeadjust the order of the columns 
    column_reorder = ['OBJECT_NAME','COSPAR_ID', 'NORAD_ID','OBJECT_TYPE','OPS_STATUS_CODE','DECAY_DATE',\
                      'PERIOD', 'INCLINATION','APOGEE','PERIGEE','MEAN_ALT','ECC',\
                      'LAUNCH_DATE','LAUNCH_SITE','RCS','OWNER','OPS_STATUS_CODE','ORBIT_CENTER','ORBIT_TYPE']
    df = df.reindex(columns=column_reorder)
    if TLE_STATUS: df = df.drop(columns=['OPS_STATUS_CODE'])
      
    # Sort     
    if sort is None:    
        df = df.sort_values(by=['NORAD_ID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
    
        if sort.__contains__('COSPAR_ID'):
            df = df.sort_values(by=['COSPAR_ID'],ascending=ascending_flag)
        elif sort.__contains__('NORAD_ID'):
            df = df.sort_values(by=['NORAD_ID'],ascending=ascending_flag)   
        elif sort.__contains__('DECAY_DATE'):
            df = df.sort_values(by=['DECAY_DATE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIOD'):
            df = df.sort_values(by=['PERIOD'],ascending=ascending_flag)    
        elif sort.__contains__('INCLINATION'):
            df = df.sort_values(by=['INCLINATION'],ascending=ascending_flag) 
        elif sort.__contains__('APOGEE'):
            df = df.sort_values(by=['APOGEE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIGEE'):
            df = df.sort_values(by=['PERIGEE'],ascending=ascending_flag) 
        elif sort.__contains__('MEAN_ALT'):
            df = df.sort_values(by=['MEAN_ALT'],ascending=ascending_flag) 
        elif sort.__contains__('ECC'):
            df = df.sort_values(by=['ECC'],ascending=ascending_flag)     
        elif sort.__contains__('LAUNCH_DATE'):
            df = df.sort_values(by=['LAUNCH_DATE'],ascending=ascending_flag) 
        elif sort.__contains__('LAUNCH_SITE'):
            df = df.sort_values(by=['LAUNCH_SITE'],ascending=ascending_flag)     
        elif sort.__contains__('RCS'):
            df = df.sort_values(by=['RCS'],ascending=ascending_flag)    
        elif sort.__contains__('OWNER'):
            df = df.sort_values(by=['OWNER'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', 'LAUNCH_DATE', 'LAUNCH_SITE', 'RCS', and 'OWNER'. Also, a negative sign '-' can be added ahead to the option to sort in descending order.")
    df = df.reset_index(drop=True)

    return df

def parseQSMagFile1():
    """
    Get the noradid and standard(intrinsic) magnitude for space objects by reading and parsing the qs.mag file.
    """

    # Load and update the QSMag files from https://www.prismnet.com/~mmccants/programs/qsmag.zip
    data_prepare.qsmag_load()
    qsfile = data_prepare.qs_file

    qsmag = np.genfromtxt(qsfile,skip_header=1,skip_footer=1,delimiter=[5,28,5],dtype=(int,str,float)) 
    df_qsmag = pd.DataFrame(qsmag).drop(columns=['f1']).rename(columns={"f0": "NORAD_ID", "f2": "StdMag"})
    return df_qsmag

def _objects_query1(COSPAR_ID=None,NORAD_ID=None,PAYLOAD=None,OBJECT_CLASS=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,TLE_STATUS=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,OWNER=None,sort=None):
    """
    Given the geometric and orbital constraints of a space object, query the qualified space objects from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.

    Usage: 
        satcatalog_df = objects_query(PAYLOAD=False,DECAYED=False,MEAN_ALT=[400,900],RCSAvg=[5,15])

    Inputs:
        COSPAR_ID -> [str or list of str, optional, default = None] object IDs defined by the Committee On SPAce Research; if None, this option is ignored. 
        NORAD_ID -> [int, str, list, or filename(such as 'noradids.txt'), optional, default = None] object IDs defined by the North American Aerospace Defense Command; if None, this option is ignored.
        OBJECT_CLASS -> [str, list of str, optional, default = None] Classification of objects; available options are 'Payload', 'Payload Debris', 'Payload Fragmentation Debris', 
        'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris', 'Rocket Mission Related Object', 'Other Mission Related Object','Other Debris', Unknown', or any combination of them, 
        for example, ['Rocket Body', 'Rocket Debris', 'Rocket Fragmentation Debris']; If None, this option is ignored.  
        DECAYED -> [bool, optional, default = None] Whether an object is  decayed(re-entry) or not; If False, the object is still in orbit by now; if True, then decayed; if None, this option is ignored.
        DECAY_DATE -> [list of str, optional, default = None] Date range of decay; it must be in form of ['date1','date2'], such as ['2019-01-05','2020-05-30']; if None, then this option is ignored.
        PERIOD -> [list of float, optional, default = None] Orbital period[minutes] range of a space object; it must be in form of [period1,period2], such as [100.0,200.0]; if None, this option is ignored.  
        INCLINATION -> [list of float, optional, default = None] Range of inclination[degrees] of a space object; it must be in form of [inc1,inc2], such as [45.0,80.0]; if None, this option is ignored.  
        APOGEE -> [list of float, optional, default = None] Range of Apogee Altitude[km]; it must be in form of [apoalt1,apoalt2], such as [800.0,1400.0]; if None, this option is ignored.  
        PERIGEE -> [list of float, optional, default = None] Range of Perigee Altitude[km]; it must be in form of [peralt1,peralt2], such as [300.0,400.0]; if None, this option is ignored.  
        MEAN_ALT -> [list of float, optional, default = None] Mean Altitude[km] of objects; it must be in form of [meanalt1,meanalt2], such as [300.0,800.0]; if None, then option is ignored. 
        ECC -> [list of float, optional, default = None] Range of Eccentricity; it must be in form of [ecc1,ecc2], such as [0.01,0.2]; if None, then option is ignored.   
        TLE_STATUS -> [bool, optional, default = None] Whether a TLE is valid. If False, it means No Current Elements, No Initial Elements, or No Elements Available; if None, this option is ignored.
        MASS -> [list of float, optional, default = None] Mass[kg] range of an object; it must be in form of [m1,m2], such as [5.0,10.0]; if None, this option is ignored.
        SHAPE -> [str or list of str, optional, default = None] Shape of an object; the usual choices include 'Cyl', 'Sphere', 'Cone', 'Dcone', Pan', 'Ell', 'Dish', 'Cable', 'Box', 'Rod', 'Poly', 'Sail', 'Ant', 
        'Frust', 'Truss', 'Nozzle', and 'lrr'. Any combination of them is also supported, for examle, ['Cyl', 'Sphere', 'Pan'] means 'or', and ['Cyl', 'Sphere', 'Pan', '+'] means 'and'; If None, this option is ignored.  
        LENGTH -> [list of float, optional, default = None] Length[m] range of an object; it must be in form of [l1,l2], such as [5.0,10.0]; if None, this option is ignored.
        HEIFHT -> [list of float, optional, default = None] Height[m] range of an object; it must be in form of [h1,h2], such as [5.0,10.0]; if None, this option is ignored.
        DEPTH -> [list of float, optional, default = None] Depth[m] range of an object; it must be in form of [d1,d2], such as [5.0,10.0]; if None, this option is ignored.
        RCSMin -> [list of float, optional, default = None] Minimum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        RCSMax -> [list of float, optional, default = None] Maximum Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        RCSAvg -> [list of float, optional, default = None] Average Radar Cross Section(RCS)[m2] of an object; if None, this option is ignored.
        OWNER -> [str or list of str, optional, default = None] Ownership of a space object; and country codes/names can be found at http://www.fao.org/countryprofiles/iso3list/en/; if None, this option is ignored.
        sort -> [str, optional, default = None] Sort according to attributes of a spatial object, such as by mass; available options include 'COSPAR_ID', NORAD_ID', 'OBJECT_CLASS', 'MASS', 'DECAY_DATE', 'SHAPE', 
        'LENGTH', 'HEIGHT', 'DEPTH', 'RCSMin', 'RSCMax', 'RCSAvg', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', and 'OWNER'.
        If the attribute is prefixed with a '-', such as "-RCSAvg", it will be sorted in descending order. If None, the spatial objects are sorted by NORADID by default.
    
    Outputs:
        satcatalog_df -> Data frame containing the selected spatial objects
    """ 
    # Query space targets from the CELESTRAK database
    df_celestrak = _celestrak_query(COSPAR_ID,NORAD_ID,PAYLOAD,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,OWNER,TLE_STATUS).drop('OBJECT_NAME',axis=1)
    # Query space targets from the DISCOS database
    noradids = list(df_celestrak['NORAD_ID'])
    if len(noradids) > 1000: noradids = NORAD_ID
    print('Go through the DISCOS database ... ')    
    df_discos = _discos_query(COSPAR_ID,noradids,OBJECT_CLASS,PAYLOAD,DECAYED,DECAY_DATE,MASS,SHAPE,LENGTH,HEIGHT,DEPTH,RCSMin,RCSMax,RCSAvg).dropna(subset=['NORAD_ID'])

    # Merge the CELESTRAK database and the DISCOS database
    df = pd.merge(df_celestrak, df_discos, on=['COSPAR_ID','NORAD_ID'],validate="one_to_one")

    # Merge the QSMAG database
    df_qsmag = parseQSMagFile()
    df = pd.merge(df, df_qsmag, on=['NORAD_ID'],how='left',validate="one_to_one")

    # Remove unwanted columns and readjust the order of the columns 
    df = df.drop(['RCS'],axis=1)
    column_reorder = ['OBJECT_NAME','COSPAR_ID','NORAD_ID','OBJECT_CLASS','OPS_STATUS_CODE','DECAY_DATE',\
                      'PERIOD', 'INCLINATION','APOGEE', 'PERIGEE','MEAN_ALT','ECC','OPS_STATUS_CODE','ORBIT_CENTER','ORBIT_TYPE',\
                      'MASS','SHAPE','LENGTH', 'HEIGHT','DEPTH','RCSMin', 'RCSMax', 'RCSAvg','StdMag',\
                      'LAUNCH_DATE','LAUNCH_SITE','OWNER']                                 
    df = df.reindex(columns=column_reorder)  
    if TLE_STATUS: df = df.drop(columns=['OPS_STATUS_CODE'])
         
    # Sort
    if sort is None:    
        df = df.sort_values(by=['NORAD_ID'])
    else:
        if sort[0] == '-': 
            ascending_flag = False
        else:
            ascending_flag = True
        
        if sort.__contains__('COSPAR_ID'):
            df = df.sort_values(by=['COSPAR_ID'],ascending=ascending_flag)
        elif sort.__contains__('NORAD_ID'):
            df = df.sort_values(by=['NORAD_ID'],ascending=ascending_flag)  
        elif sort.__contains__('DECAY_DATE'):
            df = df.sort_values(by=['DECAY_DATE'],ascending=ascending_flag)  
        elif sort.__contains__('PERIOD'):
            df = df.sort_values(by=['PERIOD'],ascending=ascending_flag)    
        elif sort.__contains__('INCLINATION'):
            df = df.sort_values(by=['INCLINATION'],ascending=ascending_flag) 
        elif sort.__contains__('APOGEE'):
            df = df.sort_values(by=['APOGEE'],ascending=ascending_flag)   
        elif sort.__contains__('PERIGEE'):
            df = df.sort_values(by=['PERIGEE'],ascending=ascending_flag) 
        elif sort.__contains__('MEAN_ALT'):
            df = df.sort_values(by=['MEAN_ALT'],ascending=ascending_flag) 
        elif sort.__contains__('ECC'):
            df = df.sort_values(by=['ECC'],ascending=ascending_flag)              
        elif sort.__contains__('MASS'):
            df = df.sort_values(by=['MASS'],ascending=ascending_flag)    
        elif sort.__contains__('LENGTH'):
            df = df.sort_values(by=['LENGTH'],ascending=ascending_flag)
        elif sort.__contains__('HEIGHT'):
            df = df.sort_values(by=['HEIGHT'],ascending=ascending_flag)
        elif sort.__contains__('DEPTH'):
            df = df.sort_values(by=['DEPTH'],ascending=ascending_flag)   
        elif sort.__contains__('RCSMin'): 
            df =  df.sort_values(by=['RCSMin'],ascending=ascending_flag)  
        elif sort.__contains__('RCSMax'): 
            df =  df.sort_values(by=['RCSMax'],ascending=ascending_flag)    
        elif sort.__contains__('RCSAvg'): 
            df =  df.sort_values(by=['RCSAvg'],ascending=ascending_flag) 
        elif sort.__contains__('StdMag'):
            df = df.sort_values(by=['StdMag'],ascending=ascending_flag)          
        elif sort.__contains__('LAUNCH_DATE'):
            df = df.sort_values(by=['LAUNCH_DATE'],ascending=ascending_flag)   
        elif sort.__contains__('OWNER'):
            df = df.sort_values(by=['OWNER'],ascending=ascending_flag)
        else:
            raise Exception("Avaliable options include 'COSPAR_ID', NORAD_ID', 'DECAY_DATE', 'PERIOD', 'INCLINATION', \
                'APOGEE', 'PERIGEE', 'MEAN_ALT', 'ECC', 'MASS','LENGTH','DEPTH','HEIGHT', 'RCSMin','RCSMax', 'RCSAvg',\
                'StdMag','LAUNCH_DATE',and 'OWNER'. Also, a negative sign '-' can be added to the option to sort in descending order.")
    df = df.reset_index(drop=True)
    return df