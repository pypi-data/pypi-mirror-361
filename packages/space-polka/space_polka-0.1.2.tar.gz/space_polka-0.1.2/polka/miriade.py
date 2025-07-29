from astropy.time import Time
import pandas as pd
import requests


def query(name, epochs):
    """Gets asteroid ephemerides from LTE Miriade.

    Parameters
    ----------
    name : str
        Name or designation of asteroid.
    epochs : list
        List of observation epochs in JD or ISO formats.

    Returns
    -------
    pd.DataFrame - Ephemerides for the requested epochs
                   False - If query failed somehow
    """

    # Pass sorted list of epochs to speed up query
    # Convert epochs to JD
    epochs = [ e if isinstance(e, float) else float(Time(e).jd) for e in epochs ]
    files = {"epochs": ("epochs", "\n".join(["%.6f" % epoch for epoch in epochs]))}

    # VOSSP/Miriade parameters
    url = "https://ssp.imcce.fr/webservices/miriade/api/ephemcc.php"

    params = {
        "-name": f"a:{name}",
        "-mime": "json",
        "-tcoor": "1",
        "-output": "--jd",
        "-tscale": "UTC",
        "-observer": "500",
    }

    # Execute query
    try:
        r = requests.post(url, params=params, files=files, timeout=50)
    except requests.exceptions.ReadTimeout:
        return False
    j = r.json()

    # Read JSON response
    try:
        ephem = pd.DataFrame.from_dict(j["data"])
    except KeyError:
        return False

    return ephem
