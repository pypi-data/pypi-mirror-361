import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import sys
import requests
from pyproj import Transformer
import json  # For PDAL pipeline construction
import subprocess  # For executing PDAL command
from urllib.parse import urlparse  # For parsing URLs
from pathlib import Path
from qgis.core import QgsGeometry, QgsSpatialIndex
import laspy
from pyproj import CRS, exceptions  # Import CRS from pyproj for checking object type
import argparse

from sklearn.cluster import DBSCAN
from sklearn.metrics import pairwise_distances_argmin_min
from scipy.spatial import ConvexHull
import numpy as np
from PIL import Image
from io import BytesIO
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# print("laspy version:", laspy.__version__)
# --- Step 0: Set up the PyQGIS Environment (Crucial for Standalone Scripts) ---
# Check if running in conda environment
if "CONDA_PREFIX" in os.environ:
    QGIS_PATH = os.environ["CONDA_PREFIX"]
    # For conda environments, we need to set these additional paths
    os.environ["GDAL_DATA"] = os.path.join(QGIS_PATH, "share", "gdal")
    os.environ["PROJ_LIB"] = os.path.join(QGIS_PATH, "share", "proj")
else:
    # Fallback to system QGIS path
    QGIS_PATH = "/usr"

# Add QGIS Python paths to system path
os.environ["QGIS_PREFIX_PATH"] = QGIS_PATH
QT_PLUGIN_PATH = os.path.join(QGIS_PATH, "lib", "qt", "plugins")
QGIS_PLUGIN_PATH = os.path.join(QGIS_PATH, "share", "qgis", "python", "plugins")

# Set environment variables
os.environ["QT_PLUGIN_PATH"] = QT_PLUGIN_PATH
os.environ["PYTHONPATH"] = os.pathsep.join(
    [
        os.path.join(QGIS_PATH, "share", "qgis", "python"),
        QGIS_PLUGIN_PATH,
        os.environ.get("PYTHONPATH", ""),
    ]
).strip(os.pathsep)

# Add paths to sys.path if they're not already there
qgis_python_path = os.path.join(QGIS_PATH, "share", "qgis", "python")
if qgis_python_path not in sys.path:
    sys.path.append(qgis_python_path)
if QGIS_PLUGIN_PATH not in sys.path:
    sys.path.append(QGIS_PLUGIN_PATH)

# Print debug information
print("\nQGIS Environment Setup:")
print(f"QGIS_PREFIX_PATH: {os.environ['QGIS_PREFIX_PATH']}")
print(f"QT_PLUGIN_PATH: {os.environ['QT_PLUGIN_PATH']}")
print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
if "CONDA_PREFIX" in os.environ:
    print(f"GDAL_DATA: {os.environ['GDAL_DATA']}")
    print(f"PROJ_LIB: {os.environ['PROJ_LIB']}")
print(f"sys.path: {sys.path}\n")

try:
    from qgis.core import (
        QgsApplication,
        QgsVectorLayer,
        QgsProject,
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsPointXY,
        QgsFeatureRequest,
        QgsPoint,
        QgsProviderRegistry,
        QgsDataSourceUri,
    )
except ImportError as e:
    print(f"Error importing PyQGIS modules: {e}")
    print("Please ensure QGIS is installed in your conda environment.")
    print("You can install it using:")
    print("conda install -c conda-forge qgis")
    sys.exit(1)

# Initialize QGIS Application (headless mode - no GUI)
qgs = QgsApplication([], False)
qgs.initQgis()
print("PyQGIS environment initialized for headless operation.")

# --- Define Paths and Constants ---
LIDAR_INDEX_GPKG_PATH = (
    "/home/amadgakkhar/code/qgis-ns-pe/index/Index_LiDARtiles_tuileslidar.gpkg"
)
LIDAR_DIR = Path("lidar_tiles")
OUTPUT_DIR = Path("output")

# Define standard output filenames
SATELLITE_IMAGE = "satellite_image.png"
LIDAR_SUBSET = "lidar_cropped.laz"
BUILDINGS_OUTPUT = "buildings.laz"
CONTOUR = "contour_points.npy"

