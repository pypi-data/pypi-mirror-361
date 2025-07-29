from alerce.core import Alerce
from astropy import table
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astroquery.ipac.irsa import Irsa
from astroquery.mast import Catalogs
from astroquery.sdss import SDSS
from collections import OrderedDict
from scipy import stats
from scipy.optimize import minimize
from scipy.stats import chi2
import astropy.units as u
import json
import numpy as np
import os
import pathlib
import requests
import warnings

# Suppress insecure request warnings (for development purposes only)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


def get_tns_credentials():
    """
    Retrieve TNS credentials from environment variables if available,
    otherwise fall back to reading the tns_key.txt file.
    """
    api_key = os.environ.get("TNS_API_KEY")
    tns_id = os.environ.get("TNS_ID")
    username = os.environ.get("TNS_USERNAME")

    if api_key and tns_id and username:
        return api_key, tns_id, username

    # Fall back to the key file in the user's home directory.
    key_path = pathlib.Path.home() / 'tns_key.txt'
    try:
        with open(key_path, 'r') as key_file:
            lines = [line.strip() for line in key_file if line.strip()]
        if len(lines) < 3:
            raise ValueError("TNS key file is incomplete. It must contain API key, TNS ID, and username.")
        return lines[0], lines[1], lines[2]
    except Exception as e:
        raise Exception("Error retrieving TNS credentials: " + str(e))


