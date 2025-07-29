import os,re
from datetime import datetime,timezone
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import random
from collections import Counter

from .query import _discos_query,_celestrak_query,_objects_query
from .data_download import download_tle

class SatCatalog(object):
    """
    SatCatalog class: catalog toolset for space object querying and analysis.

    Methods：
        discos_query(...)
            Query space objects from the ESA DISCOS database using geometric and/or physical constraints.
        celestrak_query(...)
            Query space objects from the CELESTRAK database using orbital constraints.
        objects_query(...)
            Joint query: filter by both orbital (CELESTRAK) and physical (DISCOS) constraints, and merge results.
        to_csv(filename)
            Save the current catalog DataFrame to a CSV file.
        from_csv(filename)
            Load a catalog DataFrame from a CSV file.
        hist2d(x, y, ...)
            Draw a 2D histogram for catalog columns.
        hist1d(x, ...)
            Draw a 1D histogram for a catalog column.
        pie(x, ...)
            Draw a pie chart for a catalog column.
        get_tle(...)
            Retrieve TLE (Two-Line Element) data from SPACETRACK for catalog objects.
    """
    def __init__(self, df, mode):
        """
        Initialize a SatCatalog instance.

        Inputs:
            df -> [pandas.DataFrame] Catalog data (rows = objects, columns = attributes).
            mode -> [str] Catalog mode, e.g., 'discos_catalog', 'celestrak_catalog', etc.
        """
        self.df = df
        self._mode = mode

    def __repr__(self):
        """
        Return a summary string describing the catalog.

        Returns:
            Human-readable summary including object count and catalog mode.
        """
        n = len(self.df)
        return f"<SatCatalog: {n} objects, MODE='{self._mode}'>"

    @staticmethod
    def discos_query(NORAD_ID=None,COSPAR_ID=None,OBJECT_CLASS=None,MISSION_TYPE=None,PAYLOAD=None,DECAYED=None,
                     DECAY_DATE=None,FIRST_EPOCH=None,MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,
                     DIAMETER=None,SPAN=None,RCSMin=None,RCSMax=None,RCSAvg=None,ACTIVE=None,sort=None):
        """
        Query the ESA DISCOS (Database and Information System Characterising Objects in Space) catalog
        for space objects matching specified geometric, physical, and status constraints.

        Inputs:
            NORAD_ID -> [int, str, list, or str (filename), optional] One or more NORAD IDs, or a filename (e.g. 'noradids.txt') containing NORAD IDs (one per line).
            COSPAR_ID -> [str or list of str, optional] One or more COSPAR IDs (International Designators).
            OBJECT_CLASS -> [str or list of str, optional] Classification of objects.
                Available options include:
                    'Payload', 'Payload Debris', 'Payload Fragmentation Debris',
                    'Payload Mission Related Object', 'Rocket Body', 'Rocket Debris',
                    'Rocket Fragmentation Debris', 'Rocket Mission Related Object',
                    'Other Mission Related Object', 'Other Debris', 'Unknown'.
                Any combination is supported (e.g. ['Rocket Body', 'Rocket Debris']).
            MISSION_TYPE -> [str or list of str, optional] Mission type(s).
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
            DECAY_DATE -> [list of str, optional] Date range for decay epoch, as ['YYYY-MM-DD','YYYY-MM-DD'] (inclusive).
            FIRST_EPOCH -> [list of str, optional] Date range for first epoch (launch), as ['YYYY-MM-DD','YYYY-MM-DD'] (inclusive).
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
            catalog -> [SatCatalog] SatCatalog instance containing the query results (as a DataFrame).
                The DataFrame includes attributes such as NORAD_ID, COSPAR_ID, OBJECT_CLASS,
                physical dimensions, mass, RCS, etc., according to the query and database contents.
        Notes:
            - All filter arguments are optional. If no arguments are given, the full DISCOS catalog is returned (may be large).
            - The returned SatCatalog can be saved, plotted, or further filtered.
            - If too many pages are requested, automatic throttling is applied (30s pause after every 20 pages).
            - All size and RCS ranges are inclusive and use SI units.
            - See https://discosweb.esoc.esa.int for catalog field definitions.
        """
        df = _discos_query(COSPAR_ID, NORAD_ID, OBJECT_CLASS, MISSION_TYPE, PAYLOAD,
                          DECAYED, DECAY_DATE, FIRST_EPOCH, MASS, SHAPE, LENGTH,
                          HEIGHT, DEPTH, DIAMETER, SPAN, RCSMin, RCSMax, RCSAvg,
                          ACTIVE, sort)
        mode = 'discos_catalog'
        return SatCatalog(df,mode)

    @staticmethod
    def celestrak_query(NORAD_ID=None,COSPAR_ID=None,PAYLOAD=None,DECAYED=None,DECAY_DATE=None,PERIOD=None,
                        INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,OWNER=None,TLE_STATUS=None,sort=None):
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
            catalog -> [SatCatalog] SatCatalog instance containing the query results as a DataFrame.
                Typical columns include COSPAR_ID, NORAD_ID, PERIOD, INCLINATION, APOGEE, PERIGEE,
                MEAN_ALT, ECC, OBJECT_TYPE, OPS_STATUS_CODE, LAUNCH_DATE, OWNER, and more.
        Notes:
            - All filter arguments are optional; if none are specified, the full CELESTRAK catalog is returned.
            - The returned SatCatalog can be saved, visualized, or further filtered using other methods.
            - Use the `sort` parameter to specify sorting of results by any supported attribute.
            - 'PERIOD' is in minutes, 'INCLINATION' in degrees, 'APOGEE'/'PERIGEE'/'MEAN_ALT' in km, 'ECC' is dimensionless.
            - Input ranges [min, max] are inclusive.
            - See https://celestrak.com/satcat/ for catalog field definitions and value conventions.
        """
        df = _celestrak_query(COSPAR_ID,NORAD_ID,PAYLOAD,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,OWNER,TLE_STATUS,sort)
        mode = 'celestrak_catalog'
        return SatCatalog(df,mode)

    @staticmethod
    def objects_query(NORAD_ID=None,COSPAR_ID=None,PAYLOAD=None,OBJECT_CLASS=None,DECAYED=None,DECAY_DATE=None,
                      PERIOD=None,INCLINATION=None,APOGEE=None,PERIGEE=None,MEAN_ALT=None,ECC=None,TLE_STATUS=None,
                      MASS=None,SHAPE=None,LENGTH=None,HEIGHT=None,DEPTH=None,RCSMin=None,RCSMax=None,RCSAvg=None,OWNER=None,sort=None):
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
            catalog -> [SatCatalog] SatCatalog instance containing the merged query results as a DataFrame.
                Columns include orbital parameters (PERIOD, INCLINATION, APOGEE, PERIGEE, MEAN_ALT, ECC, etc.),
                physical and geometric attributes (MASS, SHAPE, LENGTH, HEIGHT, DEPTH, RCS, etc.), owner, status codes,
                and photometric standard magnitude (`StdMag`) if available.
        Notes:
            - All filters are optional. If too many objects are matched from CELESTRAK, DISCOS query is automatically limited for efficiency.
            - The result combines all available orbital and physical fields from both catalogs.
            - Use `sort` to control result order. The returned SatCatalog supports export, visualization, or further analysis.
            - Ranges [min, max] are inclusive; all units are SI (km, deg, min, kg, m^2, etc).
            - See https://discosweb.esoc.esa.int and https://celestrak.com/satcat/ for field definitions.
        """
        df = _objects_query(COSPAR_ID,NORAD_ID,PAYLOAD,OBJECT_CLASS,DECAYED,DECAY_DATE,PERIOD,INCLINATION,APOGEE,PERIGEE,MEAN_ALT,ECC,TLE_STATUS,MASS,SHAPE,LENGTH,HEIGHT,DEPTH,RCSMin,RCSMax,RCSAvg,OWNER,sort)
        mode = 'objects_catalog'
        return SatCatalog(df,mode) 

    def to_csv(self,dir_catalog='satcatalogs'):
        """
        Save the query results to a csv file.

        Inputs:
            dir_catalog -> [str, optional, default='satcatalogs'] Directory where the CSV file will be saved.
        Returns:
            file_catalog -> [str] File path of the saved CSV file.
        """
        df = self.df
        mode = self._mode

        os.makedirs(dir_catalog, exist_ok=True)

        # Use current UTC date string in YYYYMMDD format
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        file_catalog = os.path.join(dir_catalog, f'{mode}_{date_str}.csv')
        df.to_csv(file_catalog, index=False)

        return file_catalog

    @staticmethod
    def from_csv(csv_file):
        """
        Load a csv file that records query results.

        Examples:
            >>> satcat = SatCatalog.from_csv('satcatalogs/celestrak_catalog_20240701.csv')
            >>> print(satcat)
            <SatCatalog: 1273 objects, mode='celestrak_catalog'>
        Inputs:
            csv_file -> [str] Path to the csv file
        Returns:
            satcatalog -> [SatCatalog] Instance of SatCatalog containing the catalog DataFrame.
            The catalog 'mode' is automatically determined from the file name if it follows the convention '<mode>_<YYYYMMDD>.csv'.
        """
        df = pd.read_csv(csv_file)
        # Parse mode from filename: e.g. 'satcatalogs/discos_catalog_20240706.csv' => 'discos_catalog'
        match = re.search(r'([a-zA-Z0-9_]+)_\d{8}\.csv$', os.path.basename(csv_file))
        mode = match.group(1) if match else None
        return SatCatalog(df, mode)

    def hist2d(self,x,y,num_bins=50,dir_fig='satcatalogs'):
        """
        Draw a 2D histogram (density map) of two catalog columns.

        Examples:
            >>> figfile = satcatalog.hist2d('MEAN_ALT', 'ECC')
            >>> print(figfile)
            satcatalogs/MEAN_ALT-ECC.png
        Inputs:
            x -> [str] Column name for the x-axis (must exist in self.df).
            y -> [str] Column name for the y-axis (must exist in self.df).
            num_bins -> [int, optional, default=50] Number of bins for each axis.
            dir_fig -> [str, optional, default='satcatalogs'] Directory in which to save the histogram image.
        Returns:
            file_fig -> [str] Full path to the saved histogram image (PNG).
        """
        df = self.df
        os.makedirs(dir_fig, exist_ok=True)

        fig, ax = plt.subplots(tight_layout=True,dpi=300)

        # the histogram of the data
        df_x,df_y = df[x],df[y]

        hist = ax.hist2d(df_x, df_y,bins=num_bins,density=True,norm=colors.LogNorm(),cmap='Oranges')
        ax.set_xlabel(str(x))
        ax.set_ylabel(str(y))
        file_fig = os.path.join(dir_fig, f'{x}-{y}.png')
        plt.savefig(file_fig,bbox_inches='tight')
        plt.close(fig)
        return file_fig  

    def hist1d(self,xs,num_bins=50,dir_fig='satcatalogs'):
        """
        Draw a 1D histogram for one or more columns.

        Usage:
            >>> satcatalog.hist1d('StdMag')
            satcatalogs/StdMag.png
        Inputs:
            xs -> [str or list of str] Single column name or list of column names (must exist in self.df).
            num_bins -> [int, optional, default=50] Number of bins for the axis.
            dir_fig -> [str, optional, default='satcatalogs'] Directory in which to save the histogram image.
        Returns:
            file_fig -> [str] Full path to the saved histogram image (PNG).
        """
        df = self.df
        os.makedirs(dir_fig,exist_ok=True)

        # Allow xs as str or list of str
        if isinstance(xs, str):
            xs = [xs]

        if len(xs) > 1:
            n_xs = len(xs)
            fig, axes = plt.subplots(1, n_xs, dpi=300)
            if n_xs == 1:
                axes = [axes]
            fig.tight_layout(pad=2)
            for i, col in enumerate(xs):
                df_x = df[col]
                ax = axes[i]
                if col in ['LAUNCH_DATE', 'DECAY_DATE']:
                    df_x = pd.to_datetime(df_x, errors='coerce')
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                    ax.tick_params(axis='x', rotation=30)
                elif col == 'MEAN_ALT':
                    ax.tick_params(axis='x', rotation=30)
                n, bins, patches = ax.hist(df_x.dropna(), num_bins)
                ax.set_xlabel(str(col))
            file_fig = os.path.join(dir_fig, f"{'_'.join(xs)}.png")
        else:
            col = xs[0]
            fig, ax = plt.subplots(1, 1, dpi=300)
            fig.tight_layout(pad=2)
            df_x = df[col]
            if col in ['LAUNCH_DATE', 'DECAY_DATE']:
                df_x = pd.to_datetime(df_x, errors='coerce')
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax.tick_params(axis='x', rotation=30)
            n, bins, patches = ax.hist(df_x.dropna(), num_bins)
            ax.set_xlabel(str(col))
            file_fig = os.path.join(dir_fig, f"{col}.png")

        plt.savefig(file_fig, bbox_inches='tight')
        plt.close(fig)
        return file_fig

        # if type(xs) is list and len(xs) > 1:
        #     n_xs = len(xs)
        #
        #     fig, ax = plt.subplots(1, n_xs,dpi=300)
        #     fig.tight_layout(pad=2)
        #
        #     for i in range(n_xs):
        #         df_x = df[xs[i]]
        #         if xs[i] in ['LAUNCH_DATE','DECAY_DATE']:
        #             df_x = df_x.astype("datetime64")
        #             ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        #             ax[i].tick_params(axis='x', rotation=30)
        #         elif xs[i] == 'MEAN_ALT':
        #             ax[i].tick_params(axis='x', rotation=30)
        #         n, bins, patches = ax[i].hist(df_x, num_bins)
        #         ax[i].set_xlabel('{:s}'.format(xs[i]))
        #     file_fig = dir_fig+'{:s}.png'.format('_'.join(xs))
        # else:
        #     fig, ax = plt.subplots(1, 1,dpi=300)
        #     fig.tight_layout(pad=2)
        #
        #     if type(xs) is list: xs = xs[0]
        #
        #     df_x = df[xs]
        #
        #     if xs in ['LAUNCH_DATE','DECAY_DATE']:
        #         df_x = df_x.astype("datetime64")
        #         ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        #         ax.tick_params(axis='x', rotation=30)
        #
        #     n, bins, patches = ax.hist(df_x, num_bins)
        #     ax.set_xlabel('{:s}'.format(xs))
        #     file_fig = dir_fig+'{:s}.png'.format(xs)
        #
        # plt.savefig(file_fig,bbox_inches = 'tight')
        #
        # return file_fig


    def pie(self,x,prominent=None,cutoff=50,dir_fig='satcatalogs'):
        """
        Draw a pie chart for a categorical column in the catalog.

        Usage:
            >>> satcatalog.pie('OWNER', cutoff=100)
            satcatalogs/OWNER.png
        Inputs:
            x -> [str] Column name for the pie chart. Must be one of ['OWNER', 'LAUNCH_SITE', 'OBJECT_CLASS', 'SHAPE'].
            prominent -> [str,optional,default=None] The category to highlight (explode) in the pie chart. If None, a random category will be highlighted.
            cutoff -> [int,default=50] Categories with fewer than `cutoff` entries are grouped into 'Other'.
            dir_fig -> [str,optional,default='satcatalogs'] Directory to save the pie chart PNG file.
        Returns:
            file_fig -> [str] Path of the saved pie chart image.
        Notes:
            - If `prominent` is not specified, a random category will be highlighted in the pie chart.
            - Only columns ['OWNER', 'LAUNCH_SITE', 'OBJECT_CLASS', 'SHAPE'] are supported for pie chart visualization.
        """
        os.makedirs(dir_fig,exist_ok=True)

        if x not in ['OWNER','LAUNCH_SITE','OBJECT_CLASS','SHAPE']:
            raise Exception("Pie chart variable must be one of ['OWNER', 'LAUNCH_SITE', 'OBJECT_CLASS', 'SHAPE'].")

        df_x = self.df[x]

        # Count frequencies for each category
        x_fre = pd.DataFrame(Counter(df_x).items(),columns=[x,'fre'])
        # Filter categories above cutoff; others grouped as 'Other'
        condition = x_fre['fre'] > cutoff
        most_fre = x_fre[condition]

        other_sum = x_fre[~condition]['fre'].sum()
        other_fre = pd.DataFrame({x: ['Other'], 'fre': [other_sum]})
        x_fre = pd.concat([most_fre, other_fre], ignore_index=True)

        labels,counts = x_fre[x],x_fre['fre']
        explode = np.zeros_like(labels)

        if prominent is None: prominent = random.choice(labels)
        prominent_index = labels.index[labels == prominent].tolist()[0]
        explode[prominent_index] = 0.15

        fig, ax = plt.subplots(dpi=300)
        fig.tight_layout(pad=2)

        ax.pie(counts, labels=labels, explode=explode,autopct='%.1f%%',startangle=26)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        file_fig = os.path.join(dir_fig, f"{x}.png")
        plt.savefig(file_fig,bbox_inches='tight')
        plt.close(fig)
        return file_fig

    def get_tle(self,mode='keep',dir_TLE='TLE'):
        """
        Download TLE (Two-Line Element) data from [SPACETRACK](https://www.space-track.org) for all NORAD_IDs in the current catalog.

        Usage:
            >>> tle_file = satcatalog.get_tle()
            >>> print("TLE file saved at:", tle_file)
        Inputs:
            mode -> [str,optional,default='keep'] Action for the TLE directory.
                Use 'keep' to retain existing TLE files, or 'clear' to delete existing files before downloading.
            dir_TLE -> [str,optional,default='TLE'] Directory to save downloaded TLE files.
        Returns:
            tle_file -> [str] Path of the file containing the downloaded TLE data.
        Notes:
            - Requires a valid Space-Track account for downloading TLEs.
        """
        norad_ids = list(self.df['NORAD_ID'])
        file_tle = download_tle(norad_ids,mode=mode,dir_TLE=dir_TLE)
        return file_tle
            