# Create directories if they don't exist
os.makedirs(LIDAR_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Step 1: Geocode the Address to Lat/Lon ---


def geocode_address(address, user_agent="MyGeocoderApp/1.0 (contact@example.com)"):
    """
    Geocodes a given address using the OpenStreetMap Nominatim API.

    Args:
        address (str): The address to geocode.
        user_agent (str): The User-Agent string including contact info.

    Returns:
        dict: A dictionary with latitude and longitude, or None if not found.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1, "addressdetails": 0}
    headers = {"User-Agent": user_agent}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        if results:
            return results[0]["lat"], results[0]["lon"]

        else:
            print("No results found for the address.")
            return None, None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Error during request: {err}")
    return None, None


# --- Step 2: Convert Lat/Lon to UTM (NAD83(CSRS) / Canada UTM, EPSG:3978) ---
def transform_coords(lat, lon, target_epsg=3978):
    """Transforms WGS84 (Lat/Lon) to a target CRS (e.g., UTM 3978)."""
    transformer = Transformer.from_crs(
        "epsg:4326", f"epsg:{target_epsg}", always_xy=True
    )
    utm_x, utm_y = transformer.transform(
        lon, lat
    )  # pyproj expects (lon, lat) order for transform
    print(f"Transformed to EPSG:{target_epsg}: X={utm_x}, Y={utm_y}")
    return utm_x, utm_y


# --- Step 3: Get Satellite Image (PNG) for the Bounding Box ---


def get_mapbox_static_image(
    lat,
    lon,
    output_path,
    zoom=20,
    width=400,
    height=400,
    access_token="pk.eyJ1Ijoid3VzZWxtYXBzIiwiYSI6ImNqdTVpc2VibDA4c3E0NXFyMmEycHE3dXUifQ.Wy3_Ou1KrVRkIH1UGb_R3Q",
):
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
        f"{lon},{lat},{zoom}/{width}x{height}?access_token={access_token}"
    )

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"Satellite map image saved to {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return False


def get_static_map(lat, lon, output_path, zoom=16, width=400, height=400):
    """
    Downloads a static map image from OpenStreetMap's tile-based static map service.

    Args:
        lat (float): Latitude of the center point.
        lon (float): Longitude of the center point.
        output_path (str): File path to save the image.
        zoom (int): Zoom level (default 16).
        width (int): Image width in pixels (max 1280).
        height (int): Image height in pixels (max 1280).

    Returns:
        bool: True if the image was saved successfully, False otherwise.
    """
    base_url = "https://staticmap.openstreetmap.de/staticmap.php"
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": f"{width}x{height}",
        "maptype": "mapnik",  # or "cycle"
        "markers": f"{lat},{lon},red",
    }

    try:
        response = requests.get(base_url, params=params, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            print(f"Invalid content type: {content_type}")
            return False

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"Map image saved to: {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error fetching map: {e}")
        return False


def get_satellite_image(lat, lng, API_KEY=GOOGLE_API_KEY):
    """Helper function to get satellite image for given coordinates
    Args:
        lat: Latitude
        lng: Longitude
        API_KEY: Google Maps API key
    Returns:
        PIL Image object
    """
    # Google Static Maps parameters
    size = "640x640"  # Base size
    scale = 2  # Double the resolution
    zoom = 20  # Maximum zoom for highest detail

    map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lng}&"
        f"zoom={zoom}&"
        f"size={size}&"
        f"scale={scale}&"
        f"maptype=satellite&"
        f"key={API_KEY}"
    )

    print(f"\nFetching satellite image for coordinates: ({lat}, {lng})")
    response = requests.get(map_url)
    return Image.open(BytesIO(response.content))


def pixel_to_latlng(x, y, center_lat, center_lng, zoom=20, image_size=(1280, 1280)):
    """Convert pixel coordinates to lat/lng for Google Static Maps
    Args:
        x, y: Pixel coordinates (from click)
        center_lat, center_lng: Center coordinates of the image
        zoom: Google Maps zoom level (default 20)
        image_size: Size of the image in pixels (default 1280x1280 for 640x640 with scale=2)
    Returns:
        (lat, lng): New coordinates after pixel conversion
    """
    # Constants for Google Static Maps
    EARTH_CIRCUMFERENCE = 40075016.686  # Earth's circumference in meters

    # Calculate ground resolution at the center latitude
    # At zoom level 0, one pixel = circumference/256
    # At zoom level z, one pixel = circumference/(256 * 2^z)
    ground_resolution = (EARTH_CIRCUMFERENCE * math.cos(math.radians(center_lat))) / (
        math.pow(2, zoom + 8)
    )  # 256 = 2^8

    # Calculate offset from center in pixels
    dx = x - (image_size[0] / 2)
    dy = y - (image_size[1] / 2)

    # Convert pixel offsets to meters
    meters_x = dx * ground_resolution
    meters_y = -dy * ground_resolution  # Negative because y increases downward in image

    # Convert meters to degrees
    # At the equator, 1 degree = 111,319.9 meters
    meters_per_degree_lat = 111319.9
    meters_per_degree_lng = meters_per_degree_lat * math.cos(math.radians(center_lat))

    # Calculate new coordinates
    new_lat = center_lat + (meters_y / meters_per_degree_lat)
    new_lng = center_lng + (meters_x / meters_per_degree_lng)

    print("\nDebug - Coordinate Conversion:")
    print(f"Click position (x,y): ({x}, {y})")
    print(f"Image center: ({center_lat}, {center_lng})")
    print(f"Pixel offset from center: ({dx}, {dy})")
    print(f"Ground resolution: {ground_resolution:.2f} meters/pixel")
    print(f"Distance in meters: ({meters_x:.2f}m, {meters_y:.2f}m)")
    print(f"New coordinates: ({new_lat}, {new_lng})")

    return new_lat, new_lng


def geocode_satellite_image(address, API_KEY=GOOGLE_API_KEY, point_correction=False):
    """
    Geocode a satellite image for a given address with optional point correction.
    """
    if not API_KEY:
        print(
            "No API key provided. Please set the GOOGLE_API_KEY environment variable."
        )
        sys.exit(1)

    # Print debug info (will be masked in output)
    print("\nDebug Info:")
    print(f"API Key length: {len(API_KEY)} characters")
    print(f"API Key starts with: {API_KEY[:4]}...")
    print(f"Address to geocode: {address}")

    # URL encode the address
    encoded_address = requests.utils.quote(address)
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}"

    try:
        print("\nMaking request to Google Maps API...")
        response = requests.get(geocode_url)
        print(f"Response status code: {response.status_code}")

        # Try to get JSON response
        try:
            geocode_response = response.json()
            print(f"Response status: {geocode_response.get('status')}")
            if "error_message" in geocode_response:
                print(f"Error message: {geocode_response['error_message']}")
        except ValueError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text[:200]}...")  # Print first 200 chars
            return None, None, None

        if geocode_response["status"] != "OK":
            if geocode_response["status"] == "REQUEST_DENIED":
                print("\nPossible issues:")
                print("1. API key might not be activated for Geocoding API")
                print("2. Billing might not be enabled for the project")
                print("3. API key might have restrictions (IP, referrer, etc.)")
                print("\nTo fix:")
                print("1. Go to Google Cloud Console")
                print("2. Make sure Geocoding API is enabled")
                print("3. Check API key restrictions")
                print("4. Enable billing if not already enabled")
            return None, None, None

        # Get initial coordinates
        location = geocode_response["results"][0]["geometry"]["location"]
        initial_lat, initial_lng = location["lat"], location["lng"]
        print(
            f"Initial geocoding:\nAddress: {address}\nLatitude: {initial_lat}, Longitude: {initial_lng}"
        )

        # Get initial satellite image
        image = get_satellite_image(initial_lat, initial_lng, API_KEY)

        if not point_correction:
            return image, initial_lat, initial_lng

        # Convert PIL Image to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Create a figure with fixed size for point selection
        fig = plt.figure(figsize=(12, 12))
        ax = plt.gca()
        ax.imshow(image)
        ax.set_title("Click to select the building location\nClose window when done")
        ax.axis("off")

        # Variable to store the selected point
        selected_point = [None]

        def onclick(event):
            if event.xdata is not None and event.ydata is not None:
                x, y = int(event.xdata), int(event.ydata)
                selected_point[0] = (x, y)

                # Highlight the selected point
                if hasattr(ax, "point_marker"):
                    ax.point_marker.remove()
                ax.point_marker = ax.plot(x, y, "ro", markersize=10)[0]
                fig.canvas.draw()

                # Close the figure after a short delay
                plt.close(fig)

        # Connect the click event
        fig.canvas.mpl_connect("button_press_event", onclick)

        # Show the plot and wait for user interaction
        plt.show(block=True)

        # If a point was selected, calculate new coordinates
        if selected_point[0] is not None:
            clicked_x, clicked_y = selected_point[0]
            final_lat, final_lng = pixel_to_latlng(
                clicked_x, clicked_y, initial_lat, initial_lng
            )
            print(
                f"\nCorrected coordinates:\nLatitude: {final_lat}, Longitude: {final_lng}"
            )

            # Get new image centered on corrected point
            final_image = get_satellite_image(final_lat, final_lng, API_KEY)
            return final_image, final_lat, final_lng

        # If no point was selected, return original results
        return image, initial_lat, initial_lng

    except requests.exceptions.RequestException as e:
        print(f"\nNetwork error when contacting Google Maps API: {e}")
        return None, None, None


# --- Step 4: Find Corresponding LiDAR Tile ---
def find_lidar_tile(utm_x, utm_y, gpkg_path):
    """
    Finds the URL of the LiDAR tile containing the given UTM coordinates.
    """
    if not os.path.exists(gpkg_path):
        print(f"Error: GeoPackage file not found at {gpkg_path}")
        return None

    # Try to open the GeoPackage
    gpkg_layer = QgsVectorLayer(gpkg_path, "GPKG", "ogr")
    if not gpkg_layer.isValid():
        print(f"Error: Unable to open GeoPackage file: {gpkg_path}")
        return None

    # Get the layer name from sublayers
    sublayers = gpkg_layer.dataProvider().subLayers()
    if not sublayers:
        print("No layers found in GeoPackage.")
        return None

    # Get the layer name from the first sublayer
    layer_parts = sublayers[0].split("!!::!!")
    if len(layer_parts) < 2:
        print("Invalid layer format in GeoPackage.")
        return None

    layer_name = layer_parts[1].strip()
    if not layer_name:
        print("Empty layer name found in GeoPackage.")
        return None

    # Load the actual layer
    uri = f"{gpkg_path}|layername={layer_name}"
    lidar_index_layer = QgsVectorLayer(uri, "LiDAR Tiles Index", "ogr")
    if not lidar_index_layer.isValid():
        print("Failed to load LiDAR index layer.")
        return None

    # Create point for spatial query
    query_point = QgsPointXY(utm_x, utm_y)

    # Transform point if needed
    layer_crs = lidar_index_layer.crs()
    if layer_crs.authid() != "EPSG:3978":
        transform = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:3978"), layer_crs, QgsProject.instance()
        )
        query_point = transform.transform(query_point)

    # Create point geometry for containment check
    point_geom = QgsGeometry.fromPointXY(query_point)

    # Find intersecting feature
    for feature in lidar_index_layer.getFeatures():
        if feature.geometry().contains(point_geom):
            url = feature["url"]
            if url:
                print(f"Found LiDAR tile URL: {url}")
                return url
            else:
                print("Found matching tile but no URL field.")
                return None

    print("No LiDAR tile found containing the coordinates.")
    return None


# --- New Function: Process LiDAR Subset with laspy ---
def process_lidar_subset_with_laspy(
    input_laz_path, output_laz_path, utm_x, utm_y, buffer_m=30
):
    """
    Subsets a local LAZ point cloud to a 50x50m area around utm_x, utm_y using laspy.
    """
    try:
        print(f"\nReading LAZ file: {input_laz_path}")
        from laspy.compression import LazrsBackend

        with laspy.open(input_laz_path, laz_backend=LazrsBackend()) as fh:
            print("Reading points...")
            las = fh.read()
            print(f"Total points: {len(las.points)}")

            # Get a sample of points to determine coordinate range
            points = np.stack([las.x, las.y, las.z], axis=0).transpose()
            print(f"\nPoint cloud bounds:")
            print(f"X range: [{points[:, 0].min():.2f}, {points[:, 0].max():.2f}]")
            print(f"Y range: [{points[:, 1].min():.2f}, {points[:, 1].max():.2f}]")
            print(f"Target point: X={utm_x:.2f}, Y={utm_y:.2f}")

            # Check if coordinates might be in different CRS
            x_in_range = points[:, 0].min() <= utm_x <= points[:, 0].max()
            y_in_range = points[:, 1].min() <= utm_y <= points[:, 1].max()

            if not (x_in_range and y_in_range):
                print(
                    "\nWarning: Target coordinates appear to be outside point cloud bounds."
                )
                print(
                    "Attempting to transform coordinates from EPSG:3978 to EPSG:2961..."
                )

                # Transform from EPSG:3978 (NAD83 CSRS) to EPSG:2961 (NAD83(CSRS) / MTM zone 5 Nova Scotia)
                transformer = Transformer.from_crs(
                    "EPSG:3978", "EPSG:2961", always_xy=True
                )
                utm_x, utm_y = transformer.transform(utm_x, utm_y)
                print(f"Transformed coordinates: X={utm_x:.2f}, Y={utm_y:.2f}")

            # Define bounds for clipping
            x_min = utm_x - buffer_m
            x_max = utm_x + buffer_m
            y_min = utm_y - buffer_m
            y_max = utm_y + buffer_m

            print(
                f"\nClipping bounds: X[{x_min:.2f}, {x_max:.2f}], Y[{y_min:.2f}, {y_max:.2f}]"
            )

            # Find points within bounds
            mask = (
                (points[:, 0] >= x_min)
                & (points[:, 0] <= x_max)
                & (points[:, 1] >= y_min)
                & (points[:, 1] <= y_max)
            )

            points_in_bounds = mask.sum()
            print(f"Found {points_in_bounds} points within bounds")

            if points_in_bounds == 0:
                # Try with a larger buffer
                print("\nNo points found. Trying with a larger buffer...")
                buffer_m *= 5  # Try 5x larger buffer
                x_min = utm_x - buffer_m
                x_max = utm_x + buffer_m
                y_min = utm_y - buffer_m
                y_max = utm_y + buffer_m

                print(
                    f"New bounds: X[{x_min:.2f}, {x_max:.2f}], Y[{y_min:.2f}, {y_max:.2f}]"
                )

                mask = (
                    (points[:, 0] >= x_min)
                    & (points[:, 0] <= x_max)
                    & (points[:, 1] >= y_min)
                    & (points[:, 1] <= y_max)
                )

                points_in_bounds = mask.sum()
                print(f"Found {points_in_bounds} points with larger buffer")

                if points_in_bounds == 0:
                    print("Still no points found within the specified bounds!")
                    return False

            # Rest of the function remains the same...
            new_header = laspy.LasHeader(
                version=las.header.version, point_format=las.header.point_format
            )
            new_header.offsets = las.header.offsets
            new_header.scales = las.header.scales
            new_header.point_count = points_in_bounds

            print(f"Writing {points_in_bounds} points to output file...")
            with laspy.open(
                output_laz_path, mode="w", header=new_header, laz_backend=LazrsBackend()
            ) as writer:
                new_points = laspy.ScaleAwarePointRecord.zeros(
                    points_in_bounds, header=new_header
                )
                for name in las.point_format.dimension_names:
                    setattr(new_points, name, las[name][mask])
                writer.write_points(new_points)

            print(
                f"Successfully saved subset with {points_in_bounds} points to: {output_laz_path}"
            )
            return True

    except Exception as e:
        print(f"Error processing LAZ file: {str(e)}")
        print("Stack trace:")
        import traceback

        traceback.print_exc()
        return False


def visualize_point_cloud(laz_path, title=None, point_size=0.5, color_by="elevation"):
    """
    Visualizes a LAZ/LAS point cloud in 3D using matplotlib.
    """
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        print(f"Reading point cloud from: {laz_path}")
        with laspy.open(laz_path) as fh:
            las = fh.read()

        # Get points
        points = np.vstack((las.x, las.y, las.z)).transpose()

        # Create figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Determine coloring
        if color_by == "elevation":
            colors = points[:, 2]  # Z coordinates
            cmap = plt.cm.viridis
            color_label = "Elevation"
        elif color_by == "intensity" and hasattr(las, "intensity"):
            colors = las.intensity
            cmap = plt.cm.plasma
            color_label = "Intensity"
        elif color_by == "classification" and hasattr(las, "classification"):
            colors = las.classification
            cmap = plt.cm.tab20
            color_label = "Classification"
        else:
            colors = points[:, 2]  # Default to elevation
            cmap = plt.cm.viridis
            color_label = "Elevation"

        # Plot points
        scatter = ax.scatter(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            c=colors,
            cmap=cmap,
            s=point_size,
            alpha=0.6,
        )

        # Add colorbar
        plt.colorbar(scatter, label=color_label)

        # Set labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        if title:
            plt.title(title)

        # Make the plot more visually appealing
        ax.grid(True)

        # Set equal aspect ratio
        max_range = (
            np.array(
                [
                    points[:, 0].max() - points[:, 0].min(),
                    points[:, 1].max() - points[:, 1].min(),
                    points[:, 2].max() - points[:, 2].min(),
                ]
            ).max()
            / 2.0
        )

        mean_x = points[:, 0].mean()
        mean_y = points[:, 1].mean()
        mean_z = points[:, 2].mean()

        ax.set_xlim(mean_x - max_range, mean_x + max_range)
        ax.set_ylim(mean_y - max_range, mean_y + max_range)
        ax.set_zlim(mean_z - max_range, mean_z + max_range)

        # Add point count and bounds info
        info_text = f"Total points: {len(points):,}\n"
        info_text += f"X range: [{points[:, 0].min():.2f}, {points[:, 0].max():.2f}]\n"
        info_text += f"Y range: [{points[:, 1].min():.2f}, {points[:, 1].max():.2f}]\n"
        info_text += f"Z range: [{points[:, 2].min():.2f}, {points[:, 2].max():.2f}]"

        plt.figtext(0.02, 0.02, info_text, fontsize=8, family="monospace")

        # Show the plot (but don't save it)
        plt.show()

    except Exception as e:
        print(f"Error visualizing point cloud: {str(e)}")
        import traceback

        traceback.print_exc()


def extract_building_points_laspy(
    input_laz_path,
    output_building_laz_path,
    building_class_code=6,
    target_x=None,
    target_y=None,
):
    """
    Extracts points classified as 'Building' from a LAZ file, clusters them,
    and selects the nearest cluster to the target point.

    Args:
        input_laz_path (str): Path to the input LAZ/LAS file.
        output_building_laz_path (str): Path where the output LAZ/LAS file will be saved.
        building_class_code (int): The classification code for buildings (default is 6).
        target_x (float): Target X coordinate to find nearest cluster (optional)
        target_y (float): Target Y coordinate to find nearest cluster (optional)
    """
    if not os.path.exists(input_laz_path):
        print(f"Error: Input LAZ file not found at {input_laz_path}")
        return False

    try:
        from sklearn.cluster import DBSCAN
        from sklearn.metrics import pairwise_distances_argmin_min
        import numpy as np

        print(
            f"\nAttempting to extract and cluster building points from {input_laz_path}..."
        )

        # Read the LAS/LAZ file
        infile = laspy.read(input_laz_path)

        # Check if 'classification' dimension exists
        if "classification" not in infile.point_format.dimension_names:
            print(f"Error: 'classification' dimension not found in {input_laz_path}")
            return False

        # Create a boolean mask for points classified as buildings
        building_mask = infile.classification == building_class_code

        # Print initial count of building points
        initial_building_count = building_mask.sum()
        print(f"Initial building points found: {initial_building_count}")

        if initial_building_count == 0:
            print("No building points found in the input file.")
            return False

        # Get coordinates of building points
        building_points = np.column_stack(
            (infile.x[building_mask], infile.y[building_mask])
        )

        # Perform DBSCAN clustering
        eps = 2.0  # 2 meters between points in a cluster
        min_samples = 10  # Minimum points to form a cluster
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(building_points)

        # Get cluster labels (-1 represents noise)
        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"Number of clusters found: {n_clusters}")

        if n_clusters == 0:
            print("No valid clusters found. Adjusting parameters...")
            # Try with more relaxed parameters
            eps = 3.0
            min_samples = 5
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(building_points)
            labels = db.labels_
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"After adjustment, clusters found: {n_clusters}")

        if n_clusters == 0:
            print("Still no clusters found. Using all building points...")
            selected_mask = building_mask
        else:
            # Calculate cluster centroids
            cluster_centroids = []
            for i in range(n_clusters):
                mask = labels == i
                centroid = building_points[mask].mean(axis=0)
                cluster_centroids.append(centroid)

            # If target coordinates are provided, find nearest cluster
            if target_x is not None and target_y is not None:
                target_point = np.array([[target_x, target_y]])
                nearest_cluster_idx, _ = pairwise_distances_argmin_min(
                    target_point, np.array(cluster_centroids)
                )
                nearest_cluster_idx = nearest_cluster_idx[0]
                print(
                    f"Selected cluster {nearest_cluster_idx} (nearest to target point)"
                )

                # Create mask for points in the nearest cluster
                nearest_cluster_mask = labels == nearest_cluster_idx

                # Map back to original point cloud indices
                selected_mask = np.zeros_like(building_mask, dtype=bool)
                selected_mask[building_mask] = nearest_cluster_mask
            else:
                # If no target point, use the largest cluster
                largest_cluster_idx = max(
                    range(n_clusters), key=lambda i: np.sum(labels == i)
                )
                print(f"Selected cluster {largest_cluster_idx} (largest cluster)")

                # Create mask for points in the largest cluster
                largest_cluster_mask = labels == largest_cluster_idx

                # Map back to original point cloud indices
                selected_mask = np.zeros_like(building_mask, dtype=bool)
                selected_mask[building_mask] = largest_cluster_mask

        # Add buffer around selected points
        if np.any(selected_mask):
            selected_x = infile.x[selected_mask]
            selected_y = infile.y[selected_mask]
            centroid_x = np.mean(selected_x)
            centroid_y = np.mean(selected_y)

            # Create buffer around selected points
            buffer_size = 3.0  # meters
            buffer_mask = (
                (infile.x >= centroid_x - buffer_size)
                & (infile.x <= centroid_x + buffer_size)
                & (infile.y >= centroid_y - buffer_size)
                & (infile.y <= centroid_y + buffer_size)
            )

            # Combine original selection mask with buffer mask
            final_mask = selected_mask | buffer_mask
        else:
            final_mask = selected_mask

        # Select the points based on the final mask
        out_points = infile.points[final_mask]

        # Create a new LasData object for the filtered points
        outfile = laspy.create(
            point_format=infile.point_format, file_version=infile.header.version
        )
        outfile.points = out_points

        # Write the new LAZ file
        outfile.write(output_building_laz_path)

        final_building_count = len(out_points)
        print(f"Successfully extracted {final_building_count} points")
        print(f"Building points saved to: {output_building_laz_path}")
        return True

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        import traceback

        traceback.print_exc()
        return False


def get_laz_crs(laz_file_path):
    """
    Checks and prints the CRS information of a LAZ/LAS file using laspy 2.x.
    """
    if not os.path.exists(laz_file_path):
        print(f"Error: File not found at {laz_file_path}")
        return

    print(f"\nChecking CRS for: {laz_file_path}")
    try:
        with laspy.open(laz_file_path) as fh:
            las = fh.read()
            header = las.header

            # Print coordinate ranges
            print("\nFile coordinate ranges:")
            print(f"X: [{header.x_min:.2f}, {header.x_max:.2f}]")
            print(f"Y: [{header.y_min:.2f}, {header.y_max:.2f}]")
            print(f"Z: [{header.z_min:.2f}, {header.z_max:.2f}]")

            # Check coordinate ranges
            is_pei = (
                300000 <= header.x_min <= 500000 and 600000 <= header.y_min <= 800000
            )

            is_ns = (
                400000 <= header.x_min <= 500000 and 4900000 <= header.y_min <= 5000000
            )

            if is_pei:
                print(
                    "\nCoordinate ranges match PEI Stereographic projection (EPSG:2291)"
                )
                return CRS.from_epsg(2291)
            elif is_ns:
                print("\nCoordinate ranges match Nova Scotia MTM zone 5 (EPSG:2961)")
                return CRS.from_epsg(2961)
            else:
                print(
                    "\nWarning: Could not definitively determine CRS from coordinates"
                )
                print("Coordinates suggest Nova Scotia MTM zone 5 (EPSG:2961)")
                return CRS.from_epsg(2961)

    except Exception as e:
        print(f"Error reading LAZ file: {e}")
        import traceback

        traceback.print_exc()
        return None


def clip_to_nearest_building_cluster(
    input_laz_path,
    output_laz_path,
    target_x,
    target_y,
    search_buffer=30,
    building_class_code=6,
    buildings_only=False,
):
    """
    Clips a LAZ file to the boundary of the nearest building cluster to the target point.

    Args:
        input_laz_path (str): Path to input LAZ file
        output_laz_path (str): Path to save clipped LAZ file
        target_x (float): Target X coordinate
        target_y (float): Target Y coordinate
        search_buffer (float): Buffer distance in meters to search for buildings around target point
        building_class_code (int): Classification code for buildings (default 6)
        buildings_only (bool): If True, output only building points. If False, output all points within boundary

    Returns:
        tuple: (success: bool, boundary_points: np.ndarray or None)
            - success: True if operation was successful
            - boundary_points: Nx2 numpy array of boundary points (X,Y) or None if failed
    """
    try:
        print(f"\nProcessing LAZ file: {input_laz_path}")

        # Read the LAZ file
        infile = laspy.read(input_laz_path)

        # First filter points within the search buffer
        points_mask = (
            (infile.x >= target_x - search_buffer)
            & (infile.x <= target_x + search_buffer)
            & (infile.y >= target_y - search_buffer)
            & (infile.y <= target_y + search_buffer)
        )

        # Further filter for building points
        building_mask = infile.classification == building_class_code
        combined_mask = points_mask & building_mask

        # Get building points coordinates
        building_points = np.column_stack(
            (infile.x[combined_mask], infile.y[combined_mask])
        )

        if len(building_points) < 5:
            print(f"Not enough building points found in the {search_buffer}m buffer")
            return False, None

        print(f"Found {len(building_points)} building points in search area")

        # Perform DBSCAN clustering
        eps = 2.0  # 2 meters between points in a cluster
        min_samples = 10  # Minimum points to form a cluster
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(building_points)

        # Get cluster labels (-1 represents noise)
        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"Initial clustering found {n_clusters} clusters")

        # If no clusters found, try with more relaxed parameters
        if n_clusters == 0:
            eps = 3.0
            min_samples = 5
            db = DBSCAN(eps=eps, min_samples=min_samples).fit(building_points)
            labels = db.labels_
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"After relaxing parameters, found {n_clusters} clusters")

        if n_clusters == 0:
            print("No valid clusters found")
            return False, None

        # Calculate cluster centroids and find nearest
        cluster_info = []
        target_point = np.array([[target_x, target_y]])

        for i in range(n_clusters):
            cluster_mask = labels == i
            cluster_points = building_points[cluster_mask]

            # Calculate centroid
            centroid = cluster_points.mean(axis=0)

            # Calculate convex hull for this cluster
            hull = ConvexHull(cluster_points)
            hull_points = cluster_points[hull.vertices]

            cluster_info.append(
                {
                    "id": i,
                    "centroid": centroid,
                    "points": cluster_points,
                    "hull_points": hull_points,
                }
            )

        # Find nearest cluster
        centroids = np.array([c["centroid"] for c in cluster_info])
        nearest_idx, _ = pairwise_distances_argmin_min(target_point, centroids)
        nearest_idx = nearest_idx[0]
        nearest_cluster = cluster_info[nearest_idx]

        print(f"Selected cluster {nearest_idx} (nearest to target point)")

        # Get convex hull points of nearest cluster
        hull_points = nearest_cluster["hull_points"]

        # Add buffer to hull points
        buffer_size = 2.0  # 2 meter buffer

        # Calculate min/max coordinates with buffer
        min_x = np.min(hull_points[:, 0]) - buffer_size
        max_x = np.max(hull_points[:, 0]) + buffer_size
        min_y = np.min(hull_points[:, 1]) - buffer_size
        max_y = np.max(hull_points[:, 1]) + buffer_size

        # Create final mask for points within buffered boundary
        boundary_mask = (
            (infile.x >= min_x)
            & (infile.x <= max_x)
            & (infile.y >= min_y)
            & (infile.y <= max_y)
        )

        # If buildings_only is True, also apply building classification mask
        if buildings_only:
            final_mask = boundary_mask & building_mask
            print("Extracting building points only within boundary")
        else:
            final_mask = boundary_mask
            print("Extracting all points within boundary")

        # Select points and create new LAZ file
        out_points = infile.points[final_mask]

        # Create output file

        print("Bounds before scaling:")
        print(f"X bounds: {np.min(out_points.x)} to {np.max(out_points.x)}")
        print(f"Y bounds: {np.min(out_points.y)} to {np.max(out_points.y)}")
        print(f"Z bounds: {np.min(out_points.z)} to {np.max(out_points.z)}")

        outfile = laspy.create(
            point_format=infile.point_format, file_version=infile.header.version
        )

        origin_x = math.floor(out_points.x.min() / 500.0) * 500.0
        origin_y = math.ceil(out_points.y.max() / 500.0) * 500.0
        print(f"Origin: {origin_x}, {origin_y}")

        shifted_x = out_points.x - origin_x
        shifted_y = out_points.y - origin_y
        shifted_z = out_points.z  # z is already in metres

        outfile.points = out_points
        outfile.x = shifted_x
        outfile.y = shifted_y
        outfile.z = shifted_z

        outfile.header.offsets = (0.0, 0.0, 0.0)
        print(
            "Bounds after shift:",
            shifted_x.min(),
            shifted_x.max(),
            shifted_y.min(),
            shifted_y.max(),
            shifted_z.min(),
            shifted_z.max(),
        )

        # Write output
        outfile.write(output_laz_path)

        print(f"Successfully extracted {len(out_points)} points")
        print(f"Clipped point cloud saved to: {output_laz_path}")

        # Return success and the boundary points (hull vertices)
        # Sort hull points to form a closed polygon (clockwise order)
        hull = ConvexHull(hull_points)
        boundary_points = hull_points[hull.vertices]

        # Add the first point at the end to close the polygon
        boundary_points = np.vstack((boundary_points, boundary_points[0]))

        return True, boundary_points

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()
        return False, None


# --- Main Script Execution ---
def main(args=None):
    """
    Main function to process LiDAR data for a given address.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process LiDAR data for a given address using a LiDAR index file."
    )

    # Required arguments with -- prefix
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Address to process (e.g., '8 Alderwood Dr, Halifax, NS B3N 1S7')",
    )

    parser.add_argument(
        "--index_path",
        type=str,
        required=True,
        help="Path to the LiDAR index GPKG file",
    )

    # Optional arguments
    parser.add_argument(
        "--show_3d",
        action="store_true",
        help="Show 3D visualizations of the point clouds",
    )

    parser.add_argument(
        "--point_correction",
        action="store_true",
        help="Allow manual correction of the point location on satellite image",
    )

    # Parse arguments
    args = parser.parse_args(args)

    # Create output directories
    os.makedirs(LIDAR_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Geocode Address ---
    print(f"\nProcessing address: {args.address}")
    print(f"Using index file: {args.index_path}")

    image, lat, lon = geocode_satellite_image(
        address=args.address,
        point_correction=args.point_correction,
        API_KEY=GOOGLE_API_KEY,
    )
    if lat is None:
        print("Failed to geocode address. Exiting.")
        qgs.exitQgis()
        sys.exit(1)

    # Save the satellite image
    output_image_path = os.path.join(OUTPUT_DIR, SATELLITE_IMAGE)
    image.save(output_image_path)
    print(f"Satellite image saved to: {output_image_path}")

    # --- Transform Coordinates to UTM (EPSG:3978) ---
    utm_x, utm_y = transform_coords(lat, lon, target_epsg=3978)
    print(f"Transformed coordinates: {utm_x}, {utm_y}")

    # --- Find Corresponding LiDAR Tile ---
    lidar_url = find_lidar_tile(utm_x, utm_y, args.index_path)

    if lidar_url:
        # --- Extract filename from URL and define local path ---
        parsed_url = urlparse(lidar_url)
        laz_filename = os.path.basename(parsed_url.path)
        local_laz_path = os.path.join(LIDAR_DIR, laz_filename)

        # --- Check if LAZ file exists locally ---
        if not os.path.exists(local_laz_path):
            print(f"\nLiDAR file not found in '{LIDAR_DIR}'.")
            print("Please download the file from the following link:")
            print(f"\nDownload Link: {lidar_url}\n")
            print(f"Please save the file to: {LIDAR_DIR}\n")
            input("After downloading the file, press Enter to continue...")

            if not os.path.exists(local_laz_path):
                print("\nError: LiDAR file still not found after download. Exiting.")
                qgs.exitQgis()
                sys.exit(1)

            print("LiDAR file found. Proceeding...")

        # Get CRS info and transform coordinates if needed
        crs_info = get_laz_crs(local_laz_path)
        transformed_x, transformed_y = utm_x, utm_y

        # --- Process and Save Point Cloud Subset ---
        output_laz_subset_path = os.path.join(OUTPUT_DIR, LIDAR_SUBSET)
        output_buildings_path = os.path.join(OUTPUT_DIR, BUILDINGS_OUTPUT)

        # Transform coordinates based on detected CRS
        if crs_info:
            target_epsg = crs_info.to_epsg()
            if target_epsg == 2961:  # Nova Scotia MTM zone 5
                print(
                    "\nTransforming coordinates to Nova Scotia MTM zone 5 (EPSG:2961)..."
                )
                transformer = Transformer.from_crs(
                    "EPSG:3978", "EPSG:2961", always_xy=True
                )
                transformed_x, transformed_y = transformer.transform(utm_x, utm_y)
                print(
                    f"Transformed coordinates: X={transformed_x:.2f}, Y={transformed_y:.2f}"
                )
            elif target_epsg == 2291:  # PEI Stereographic
                print("\nTransforming coordinates to PEI Stereographic (EPSG:2291)...")
                transformer = Transformer.from_crs(
                    "EPSG:3978", "EPSG:2291", always_xy=True
                )
                transformed_x, transformed_y = transformer.transform(utm_x, utm_y)
                print(
                    f"Transformed coordinates: X={transformed_x:.2f}, Y={transformed_y:.2f}"
                )
            else:
                print(f"\nUnexpected CRS EPSG:{target_epsg}. Using coordinates as-is.")

        if process_lidar_subset_with_laspy(
            local_laz_path,
            output_laz_subset_path,
            transformed_x,
            transformed_y,
            buffer_m=20,
        ):
            print(f"\nPoint cloud subset saved to: {output_laz_subset_path}")

            # Extract building points with clustering

            _, boundary_points = clip_to_nearest_building_cluster(
                local_laz_path,
                output_buildings_path,
                target_x=transformed_x,
                target_y=transformed_y,
            )
            print(f"\nBuilding points saved to: {output_buildings_path}")

            # Save boundary points to contour file
            if boundary_points is not None:
                contour_path = os.path.join(OUTPUT_DIR, CONTOUR)
                np.save(contour_path, boundary_points)
                print(f"\nContour points saved to: {contour_path}")
            # if extract_building_points_laspy(
            #     output_laz_subset_path,
            #     output_buildings_path,
            #     target_x=transformed_x,
            #     target_y=transformed_y,
            # ):
            #     print(f"\nBuilding points saved to: {output_buildings_path}")

            # Only show visualizations if requested
            if args.show_3d:
                visualize_point_cloud(
                    output_laz_subset_path,
                    title="LiDAR Point Cloud",
                    point_size=1.0,
                    color_by="elevation",
                )
                visualize_point_cloud(
                    output_buildings_path,
                    title="Building Points",
                    point_size=1.0,
                    color_by="elevation",
                )
        else:
            print("\nFailed to process point cloud subset.")
            qgs.exitQgis()
            sys.exit(1)

    else:
        print(
            "\nNo relevant LiDAR tile found for the given address. Cannot subset point cloud."
        )

    # --- Clean up QGIS environment ---
    qgs.exitQgis()
    print("\nScript finished. QGIS environment uninitialized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