def get_tns_coords(tns_name):
    """
    Retrieve the Right Ascension (RA) and Declination (DEC) in degrees for a transient
    from the Transient Name Server (TNS) based on its IAU name, along with the ZTF name if available.

    This function requires a TNS API key file located in the user's home directory named 'tns_key.txt'.
    The file should contain three lines:
      1. API key
      2. TNS ID
      3. Username

    Parameters
    -----------
    tns_name : str
        The name of the transient (e.g. "2018hyz"). If the name starts with "AT" or "AT_",
        those prefixes will be removed.

    Returns
    --------
    tuple
        A tuple (ra_deg, dec_deg, ztf_name) where ra_deg and dec_deg are floats representing the coordinates,
        and ztf_name is a string starting with "ZTF" if found in the internal_names field, or None if not.
        Returns (None, None, None) if the transient is not found or if an error occurs.
    """
    # Normalize tns_name: remove leading "AT_" or "AT" if present.
    if tns_name.startswith("AT_"):
        tns_name = tns_name[3:]
    elif tns_name.startswith("AT"):
        tns_name = tns_name[2:]

    # Locate and read the TNS key file
    try:
        api_key, tns_id, username = get_tns_credentials()
    except Exception as e:
        print("Error retrieving TNS credentials:", e)
        return None, None, None

    # Build the URL and the query payload
    base_url = "https://www.wis-tns.org/api/get"
    object_endpoint = f"{base_url}/object"
    query_data = OrderedDict([
        ("objname", tns_name),
        ("photometry", "0"),
        ("tns_id", tns_id),
        ("type", "user"),
        ("name", username)
    ])
    payload = {
        'api_key': (None, api_key),
        'data': (None, json.dumps(query_data))
    }
    headers = {
        'User-Agent': f'tns_marker{{"tns_id":{tns_id}, "type":"bot", "name":"{username}"}}'
    }

    try:
        print(f"Querying TNS coordinates for object '{tns_name}'...")
        response = requests.post(object_endpoint, files=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        # Check if the response contains valid data
        if 'data' not in response_json:
            error_message = response_json.get('id_message', 'Unknown error from TNS')
            print("TNS error:", error_message)
            return None, None, None

        data = response_json['data']
        ra = data.get('radeg')
        dec = data.get('decdeg')
        if ra is None or dec is None:
            print(f"Coordinates not found in TNS response for object '{tns_name}'.")
            return None, None, None

        # Extract ztf_name from internal_names field if available.
        internal_names = data.get('internal_names', '')
        ztf_names = [name.strip() for name in internal_names.split(',') if name.strip().startswith("ZTF")]
        ztf_name = None
        if ztf_names:
            if len(ztf_names) > 1:
                print("Warning: Multiple ZTF names found. Using the first one:", ztf_names[0])
            ztf_name = ztf_names[0]

        print(f"Found coordinates for {tns_name} at RA={ra}, DEC={dec} with ZTF name={ztf_name}")
        return ra, dec, ztf_name

    except requests.RequestException as req_err:
        print("HTTP Request error while querying TNS:", req_err)
    except Exception as e:
        print("An unexpected error occurred while querying TNS:", e)

    return None, None, None


def get_ztf_name(ra, dec, acceptance_radius=3):
    """
    Query the Alerce database to find the ZTF name of an object at given coordinates.

    Parameters
    -----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    acceptance_radius : float, optional
        Search radius in arcseconds (default: 3)

    Returns
    --------
    ztf_name : str or None
        The ZTF object name if found, None if no object is found at the given coordinates.
    """
    try:
        # Initialize Alerce client
        client = Alerce()

        # Query for objects at the given coordinates
        objects = client.query_objects(ra=ra, dec=dec, radius=acceptance_radius)

        # Return the ZTF name if an object was found, None otherwise
        if len(objects) > 0:
            ztf_name = objects['oid'][0]
        else:
            ztf_name = None

        return ztf_name

    except Exception as e:
        print(f"Error querying Alerce: {str(e)}")
        return None


def get_ztf_coordinates(ztf_name):
    """
    Get the list of all RAs and DECs of all detections of a ZTF object
    given its name by querying the Alerce database.

    Parameters
    -----------
    ztf_name : str
        The ZTF object name to query

    Returns
    --------
    tuple or (None, None)
        A tuple (ras, decs) where ras and decs are numpy arrays containing the
        RAs and DECs in degrees for all detections of the object. Returns (None, None)
        if no detections are found or if an error occurs.
    """

    try:
        # Initialize Alerce client
        client = Alerce()

        # Query detections for the object
        detections = client.query_detections(ztf_name, format="pandas")

        # If we have detections, convert to astropy table and get coordinates
        if len(detections) > 0:
            det_table = table.Table.from_pandas(detections)['mjd', 'magpsf', 'sigmapsf', 'ra', 'dec', 'fid']

            # Get arrays of all RAs and DECs
            ras = np.array(det_table['ra'])
            decs = np.array(det_table['dec'])

            return ras, decs
        else:
            print(f"No detections found for {ztf_name}")
            return None, None

    except Exception as e:
        print(f"Error querying Alerce: {str(e)}")
        return None, None


def get_coordinates(*args, save_coords=True, coords_dir='coords'):
    """
    Get the coordinates (RA, DEC) for a transient using various identification methods.
    Can accept either an object name (IAU or ZTF) or RA/DEC coordinates.

    Parameters
    -----------
    *args : str or float
        Either:
        - A single string containing an object name from IAU or ZTF (e.g., "2018hyz" or "ZTF18acpdvos")
        - Two floats representing RA and DEC in degrees
    save_coords : bool, optional
        Save the coordinates to disk (default: True)
    coords_dir : str, optional
        Directory to save the coordinates (default: 'coords')

    Returns
    --------
    tuple
        A tuple containing:
        - ras: numpy array of Right Ascension values in degrees
        - decs: numpy array of Declination values in degrees
        - ztf_name: str, the ZTF identifier for the object
        - iau_name: str, the IAU name of the object
        Returns (None, None, None, None) if the object cannot be found or if an error occurs
    """
    ztf_name = None
    iau_name = None
    ras = None
    decs = None

    try:
        # Determine object identifiers first
        if len(args) == 1:
            if args[0].startswith("ZTF"):
                ztf_name = args[0]
            else:
                iau_name = args[0]
        elif len(args) == 2:
            ra_deg, dec_deg = args
        elif len(args) == 3:
            if args[0].startswith("ZTF"):
                ztf_name = args[0]
            else:
                iau_name = args[0]
            ra_deg, dec_deg = args[1:]

        # Check for existing files
        if iau_name:
            local_file = os.path.join(coords_dir, f"{iau_name}_coords.csv")
            alternative_file = os.path.join(coords_dir, f"{iau_name}.txt")
            if os.path.exists(local_file):
                print(f"Loading coordinates from {local_file}")
                coords = table.Table.read(local_file, format='ascii.csv')
                return coords['RA'], coords['DEC'], ztf_name, iau_name
            elif os.path.exists(alternative_file):
                print(f"Loading coordinates from {alternative_file}")
                coords = table.Table.read(alternative_file, format='ascii')
                coords = coords[np.isfinite(coords['RA'])]
                return coords['RA'], coords['DEC'], ztf_name, iau_name

        if ztf_name:
            local_file = os.path.join(coords_dir, f"{ztf_name}_coords.csv")
            if os.path.exists(local_file):
                print(f"Loading coordinates from {local_file}")
                coords = table.Table.read(local_file, format='ascii.csv')
                return coords['RA'], coords['DEC'], ztf_name, iau_name

        if len(args) == 2:
            local_file = os.path.join(coords_dir, f"coords_{ra_deg:.6f}_{dec_deg:.6f}.csv")
            if os.path.exists(local_file):
                print(f"Loading coordinates from {local_file}")
                coords = table.Table.read(local_file, format='ascii.csv')
                return coords['RA'], coords['DEC'], ztf_name, iau_name

        # Check input arguments
        if len(args) == 1:
            # Case 1: Single argument - object name
            object_name = args[0]
            if object_name.startswith("ZTF"):
                ztf_name = object_name
                ras, decs = get_ztf_coordinates(ztf_name)
            else:
                iau_name = object_name
                ra, dec, ztf_name = get_tns_coords(iau_name)
                if ra is not None:
                    # If TNS didn't return a ZTF name, try to find it
                    if ztf_name is None:
                        ztf_name = get_ztf_name(ra, dec)
                    if ztf_name is not None:
                        ras, decs = get_ztf_coordinates(ztf_name)

        # Case 2: Two arguments - RA, DEC coordinates
        elif len(args) == 2:
            ra_deg, dec_deg = args
            ztf_name = get_ztf_name(ra_deg, dec_deg)
            if ztf_name is not None:
                ras, decs = get_ztf_coordinates(ztf_name)
            else:
                iau_name = object_name

        else:
            raise ValueError("Must provide either object name or both RA and DEC in degrees.")

        # Save coordinates to file if we have valid coordinates
        if save_coords and ras is not None and decs is not None:
            # Create directory if it does not exist
            os.makedirs(coords_dir, exist_ok=True)

            # Create filename based on available identifiers
            if iau_name is not None:
                output_filename = os.path.join(coords_dir, f"{iau_name}_coords.csv")
            elif ztf_name is not None:
                output_filename = os.path.join(coords_dir, f"{ztf_name}_coords.csv")
            else:
                output_filename = os.path.join(coords_dir, f"coords_{ra_deg:.6f}_{dec_deg:.6f}.csv")

            # Save coordinates to file
            coords_table = table.Table({'RA': ras, 'DEC': decs})
            coords_table.write(output_filename, format='ascii.csv', overwrite=True)
            print(f"Saved coordinates to {output_filename}")

        return ras, decs, ztf_name, iau_name

    except Exception as e:
        print(f"Error in get_coordinates: {str(e)}")
        return None, None, None, None


def query_sdss(ra_deg, dec_deg, search_radius=3, DR=18):
    """
    Query SDSS for objects within a search radius of given coordinates.

    Parameters
    -----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    search_radius : float
        Search radius in arcseconds
    DR : int, default 18
        SDSS Data Release

    Returns
    --------
    astropy.table.Table or None
        Table containing:
        - ra, dec: coordinates in degrees
        - raErr, decErr: coordinate errors in degrees
        - u,g,r,i,z: PSF magnitudes
        - offsetRa_[u,g,r,i,z], offsetDec_[u,g,r,i,z]: offsets in arcsec
        Returns None if query fails or no objects found
    """

    try:
        # Convert search radius to degrees
        radius = search_radius * u.arcsec

        # Create coordinate object
        coords = SkyCoord(ra=ra_deg*u.degree, dec=dec_deg*u.degree)

        # Define columns to retrieve
        photoobj_fields = [
            # Basics
            'objID', 'ra', 'dec', 'raErr', 'decErr',
            # PSF magnitudes
            'u', 'g', 'r', 'i', 'z',
            'psfMag_u', 'psfMag_g', 'psfMag_r', 'psfMag_i', 'psfMag_z',
            # Model magnitudes
            'modelMag_u', 'modelMag_g', 'modelMag_r', 'modelMag_i', 'modelMag_z',
            'modelMagErr_u', 'modelMagErr_g', 'modelMagErr_r', 'modelMagErr_i', 'modelMagErr_z',
            # Offsets in arcsec
            'offsetRa_u', 'offsetRa_g', 'offsetRa_r', 'offsetRa_i', 'offsetRa_z',
            'offsetDec_u', 'offsetDec_g', 'offsetDec_r', 'offsetDec_i', 'offsetDec_z',
            # Petrosian radius
            'petroR50_u', 'petroR50_g', 'petroR50_r', 'petroR50_i', 'petroR50_z',
        ]

        # Query SDSS
        results = SDSS.query_region(
            coordinates=coords,
            radius=radius,
            photoobj_fields=photoobj_fields,
            data_release=DR
        )

        # Rename objID to objID_SDSS
        results.rename_column('objID', 'objID_SDSS')

        # Only return objects with an r-band offset less than the search_radius
        results = results[np.abs(results['offsetRa_r']) < search_radius]

        return results

    except Exception as e:
        print(f"Error querying SDSS: {str(e)}")
        return None


def query_panstarrs(ra_deg, dec_deg, search_radius=3, DR=2):
    """
    Query PanSTARRS DR2 3π survey for objects within a search radius of given coordinates.

    Parameters
    -----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    search_radius : float
        Search radius in arcseconds
    DR : int, default 2
        PanSTARRS Data Release

    Returns
    --------
    astropy.table.Table or None
        Table containing:
        - Identifiers: objID, distance
        - Stack positions: raStack, decStack, raStackErr, decStackErr
        - Mean positions: raMean, decMean, raMeanErr, decMeanErr
        - Filter-specific positions: [g,r,i,z,y]ra, [g,r,i,z,y]dec and their errors
        - PSF magnitudes: [g,r,i,z,y]PSFMag and their errors
        - Kron magnitudes: [g,r,i,z,y]KronMag and their errors
        - Kron radii: [g,r,i,z,y]KronRad
        Returns None if query fails or no objects found
    """
    try:
        # Create coordinate object
        coords = SkyCoord(ra=ra_deg, dec=dec_deg, unit=(u.deg, u.deg))

        # Define keys by category
        keys = [
            # Identifiers
            'objID', 'distance',
            # Stack positions
            'raStack', 'decStack', 'raStackErr', 'decStackErr',
            # Mean positions
            'raMean', 'decMean', 'raMeanErr', 'decMeanErr',
            # Filter-specific positions
            'gra', 'gdec', 'graErr', 'gdecErr',
            'rra', 'rdec', 'rraErr', 'rdecErr',
            'ira', 'idec', 'iraErr', 'idecErr',
            'zra', 'zdec', 'zraErr', 'zdecErr',
            'yra', 'ydec', 'yraErr', 'ydecErr',
            # PSF magnitudes
            'gPSFMag', 'gPSFMagErr',
            'rPSFMag', 'rPSFMagErr',
            'iPSFMag', 'iPSFMagErr',
            'zPSFMag', 'zPSFMagErr',
            'yPSFMag', 'yPSFMagErr',
            # Kron magnitudes
            'gKronMag', 'gKronMagErr',
            'rKronMag', 'rKronMagErr',
            'iKronMag', 'iKronMagErr',
            'zKronMag', 'zKronMagErr',
            'yKronMag', 'yKronMagErr',
            # Kron radii
            'gKronRad', 'rKronRad', 'iKronRad', 'zKronRad', 'yKronRad'
        ]

        # Query PS1
        print("Querying PanSTARRS...")
        catalog_data = Catalogs.query_region(
            coordinates=coords,
            catalog="PANSTARRS",
            radius=search_radius * u.arcsec,
            data_release=f"dr{DR}",
            table="stack"
        )

        # Rename objID to objID_PS1
        output = catalog_data[keys]
        output.rename_column('objID', 'objID_PS1')

        return output

    except Exception as e:
        print(f"Error querying PanSTARRS: {str(e)}")
        return None


def get_ps1_image(ra_deg, dec_deg, size_arcsec=60, band='r', save_image=True, output_dir='images',
                  object_name=None):
    """
    Download a PanSTARRS FITS cutout in a single band.

    Parameters
    -----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    size_arcsec : int, optional
        Size of cutout in pixels (0.25 arcsec/pixel) (default: 60)
    band : str, optional
        Filter to download ('g','r','i','z', or 'y') (default: 'i')
    save_image : bool, optional
        Save the FITS file to disk (default: True)
    output_dir : str, optional
        Directory to save the FITS file (default: 'images')
    object_name : str, optional
        Object name to use in the filename (default: None)

    Returns
    --------
    image_data : numpy.ndarray or None
        Image data in the FITS file if successful, None if an error occurs
    """

    # Check for existing files
    if object_name:
        local_file = os.path.join(output_dir, f"{object_name}_{band}.fits")
        if os.path.exists(local_file):
            print(f"Loading image from {local_file}")
            with fits.open(local_file) as hdul:
                return hdul[0].data, hdul[0].header

    # Check for coordinate-based file
    local_file = os.path.join(output_dir, f"PS1_{ra_deg:.6f}_{dec_deg:.6f}_{band}.fits")
    if os.path.exists(local_file):
        print(f"Loading image from {local_file}")
        with fits.open(local_file) as hdul:
            return hdul[0].data, hdul[0].header

    # Convert size to pixels in arcsec/pixel
    plate_scale = 0.25
    size_pix = int(size_arcsec / plate_scale)

    try:
        # Get the image filename from PS1
        service = "https://ps1images.stsci.edu/cgi-bin/ps1filenames.py"
        url = f"{service}?ra={ra_deg}&dec={dec_deg}&filters={band}"
        imtable = table.Table.read(url, format='ascii')

        if len(imtable) == 0:
            print("No images found")
            return None, None

        # Construct URL for FITS cutout
        base_url = (f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
                    f"ra={ra_deg}&dec={dec_deg}&size={size_pix}&format=fits")

        filename = imtable[0]['filename']
        fits_url = base_url + "&red=" + filename

        # Get the FITS data directly
        if object_name is not None:
            output_filename = os.path.join(output_dir, f"{object_name}_{band}.fits")
        else:
            output_filename = os.path.join(output_dir, f"PS1_{ra_deg:.6f}_{dec_deg:.6f}_{band}.fits")

        # Download and save the FITS file
        with fits.open(fits_url) as hdul:
            image_data = hdul[0].data
            image_header = hdul[0].header
            if image_data is None:
                print("No data in FITS file")
                return None, None
            if save_image:
                # Create directory if it does not exist
                os.makedirs(output_dir, exist_ok=True)

                # Save the FITS file
                hdul.writeto(output_filename, overwrite=True)

            print(f"Downloaded {output_filename}")
            return image_data, image_header

    except Exception as e:
        print(f"Error: {str(e)}")
        if 'output_filename' in locals() and os.path.exists(output_filename):
            os.remove(output_filename)
        return None, None


def get_sdss_image(ra_deg, dec_deg, size_arcsec=60, save_image=True, output_dir='images',
                   object_name=None, band='r'):
    """
    Download a SDSS FITS cutout centered on given coordinates.

    Parameters
    ----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    size_arcsec : int, optional
        Size of cutout in arcseconds (default: 60)
    save_image : bool, optional
        Save the FITS file to disk (default: True)
    output_dir : str, optional
        Directory to save the FITS file (default: 'images')
    object_name : str, optional
        Object name to use in the filename (default: None)
    band : str, optional
        Filter to download ('g', 'r', 'i', 'z') (default: 'i')

    Returns
    -------
    image_data : numpy.ndarray or None
        Image data in the FITS file if successful, None if an error occurs
    """

    # Check for existing files
    if object_name:
        local_file = os.path.join(output_dir, f"{object_name}_{band}.fits")
        if os.path.exists(local_file):
            print(f"Loading image from {local_file}")
            with fits.open(local_file) as hdul:
                return hdul[0].data, hdul[0].header

    # Check for coordinate-based file
    local_file = os.path.join(output_dir, f"SDSS_{ra_deg:.6f}_{dec_deg:.6f}.fits")
    if os.path.exists(local_file):
        print(f"Loading image from {local_file}")
        with fits.open(local_file) as hdul:
            return hdul[0].data, hdul[0].header

    # Convert size to pixels in arcsec/pixel
    # plate_scale = 0.396  # SDSS plate scale in arcsec/pixel
    # size_pix = int(size_arcsec / plate_scale)

    try:
        # Create coordinate object
        coords = SkyCoord(ra=ra_deg*u.degree, dec=dec_deg*u.degree)

        # Query SDSS for the image cutout
        print("Querying SDSS for image...")
        sdss_image = SDSS.get_images(coordinates=coords, radius=0.02*u.deg,
                                     band=[band], cache=False)

        if sdss_image is None or len(sdss_image) == 0:
            print("No images found in SDSS")
            return None, None

        # Get the first image
        hdul = sdss_image[0][0]

        # Save the FITS file if requested
        if save_image:
            if object_name is not None:
                output_filename = os.path.join(output_dir, f"{object_name}_{band}.fits")
            else:
                output_filename = os.path.join(output_dir, f"SDSS_{ra_deg:.6f}_{dec_deg:.6f}.fits")

            # Create directory if it does not exist
            os.makedirs(output_dir, exist_ok=True)

            # Save the FITS file
            hdul.writeto(output_filename, overwrite=True)
            print(f"Saved SDSS image to {output_filename}")

        return hdul.data, hdul.header

    except Exception as e:
        print(f"Error downloading SDSS image: {str(e)}")
        if 'output_filename' in locals() and os.path.exists(output_filename):
            os.remove(output_filename)
        return None, None


def calc_separations(ra_array, dec_array, ra_center, dec_center,
                     separate=False):
    """
    Calculate the separation in arcseconds between arrays of
    coordinates and a central position using astropy.

    Parameters
    ----------
    ra_array : np.array
        Array of Right Ascension values in degrees
    dec_array : np.array
        Array of Declination values in degrees
    ra_center : float
        Central Right Ascension in degrees
    dec_center : float
        Central Declination in degrees
    separate : bool, optional
        Separate measurements into RA and DEC
        (Only valid for small angles)

    Returns
    -------
    sep_ra : np.array
        Array of separations in RA in arcseconds
    delta_ra, delta_dec : np.array
        Separations in RA and DEC in arcsec
    """

    if separate:
        # Calculate simple differences
        delta_dec = (dec_array - dec_center) * 3600

        # For RA, we need to account for the cos(dec) factor
        # We use the mean declination for the correction as we're assuming small distances
        cos_dec = np.cos(np.radians(dec_center))
        delta_ra = ((ra_array - ra_center) * cos_dec) * 3600

        return delta_ra, delta_dec

    # Create SkyCoord objects for comparison
    c1 = SkyCoord(ra_array*u.deg, dec_array*u.deg)
    c2 = SkyCoord(ra_center*u.deg, dec_center*u.deg)

    # Calculate the separation using astropy
    sep = c1.separation(c2).arcsec

    return sep


def get_closest_match(ra_deg, dec_deg, search_radius=3, save_catalog=True, output_dir='catalogs',
                      object_name=None):
    """
    Query both SDSS and PanSTARRS and return the closest object to the coordinates.

    Parameters
    -----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    search_radius : float, optional
        Search radius in arcseconds (default: 3)
    save_catalog : bool, optional
        Save the catalog data to disk (default: True)
    output_dir : str, optional
        Directory to save the catalog data (default: 'catalogs')
    object_name : str, optional
        Object name to use in the filename (default: None)

    Returns
    --------
    astropy.table.Table
        Single-row table containing:
        - separation: angular separation in arcseconds
        - catalog: which catalog the object is from ('SDSS', 'PS1', or 'Both')
        - All columns from both SDSS and PS1 (with '_SDSS' and '_PS1' suffixes)
        Returns None if no objects found in either catalog
    """

    # Check for existing files
    if object_name:
        local_file = os.path.join(output_dir, f"{object_name}.csv")
        if os.path.exists(local_file):
            print(f"Loading catalog data from {local_file}")
            result = table.Table.read(local_file, format='ascii.csv')
            if 'objID_SDSS' in result.colnames:
                used_catalog = 'SDSS'
            elif 'objID_PS1' in result.colnames:
                used_catalog = 'PS1'
            return result, used_catalog
        local_file = os.path.join(output_dir, f"{object_name}.cat")
        if os.path.exists(local_file):
            print(f"Loading catalog data from {local_file}")
            result = table.Table.read(local_file, format='ascii')
            if 'objID_SDSS' in result.colnames:
                used_catalog = 'SDSS'
            elif 'objID_PS1' in result.colnames:
                used_catalog = 'PS1'
            return result, used_catalog

    # Check for coordinate-based file
    local_file = os.path.join(output_dir, f"catalog_{ra_deg:.6f}_{dec_deg:.6f}.csv")
    if os.path.exists(local_file):
        print(f"Loading catalog data from {local_file}")
        result = table.Table.read(local_file, format='ascii.csv')
        if 'objID_SDSS' in result.colnames:
            used_catalog = 'SDSS'
        elif 'objID_PS1' in result.colnames:
            used_catalog = 'PS1'
        return result, used_catalog

    # Query both catalogs
    used_catalog = None
    sdss_results = query_sdss(ra_deg, dec_deg, search_radius)
    if sdss_results is None:
        ps1_results = query_panstarrs(ra_deg, dec_deg, search_radius)
    else:
        ps1_results = None

    # If no results from either catalog, return None
    if sdss_results is None and ps1_results is None:
        print("No objects found in either catalog")
        return None, None

    # Calculate separations and find closest object from each catalog
    closest_sdss = None
    closest_ps1 = None

    if sdss_results is not None and len(sdss_results) > 0:
        used_catalog = 'SDSS'
        sdss_seps = calc_separations(sdss_results['ra'], sdss_results['dec'],
                                     ra_deg, dec_deg)
        idx_sdss = np.argmin(sdss_seps)
        closest_sdss = sdss_results[idx_sdss]

    elif ps1_results is not None and len(ps1_results) > 0:
        used_catalog = 'PS1'
        idx_ps1 = np.argmin(ps1_results['distance'])
        closest_ps1 = ps1_results[idx_ps1]

    # Create output table based on which catalogs had matches
    if closest_sdss is not None and closest_ps1 is not None:
        # Both catalogs have matches - combine them
        result = table.hstack([closest_sdss, closest_ps1])
    elif closest_sdss is not None:
        result = closest_sdss
    else:
        result = closest_ps1

    # Make sure it's a table
    result = table.Table(result)

    if save_catalog:
        # Create directory if it does not exist
        os.makedirs(output_dir, exist_ok=True)

        # Save the catalog data to disk
        if object_name is not None:
            output_filename = os.path.join(output_dir, f"{object_name}.csv")
        else:
            output_filename = os.path.join(output_dir, f"catalog_{ra_deg:.6f}_{dec_deg:.6f}.csv")
        result.write(output_filename, format='ascii.csv', overwrite=True)
        print(f"Saved catalog data to {output_filename}")

    return result, used_catalog


def get_data(*args, save_all=True, base_dir='.', coords_directory='coords', catalog_directory='catalogs',
             images_directory='images', plot=True):
    """
    Get the coordinates, reference catalog, and images for a given transient.

    Parameters
    -----------
    *args : str or float
        Either:
        - A single string containing an object name from IAU or ZTF
        - Two floats representing RA and DEC in degrees
        - Three arguments: object name, RA, and DEC
    save_all : bool, optional
        Save all data to disk (default: True)
    base_dir : str, optional
        Base directory for saving data (default: current directory)
    coords_directory : str, optional
        Directory to save coordinates (default: 'coords')
    catalog_directory : str, optional
        Directory to save catalog data (default: 'catalogs')
    images_directory : str, optional
        Directory to save images (default: 'images')

    Returns
    --------
    ras : numpy.ndarray
        Array of Right Ascension values in degrees
    decs : numpy.ndarray
        Array of Declination values in degrees
    ztf_name : str
        The ZTF identifier for the object
    iau_name : str
        The IAU name of the object
    catalog_result : astropy.table.Table
        Table containing catalog data
    used_catalog : str
        The catalog used ('SDSS', 'PS1', or None)
    image_data : numpy.ndarray
        Image data in the FITS file
    image_header : astropy.io.fits.Header
        FITS header for the image
    """
    # Set up output directories
    coords_dir = os.path.join(base_dir, coords_directory)
    catalogs_dir = os.path.join(base_dir, catalog_directory)
    images_dir = os.path.join(base_dir, images_directory)

    # Get coordinates of the transient
    ras, decs, ztf_name, iau_name = get_coordinates(*args, save_coords=save_all,
                                                    coords_dir=coords_dir)

    # If we got coordinates, get the reference catalog and image data
    if ras is not None and len(ras) > 0:
        # Use median position for catalog and image queries
        ra_center = np.nanmedian(ras)
        dec_center = np.nanmedian(decs)

        # Get object name for filenames
        object_name = iau_name if iau_name is not None else ztf_name

        # Get catalog data
        catalog_result, used_catalog = get_closest_match(ra_center, dec_center,
                                                         save_catalog=save_all,
                                                         output_dir=catalogs_dir,
                                                         object_name=object_name)

        # Get PS1 image
        if (used_catalog == 'PS1') and plot:
            image_data, image_header = get_ps1_image(ra_center, dec_center,
                                                     save_image=save_all,
                                                     output_dir=images_dir,
                                                     object_name=object_name)
        elif (used_catalog == 'SDSS') and plot:
            image_data, image_header = get_sdss_image(ra_center, dec_center,
                                                      save_image=save_all,
                                                      output_dir=images_dir,
                                                      object_name=object_name)
        else:
            image_data = None
            image_header = None
    else:
        catalog_result = None
        used_catalog = None
        image_data = None
        image_header = None

    return ras, decs, ztf_name, iau_name, catalog_result, used_catalog, image_data, image_header


def query_ztf_sources(ra_deg, dec_deg, search_radius=120, band='r', ZTF_DR=22,
                      ngoodobsrel=5, min_medianmag=20):
    """
    Query ZTF Stacked Source Catalog around given RA and DEC.

    Parameters
    ----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    search_radius : float
        Search radius in arcseconds (default: 60")
    band : str, optional
        Filter to query ('g', 'r', or 'i') (default: 'r')
    ZTF_DR : int, optional
        ZTF Data Release (default: 22)
    ngoodobsrel : int, optional
        Minimum number of good observations
    min_medianmag : float, optional
        Minimum median magnitude for the source

    Returns
    -------
    output_table : astropy.table.Table
        Table of sources around the specified position
    """
    catalog = f'ztf_objects_dr{ZTF_DR}'
    coord = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
    print(f"Querying ZTF sources around RA={ra_deg}, DEC={dec_deg}")
    result_table = Irsa.query_region(coord, catalog=catalog, spatial='Cone', radius=search_radius * u.arcsec)
    print(f"\nFound {len(result_table)} sources in ZTF")

    # Filter by band
    output_table = result_table[result_table['filtercode'] == f'z{band}']
    print(f"Found {len(output_table)} sources in ZTF {band} band")

    # Filter by number of detections
    output_table = output_table[output_table['ngoodobsrel'] >= ngoodobsrel]
    print(f"Found {len(output_table)} sources with at least {ngoodobsrel} good observations")

    # Filter by median magnitude
    output_table = output_table[output_table['medianmag'] <= min_medianmag]
    print(f"Found {len(output_table)} sources with median magnitude <= {min_medianmag}")

    return output_table


def calc_astrometric_error(ra_deg, dec_deg, object_name, search_radius=120, band='r', min_ps1_mag=22, max_diff=0.2,
                           max_separation=0.5, ZTF_DR=22, ngoodobsrel=5, min_medianmag=20, ref_dir='reference',
                           used_catalog=None):
    """
    Function to calculate the astrometric error for a transient based on ZTF and PS1 data.

    Parameters
    ----------
    ra_deg : float
        Right Ascension in degrees
    dec_deg : float
        Declination in degrees
    search_radius : float, optional
        Search radius in arcseconds (default: 60")
    band : str, optional
        Filter to query ('g', 'r', or 'i') (default: 'r')
    min_ps1_mag : float, optional
        Minimum PS1 magnitude to consider (default: 22)
    max_diff : float, optional
        Maximum difference between PSF and Kron magnitudes (default: 0.2)
    max_separation : float, optional
        Maximum separation between PS1 and ZTF sources in arcseconds (default: 1.0)
    ZTF_DR : int, optional
        ZTF Data Release (default: 22)
    ngoodobsrel : int, optional
        Minimum number of good observations for ZTF sources
    min_medianmag : float, optional
        Minimum median magnitude for ZTF sources
    ref_dir : str, optional
        Directory with the reference PS1 and ZTF catalogs
    object_name : str
        Name of the object to use for saving reference files
    used_catalog : str, optional
        Catalog used for the query ('PS1', 'SDSS', or None)

    Returns
    -------
    mean_abs_total : float
        Mean absolute total separation between PS1 and ZTF sources in arcseconds
    mean_ra_offset : float
        Mean RA offset in arcseconds (ZTF - PS1 or SDSS)
    mean_dec_offset : float
        Mean DEC offset in arcseconds (ZTF - PS1 or SDSS)
    """

    # Query ZTF and PS1 catalogs
    ztf_ref_name = os.path.join(ref_dir, f"{object_name}_ztf.txt")
    ps1_ref_name = os.path.join(ref_dir, f"{object_name}_ps1.txt")
    sdss_ref_name = os.path.join(ref_dir, f"{object_name}_sdss.txt")

    # Empty variables for SDSS table
    sdss_table_in = None
    ps1_table_in = None
    ztf_table_in = None

    # Make sure directory exists
    os.makedirs(ref_dir, exist_ok=True)

    if os.path.exists(ztf_ref_name):
        ztf_table_in = table.Table.read(ztf_ref_name, format='ascii')
    else:
        ztf_table_in = query_ztf_sources(ra_deg, dec_deg, search_radius, band, ZTF_DR, ngoodobsrel, min_medianmag)
        if ztf_table_in is not None:
            ztf_table_in.write(ztf_ref_name, format='ascii')

    if ztf_table_in is not None and len(ztf_table_in) > 0:
        # Crop ZTF table based on magnitude
        ztf_table = ztf_table_in[(ztf_table_in['medianmag'] < min_ps1_mag) & (ztf_table_in['medianmag'] > 0)]
        print("Found {} ZTF sources with medianmag < {} mag".format(len(ztf_table), min_ps1_mag))
    else:
        raise RuntimeError(f"No ZTF sources found within {search_radius} arcseconds")

    if used_catalog == 'SDSS':
        if os.path.exists(sdss_ref_name):
            sdss_table_in = table.Table.read(sdss_ref_name, format='ascii')
        else:
            print('Querying SDSS for sources...')
            sdss_table_in = query_sdss(ra_deg, dec_deg, search_radius)
            if sdss_table_in is not None:
                sdss_table_in.write(sdss_ref_name, format='ascii')

        # Crop SDSS table based on magnitude
        sdss_table = sdss_table_in[(sdss_table_in['r'] < min_ps1_mag) & (sdss_table_in['r'] > 0)]
        print("Found {} SDSS sources with r < {} mag".format(len(sdss_table), min_ps1_mag))
        # Rule out galaxies by doing PSF - Model magnitude
        diff = sdss_table[f'psfMag_{band}'] - sdss_table[f'modelMag_{band}']
        sdss_table = sdss_table[(diff < max_diff) & (diff > -0.2)]
        print("Found {} SDSS sources with PSF - Model < {}".format(len(sdss_table), max_diff))

        use_coords = SkyCoord(ra=sdss_table['ra'], dec=sdss_table['dec'], unit=(u.deg, u.deg))

    elif used_catalog == 'PS1':
        if os.path.exists(ps1_ref_name):
            ps1_table_in = table.Table.read(ps1_ref_name, format='ascii')
        else:
            print('Querying PanSTARRS for sources...')
            ps1_table_in = query_panstarrs(ra_deg, dec_deg, search_radius)
            if ps1_table_in is not None:
                ps1_table_in.write(ps1_ref_name, format='ascii')

        # Crop PS1 table based on magnitude
        ps1_table = ps1_table_in[(ps1_table_in[f'{band}KronMag'] < min_ps1_mag) & (ps1_table_in[f'{band}KronMag'] > 0)]
        print("Found {} PS1 sources with {} < {} mag".format(len(ps1_table), band, min_ps1_mag))

        # Rule out galaxies by doing PSF - Kron magnitude
        diff = ps1_table[f'{band}PSFMag'] - ps1_table[f'{band}KronMag']
        ps1_table = ps1_table[(diff < max_diff) & (diff > -0.2)]
        print("Found {} PS1 sources with PSF - Kron < {}".format(len(ps1_table), max_diff))

        use_coords = SkyCoord(ra=ps1_table['raStack'], dec=ps1_table['decStack'], unit=(u.deg, u.deg))

    # Create SkyCoord objects for both catalogs
    ztf_coords = SkyCoord(ra=ztf_table['ra'], dec=ztf_table['dec'], unit=(u.deg, u.deg))

    # Find closest matches within max_separation
    idx_ztf, d2d, _ = use_coords.match_to_catalog_sky(ztf_coords)

    # Keep only matches within the specified separation
    matches = d2d < (max_separation * u.arcsec)

    # Create arrays of valid matches with their separations
    ps1_indices = np.where(matches)[0]
    ztf_indices = idx_ztf[matches]
    separations = d2d[matches]

    # Remove duplicates by keeping only the closest match for each ZTF source
    unique_matches = {}
    for i, (ps1_idx, ztf_idx, sep) in enumerate(zip(ps1_indices, ztf_indices, separations)):
        if ztf_idx not in unique_matches or sep < unique_matches[ztf_idx][1]:
            unique_matches[ztf_idx] = (ps1_idx, sep)

    # Extract the final matches and calculate offsets
    final_separations = []
    ra_offsets = []
    dec_offsets = []

    if len(unique_matches) == 0:
        raise RuntimeError(f"No unique matches found within {search_radius} arcsec")

    for ztf_idx, (ps1_idx, sep) in unique_matches.items():
        final_separations.append(sep)

        # Get coordinates for this match
        if used_catalog == 'SDSS':
            ps1_ra = sdss_table['ra'][ps1_idx]
            ps1_dec = sdss_table['dec'][ps1_idx]
        elif used_catalog == 'PS1':
            ps1_ra = ps1_table['raMean'][ps1_idx]
            ps1_dec = ps1_table['decMean'][ps1_idx]
        ztf_ra = ztf_table['ra'][ztf_idx]
        ztf_dec = ztf_table['dec'][ztf_idx]

        # Calculate offsets in arcseconds (ZTF - PS1)
        ra_offset, dec_offset = calc_separations(ztf_ra, ztf_dec, ps1_ra, ps1_dec, separate=True)

        ra_offsets.append(ra_offset)
        dec_offsets.append(dec_offset)

    print("Found {} unique matches within {} arcsec (removed {} duplicates)".format(
        len(final_separations), max_separation, np.sum(matches) - len(final_separations)))

    # Calculate mean separation
    mean_abs_total = np.nanmedian([sep.to(u.arcsec).value for sep in final_separations])
    mean_ra_offset = np.nanmedian(ra_offsets)
    mean_dec_offset = np.nanmedian(dec_offsets)

    print("\nMean astrometric error: {:.2f} arcsec with RA offset {:.2f} arcsec and DEC offset {:.2f} arcsec".format(
        mean_abs_total, mean_ra_offset, mean_dec_offset))
    return mean_abs_total, mean_ra_offset, mean_dec_offset


def get_galaxy_center(catalog_result, used_catalog=None, object_name=None, error=0.1, add_sdss=True, add_ps1=True,
                      search_radius=120, add_stack=False):
    """
    Calculate the galaxy center and its uncertainty from catalog data.

    Parameters
    ----------
    catalog_result : astropy.table.Table
        Catalog data from either SDSS or PS1
    object_name : str, optional
        Name of the object for astrometric error calculation (default: None)
    used_catalog : str, optional
        Catalog used ('SDSS', 'PS1', or None) (default: None)
    error : float, optional
        Additional systematic error in arcseconds (default: 0.1)
    add_sdss : bool, optional
        Include SDSS data in the calculation (default: True)
    add_ps1 : bool, optional
        Include PS1 data in the calculation (default: True)
    search_radius : float, optional
        Search radius in arcseconds for astrometric error calculation (default: 120)
    add_stack : bool, optional
        Include stack positions from PS1 (default: False)

    Returns
    -------
    ra_galaxy : float
        Mean Right Ascension in degrees
    dec_galaxy : float
        Mean Declination in degrees
    mean_ra_offset : float
        Mean RA offset in arcseconds (ZTF - PS1 or SDSS)
    mean_dec_offset : float
        Mean DEC offset in arcseconds (ZTF - PS1 or SDSS)
    error_arcsec : float
        1-sigma radial error in arcseconds
    """

    # Initialize lists to store positions and errors
    ra_measurements = []
    dec_measurements = []
    ra_errors = []
    dec_errors = []

    # Check if we have SDSS data
    if ('objID_SDSS' in catalog_result.colnames) and add_sdss:
        # Add main position
        ra_measurements.append(catalog_result['ra'][0])
        dec_measurements.append(catalog_result['dec'][0])
        ra_errors.append(catalog_result['raErr'][0])
        dec_errors.append(catalog_result['decErr'][0])

        # Add filter-specific offsets (converting from arcsec to degrees)
        for band in 'ugriz':
            if f'offsetRa_{band}' in catalog_result.colnames:
                offset_ra = catalog_result[f'offsetRa_{band}'][0] / 3600.  # arcsec to deg
                offset_dec = catalog_result[f'offsetDec_{band}'][0] / 3600.
                if isinstance(offset_ra, (int, float)) and isinstance(offset_dec, (int, float)):
                    ra_measurements.append(catalog_result['ra'][0] + offset_ra)
                    dec_measurements.append(catalog_result['dec'][0] + offset_dec)
                    # Use the same errors for all bands in SDSS
                    ra_errors.append(catalog_result['raErr'][0])
                    dec_errors.append(catalog_result['decErr'][0])

    # Check if we have PS1 data
    if ('objID_PS1' in catalog_result.colnames) and add_ps1:
        # Add stack position
        if add_stack:
            ra_measurements.append(catalog_result['raStack'][0])
            dec_measurements.append(catalog_result['decStack'][0])
            ra_errors.append(catalog_result['raStackErr'][0])
            dec_errors.append(catalog_result['decStackErr'][0])

        # Add mean position
        ra_measurements.append(catalog_result['raMean'][0])
        dec_measurements.append(catalog_result['decMean'][0])
        ra_errors.append(catalog_result['raMeanErr'][0])
        dec_errors.append(catalog_result['decMeanErr'][0])

        # Add filter-specific positions
        for band in 'grizy':
            if f'{band}ra' in catalog_result.colnames:
                ra_measurements.append(catalog_result[f'{band}ra'][0])
                dec_measurements.append(catalog_result[f'{band}dec'][0])
                ra_errors.append(catalog_result[f'{band}raErr'][0])
                dec_errors.append(catalog_result[f'{band}decErr'][0])

    # Convert to arrays
    ra_measurements = np.array(ra_measurements)
    dec_measurements = np.array(dec_measurements)
    ra_errors = np.array(ra_errors)
    dec_errors = np.array(dec_errors)

    # Calculate weighted mean positions
    ra_weights = 1.0 / (ra_errors**2) if len(ra_errors) > 0 else None
    dec_weights = 1.0 / (dec_errors**2) if len(dec_errors) > 0 else None

    use = np.isfinite(ra_measurements) & np.isfinite(dec_measurements) & np.isfinite(ra_weights) & np.isfinite(dec_weights)
    ra_galaxy = np.average(ra_measurements[use], weights=ra_weights[use])
    dec_galaxy = np.average(dec_measurements[use], weights=dec_weights[use])

    # Calculate total error combining:
    # 1. Standard deviation of measurements
    ra_std = np.nanstd(ra_measurements) * 3600
    dec_std = np.nanstd(dec_measurements) * 3600

    # 2. Mean of formal errors
    ra_formal = np.nanmean(ra_errors) if len(ra_errors) > 0 else 0
    dec_formal = np.nanmean(dec_errors) if len(dec_errors) > 0 else 0

    # 3. Additional systematic error
    if error is None:
        error, mean_ra_offset, mean_dec_offset = calc_astrometric_error(ra_galaxy, dec_galaxy, object_name, search_radius=search_radius,
                                                                        used_catalog=used_catalog)
    else:
        mean_ra_offset = 0
        mean_dec_offset = 0

    # Combine errors in quadrature and convert to arcseconds
    error_arcsec = np.sqrt(np.sqrt((ra_std**2 + ra_formal**2 +
                           dec_std**2 + dec_formal**2)) ** 2 + error ** 2)

    return ra_galaxy, dec_galaxy, mean_ra_offset, mean_dec_offset, error_arcsec


def rice_separation(separations, error_arcsec, confidence_level=0.95,
                    separation_threshold=3.0):
    """
    Calculate the most likely separation between a transient and a galaxy and the
    uncertainty in this measurement using a Rice distribution. Assuming the
    uncertainty in the position of the galaxy is Gaussian and symmetric along
    RA and DEC.

    Parameters:
    -----------
    separations : np.array
        Array of measured separations between transient and galaxy (in arcsec)
    error_arcsec : float
        Total measurement error in the position of the galaxy center (in arcsec)
    confidence_level : float, optional
        Confidence level for reporting the upper limit
        (default: 0.95 for 95% confidence)
    separation_threshold : float, optional
        SNR threshold for considering a detection significant (default: 3.0)

    Returns:
    --------
    nu : float
        Most likely separation between transient and galaxy.
    lower_error : float
        Lower bound of the 68% confidence interval.
    upper_error : float
        Upper bound of the 68% confidence interval.
    snr : float
        Signal-to-noise ratio of the measurement.
    upper_limit : float
        Upper limit on the separation at the specified confidence level.
    sigma : float
        Measurement noise in the galaxy center position (in arcsec).
    """

    # Define negative log likelihood for Rice distribution
    def neg_log_likelihood(params, data):
        # True underlying separation (nu) and measurement noise (sigma)
        nu, sigma = params

        # Make sure nu and sigma are not negative
        if nu < 0 or sigma <= 0:
            return np.inf

        # Return the log likelihood
        return -np.sum(stats.rice.logpdf(data, nu / sigma, scale=sigma))

    # Initial guess for the fit
    initial_guess = [np.median(separations), np.std(separations)]

    # Find maximum likelihood estimates
    bounds = [(0, None), (1e-6, None)]
    result = minimize(neg_log_likelihood, initial_guess,
                      args=(separations,), method='L-BFGS-B',
                      bounds=bounds)

    # Extract parameters
    nu, sigma = result.x

    # Add galaxy centering error
    total_sigma = np.sqrt(sigma ** 2 + error_arcsec ** 2)
    b_total = nu / total_sigma

    # Calculate the median separation +/- 1-sigma errors
    median_separation = stats.rice.ppf(0.50, b_total, scale=total_sigma)
    r_low = stats.rice.ppf(0.16, b_total, scale=total_sigma)
    r_high = stats.rice.ppf(0.84, b_total, scale=total_sigma)

    # Convert these to an error measurement
    lower_err = nu - r_low
    upper_err = r_high - nu

    # Make sure this does not go below 0
    if lower_err <= 0:
        lower_err = nu

    # Calculate signal-to-noise ratio (>> 1 means its Gaussian)
    snr = median_separation / total_sigma

    # Report upper limit
    upper_limit = stats.rice.ppf(confidence_level, 0, scale=total_sigma)

    # If separation is large, report simple stats
    if snr > separation_threshold:
        print(f"Reporting symmetric normal error for SNR={snr:.2f}... ")
        nu = np.median(separations)
        stat_error = np.std(separations) / np.sqrt(len(separations))
        total_error = np.sqrt(stat_error**2 + error_arcsec**2)
        lower_err = upper_err = total_error
    else:
        print(f"Reporting asymmetric Rice error for SNR={snr:.2f}...")

    return nu, lower_err, upper_err, snr, upper_limit, sigma


def check_nuclear(ras, decs, ra_galaxy, dec_galaxy, error_arcsec,
                  p_threshold=0.05):
    """
    Check whether ZTF detections are statistically coincident with the galaxy center,
    accounting for covariance in the ZTF positions but assuming an
    uncorrelated galaxy center uncertainty.

    Parameters
    ----------
    ras : numpy.ndarray
        Array of Right Ascension values in degrees
    decs : numpy.ndarray
        Array of Declination values in degrees
    ra_galaxy : float
        Galaxy center RA in degrees
    dec_galaxy : float
        Galaxy center Dec in degrees
    error_arcsec : float
        1-sigma uncertainty in the galaxy center position in arcseconds
    p_threshold : float, optional
        P-value threshold for significance (default: 0.05)

    Returns
    -------
    sigma : float
        Significance of separation
    chi2_val : float
        Chi-square statistic
    p_value : float
        P-value for the hypothesis test (null hypothesis: ZTF positions are consistent with galaxy center)
    is_nuclear : bool
        True if the ZTF positions are consistent with the galaxy center, False otherwise
    """

    # Convert positions to numpy array
    Y = np.column_stack([ras, decs])
    N = len(ras)

    # Calculate mean ZTF position
    mean_position = np.mean(Y, axis=0)

    # Calculate covariance matrix of ZTF positions
    cov_ztf = np.cov(Y, rowvar=False, ddof=1)

    # Covariance of the mean is reduced by sqrt(N)
    cov_mean = cov_ztf / N

    # Convert galaxy center error from arcsec to degrees
    error_deg = error_arcsec / 3600.0

    # Galaxy center covariance matrix (uncorrelated)
    cov_galaxy = np.array([[error_deg**2, 0],
                          [0, error_deg**2]])

    # Total covariance is sum of both covariances
    cov_total = cov_galaxy + cov_mean

    # Calculate difference vector between mean ZTF position and galaxy center
    d = mean_position - np.array([ra_galaxy, dec_galaxy])

    # Calculate chi-square statistic
    try:
        # Calculate inverse of total covariance matrix
        inv_cov_total = np.linalg.inv(cov_total)
        # Calculate chi-square using matrix multiplication
        # d is the difference vector [delta-ra, delta-dec] between the mean ZTF and galaxy positions
        # d.T is its transpose
        # This gives a scalar value that accounts for both the distance and uncertainties
        chi2_val = d.T @ inv_cov_total @ d

        # Calculate p-value (2 degrees of freedom)
        p_value = 1 - chi2.cdf(chi2_val, df=2)
    except np.linalg.LinAlgError:
        # Handle singular matrix case
        chi2_val = np.nan
        p_value = np.nan

    # Compile results
    is_nuclear = p_value > p_threshold if not np.isnan(p_value) else None

    # Calculate sigma significance
    sigma = np.sqrt(chi2_val)

    return sigma, chi2_val, p_value, is_nuclear
