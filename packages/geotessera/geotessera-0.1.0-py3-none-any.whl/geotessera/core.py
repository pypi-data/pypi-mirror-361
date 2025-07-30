"""Core module for accessing and working with Tessera geospatial embeddings.

This module provides the main GeoTessera class which interfaces with pre-computed
satellite embeddings from the Tessera foundation model. The embeddings compress
a full year of Sentinel-1 and Sentinel-2 observations into 128-dimensional
representation maps at 10m spatial resolution.

The module handles:
- Automatic data fetching and caching from remote servers
- Dequantization of compressed embeddings using scale factors
- Geographic tile discovery and intersection analysis
- Visualization and export of embeddings as GeoTIFF files
- Merging multiple tiles with proper coordinate alignment
"""
from pathlib import Path
from typing import Optional, Union, List, Tuple, Iterator
import importlib.resources
import pooch
import geopandas as gpd
import numpy as np


# Base URL for Tessera data downloads
TESSERA_BASE_URL = "https://dl-2.tessera.wiki"


class GeoTessera:
    """Interface for accessing Tessera foundation model embeddings.
    
    GeoTessera provides access to pre-computed embeddings from the Tessera
    foundation model, which processes Sentinel-1 and Sentinel-2 satellite imagery
    to generate dense representation maps. Each embedding compresses a full year
    of temporal-spectral observations into 128 channels at 10m resolution.
    
    The embeddings are organized in a global 0.1-degree grid system, with each
    tile covering approximately 11km × 11km at the equator. Files are fetched
    on-demand and cached locally for efficient access.
    
    Attributes:
        version: Dataset version identifier (default: "v1")
        cache_dir: Local directory for caching downloaded files
        
    Example:
        >>> gt = GeoTessera()
        >>> # Fetch embeddings for Cambridge, UK
        >>> embedding = gt.get_embedding(lat=52.2053, lon=0.1218)
        >>> print(f"Shape: {embedding.shape}")  # (height, width, 128)
        >>> # Visualize as RGB composite
        >>> gt.visualize_embedding(embedding, bands=[10, 20, 30])
    """
    
    def __init__(self, version: str = "v1", cache_dir: Optional[Union[str, Path]] = None):
        """Initialize GeoTessera client for accessing Tessera embeddings.
        
        Creates a client instance that can fetch and work with pre-computed
        satellite embeddings. Data is automatically cached locally after first
        download to improve performance.
        
        Args:
            version: Dataset version to use. Currently "v1" is available.
            cache_dir: Directory for caching downloaded files. If None, uses
                      the system's default cache directory (~/.cache/geotessera
                      on Unix-like systems).
                      
        Raises:
            ValueError: If the specified version is not supported.
            
        Note:
            The client lazily loads registry files for each year as needed,
            improving startup performance when working with specific years.
        """
        self.version = version
        self._cache_dir = cache_dir
        self._pooch = None
        self._landmask_pooch = None
        self._available_embeddings = []
        self._available_landmasks = []
        self._loaded_years = set()  # Track which years have been loaded
        self._initialize_pooch()
    
    def _initialize_pooch(self):
        """Initialize Pooch data fetchers for embeddings and land masks.
        
        Sets up two Pooch instances:
        1. Main fetcher for numpy embedding files (.npy and _scales.npy)
        2. Land mask fetcher for GeoTIFF files containing binary land/water
           masks and coordinate reference system metadata
           
        Registry files are loaded lazily per year to improve performance.
        """
        cache_path = self._cache_dir if self._cache_dir else pooch.os_cache("geotessera")
        
        # Initialize main pooch for numpy embeddings
        self._pooch = pooch.create(
            path=cache_path,
            base_url=f"{TESSERA_BASE_URL}/{self.version}/global_0.1_degree_representation/",
            version=self.version,
            registry=None,
            env="TESSERA_DATA_DIR",
        )
        
        # Registry files will be loaded lazily when needed
        # This is handled by _ensure_year_loaded method
        
        # Initialize land mask pooch for landmask GeoTIFF files
        # These TIFFs serve dual purposes:
        # 1. Binary land/water distinction (pixel values 0=water, 1=land)
        # 2. Coordinate reference system metadata for proper georeferencing
        self._landmask_pooch = pooch.create(
            path=cache_path,
            base_url=f"{TESSERA_BASE_URL}/{self.version}/global_0.1_degree_tiff_all/",
            version=self.version,
            registry=None,
            env="TESSERA_DATA_DIR", # CR:avsm FIXME this should be a separate subdir
        )
        
        # Load land mask registry dynamically
        self._load_landmask_registry()
        
        # Parse and cache available landmasks (still load immediately)
        self._parse_available_landmasks()
    
    def _load_landmask_registry(self):
        """Load registry of available land mask GeoTIFF files.
        
        Land mask files are auxiliary data that provide:
        1. Binary land/water classification (pixel values: 0=water, 1=land)
        2. Optimal coordinate reference system (CRS) for each tile
        3. Precise georeferencing metadata for coordinate alignment
        
        These files are essential for accurate merging of multiple tiles,
        especially when tiles span different UTM zones or require reprojection.
        The CRS metadata ensures proper alignment without coordinate skew.
        
        Note:
            This method is called during initialization. The registry download
            is attempted but failures are handled gracefully, allowing the
            system to work without land masks if necessary.
        """
        try:
            cache_path = self._cache_dir if self._cache_dir else pooch.os_cache("geotessera")
            
            # Use pooch.retrieve to get the registry file without known hash
            registry_file = pooch.retrieve(
                url=f"{TESSERA_BASE_URL}/{self.version}/global_0.1_degree_tiff_all/registry.txt",
                known_hash=None,
                fname="landmask_registry.txt",
                path=cache_path,
                progressbar=True
            )
            
            # Load the registry into the land mask pooch
            self._landmask_pooch.load_registry(registry_file)
            
        except Exception as e:
            print(f"Warning: Could not load land mask registry: {e}")
            # Continue without land mask support if registry loading fails
    
    def _ensure_year_loaded(self, year: int):
        """Ensure registry data for a specific year is loaded.
        
        Tessera embeddings are organized by year, with separate registry files
        for each year's data. This method lazily loads the registry when first
        accessing data from a particular year.
        
        Args:
            year: Year to load (e.g., 2024). Must be between 2017-2024.
            
        Raises:
            ValueError: If no registry exists for the specified year.
            
        Note:
            This method is called automatically when fetching embeddings.
            Users typically don't need to call it directly.
        """
        if year not in self._loaded_years:
            registry_filename = f"registry_{year}.txt"
            try:
                with importlib.resources.open_text("geotessera", registry_filename) as registry_file:
                    self._pooch.load_registry(registry_file)
                self._loaded_years.add(year)
                # Re-parse available embeddings to include the new year
                self._parse_available_embeddings()
            except FileNotFoundError:
                raise ValueError(f"Registry file for year {year} not found. Available years: {self.get_available_years()}")
    
    def get_available_years(self) -> List[int]:
        """List all years with available Tessera embeddings.
        
        Scans for registry files to determine which years have pre-computed
        embeddings available. Currently supports years 2017-2024.
        
        Returns:
            List of years with available data, sorted in ascending order.
            
        Example:
            >>> gt = GeoTessera()
            >>> years = gt.get_available_years()
            >>> print(years)  # [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        """
        available_years = []
        for year in range(2017, 2025):  # Check years 2017-2024
            registry_filename = f"registry_{year}.txt"
            try:
                with importlib.resources.open_text("geotessera", registry_filename):
                    available_years.append(year)
            except FileNotFoundError:
                continue
        return available_years
    
    def fetch_embedding(self, lat: float, lon: float, year: int = 2024, 
                       progressbar: bool = True) -> np.ndarray:
        """Fetch and dequantize Tessera embeddings for a geographic location.
        
        Downloads both the quantized embedding array and its corresponding scale
        factors, then performs dequantization by element-wise multiplication.
        The embeddings represent learned features from a full year of Sentinel-1
        and Sentinel-2 satellite observations.
        
        Args:
            lat: Latitude in decimal degrees. Will be rounded to nearest 0.1°
                 grid cell (e.g., 52.23 → 52.20).
            lon: Longitude in decimal degrees. Will be rounded to nearest 0.1°
                 grid cell (e.g., 0.17 → 0.15).
            year: Year of embeddings to fetch (2017-2024). Different years may
                  capture different environmental conditions.
            progressbar: Whether to display download progress. Useful for tracking
                        large file downloads.
            
        Returns:
            Dequantized embedding array of shape (height, width, 128) containing
            128-dimensional feature vectors for each 10m pixel. Typical tile
            dimensions are approximately 1100×1100 pixels.
            
        Raises:
            ValueError: If the requested tile is not available or year is invalid.
            IOError: If download fails after retries.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Fetch embeddings for central London
            >>> embedding = gt.fetch_embedding(lat=51.5074, lon=-0.1278)
            >>> print(f"Tile shape: {embedding.shape}")
            >>> print(f"Feature dimensions: {embedding.shape[-1]} channels")
            
        Note:
            Files are cached after first download. Subsequent requests for the
            same tile will load from cache unless the cache is cleared.
        """
        # Ensure the registry for this year is loaded
        self._ensure_year_loaded(year)
        # Format coordinates to match file naming convention
        grid_name = f"grid_{lon:.2f}_{lat:.2f}"
        
        # Fetch both the main embedding and scales files
        embedding_path = f"{year}/{grid_name}/{grid_name}.npy"
        scales_path = f"{year}/{grid_name}/{grid_name}_scales.npy"
        
        embedding_file = self._pooch.fetch(embedding_path, progressbar=progressbar)
        scales_file = self._pooch.fetch(scales_path, progressbar=progressbar)
        
        # Load both files
        embedding = np.load(embedding_file)  # shape: (height, width, channels)
        scales = np.load(scales_file)        # shape: (height, width)
        
        # Dequantize by multiplying embedding by scales across all channels
        # Broadcasting scales from (height, width) to (height, width, channels)
        dequantized = embedding.astype(np.float32) * scales[:, :, np.newaxis]
        
        return dequantized
    
    def get_embedding(self, lat: float, lon: float, year: int = 2024) -> np.ndarray:
        """Get dequantized Tessera embeddings for a location (convenience method).
        
        This is a convenience wrapper around fetch_embedding() that always shows
        a progress bar during download. Use this for interactive applications.
        
        Args:
            lat: Latitude in decimal degrees (will be rounded to 0.1° grid).
            lon: Longitude in decimal degrees (will be rounded to 0.1° grid).
            year: Year of embeddings to retrieve (2017-2024).
            
        Returns:
            Dequantized embedding array of shape (height, width, 128).
            
        See Also:
            fetch_embedding: Lower-level method with progress bar control.
            
        Example:
            >>> gt = GeoTessera()
            >>> embedding = gt.get_embedding(lat=40.7128, lon=-74.0060)  # NYC
        """
        return self.fetch_embedding(lat, lon, year, progressbar=True)
    
    def _fetch_landmask(self, lat: float, lon: float, progressbar: bool = True) -> str:
        """Download land mask GeoTIFF for coordinate reference information.
        
        Land mask files contain binary land/water data and crucial CRS metadata
        that defines the optimal projection for each tile. This metadata is used
        during tile merging to ensure proper geographic alignment.
        
        Args:
            lat: Latitude in decimal degrees (rounded to 0.1° grid).
            lon: Longitude in decimal degrees (rounded to 0.1° grid).
            progressbar: Whether to show download progress.
            
        Returns:
            Local file path to the cached land mask GeoTIFF.
            
        Raises:
            RuntimeError: If land mask registry was not loaded successfully.
            
        Note:
            This is an internal method used primarily during merge operations.
            End users typically don't need to call this directly.
        """
        if not self._landmask_pooch:
            raise RuntimeError("Land mask registry not loaded. Check initialization.")
        
        # Format coordinates to match file naming convention
        landmask_filename = f"grid_{lon:.2f}_{lat:.2f}.tiff"
        
        return self._landmask_pooch.fetch(landmask_filename, progressbar=progressbar)
    
    def _list_available_landmasks(self) -> Iterator[Tuple[float, float]]:
        """Iterate over available land mask tiles.
        
        Provides access to the catalog of land mask GeoTIFF files. Each file
        contains binary land/water classification and coordinate system metadata
        for its corresponding embedding tile.
        
        Returns:
            Iterator yielding (latitude, longitude) tuples for each available
            land mask, sorted by latitude then longitude.
            
        Note:
            Land masks are auxiliary data used primarily for coordinate alignment
            during tile merging operations.
        """
        return iter(self._available_landmasks)
    
    def _count_available_landmasks(self) -> int:
        """Count total number of available land mask files.
        
        Returns:
            Number of land mask GeoTIFF files in the registry.
            
        Note:
            Land mask availability may be limited compared to embedding tiles.
            Not all embedding tiles have corresponding land masks.
        """
        return len(self._available_landmasks)
    
    def _parse_available_embeddings(self):
        """Parse registry files to build index of available embedding tiles.
        
        Scans through loaded registry files to extract metadata about available
        tiles. Each tile is identified by year, latitude, and longitude. This
        method is called automatically when registry files are loaded.
        
        The index is stored as a sorted list of (year, lat, lon) tuples for
        efficient searching and iteration.
        """
        embeddings = []
        
        if self._pooch and self._pooch.registry:
            for file_path in self._pooch.registry.keys():
                # Only process .npy files that are not scale files
                if file_path.endswith('.npy') and not file_path.endswith('_scales.npy'):
                    # Parse file path: e.g., "2024/grid_0.15_52.05/grid_0.15_52.05.npy"
                    parts = file_path.split('/')
                    if len(parts) >= 3:
                        year_str = parts[0]
                        grid_name = parts[1]  # e.g., "grid_0.15_52.05"
                        
                        try:
                            year = int(year_str)
                            
                            # Extract coordinates from grid name
                            if grid_name.startswith('grid_'):
                                coords = grid_name[5:].split('_')  # Remove "grid_" prefix
                                if len(coords) == 2:
                                    lon = float(coords[0])
                                    lat = float(coords[1])
                                    embeddings.append((year, lat, lon))
                                    
                        except (ValueError, IndexError):
                            continue
        
        # Sort by year, then lat, then lon for consistent ordering
        embeddings.sort(key=lambda x: (x[0], x[1], x[2]))
        self._available_embeddings = embeddings
    
    def _parse_available_landmasks(self):
        """Parse land mask registry to index available GeoTIFF files.
        
        Land mask files serve dual purposes:
        1. Provide binary land/water classification (0=water, 1=land)
        2. Store coordinate reference system metadata for proper georeferencing
        
        This method builds an index of available land mask tiles as (lat, lon)
        tuples for efficient lookup during merge operations.
        """
        landmasks = []
        
        if not self._landmask_pooch or not self._landmask_pooch.registry:
            return
        
        for file_path in self._landmask_pooch.registry.keys():
            # Parse file path: e.g., "grid_0.15_52.05.tiff"
            if file_path.endswith('.tiff'):
                # Extract coordinates from filename
                filename = Path(file_path).name
                if filename.startswith('grid_'):
                    coords = filename[5:-5].split('_')  # Remove "grid_" prefix and ".tiff" suffix
                    if len(coords) == 2:
                        try:
                            lon = float(coords[0])
                            lat = float(coords[1])
                            landmasks.append((lat, lon))
                        except ValueError:
                            continue
        
        # Sort by lat, then lon for consistent ordering
        landmasks.sort(key=lambda x: (x[0], x[1]))
        self._available_landmasks = landmasks
    
    def list_available_embeddings(self) -> Iterator[Tuple[int, float, float]]:
        """Iterate over all available embedding tiles across all years.
        
        Provides an iterator over the complete catalog of available Tessera
        embeddings. Each tile covers a 0.1° × 0.1° area (approximately 
        11km × 11km at the equator) and contains embeddings for one year.
        
        Returns:
            Iterator yielding (year, latitude, longitude) tuples for each
            available tile. Tiles are sorted by year, then latitude, then
            longitude.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Count tiles in a specific region
            >>> uk_tiles = [(y, lat, lon) for y, lat, lon in gt.list_available_embeddings()
            ...             if 49 <= lat <= 59 and -8 <= lon <= 2]
            >>> print(f"UK tiles available: {len(uk_tiles)}")
            
        Note:
            On first call, this method will load registry files for all available
            years, which may take a few seconds.
        """
        # If no years have been loaded yet, load all available years
        if not self._loaded_years:
            available_years = self.get_available_years()
            for year in available_years:
                try:
                    self._ensure_year_loaded(year)
                except ValueError:
                    # Skip years that can't be loaded
                    continue
        
        return iter(self._available_embeddings)
    
    def count_available_embeddings(self) -> int:
        """Count total number of available embedding tiles across all years.
        
        Returns:
            Total number of available embedding tiles in the dataset.
            
        Example:
            >>> gt = GeoTessera()
            >>> total = gt.count_available_embeddings()
            >>> print(f"Total tiles available: {total:,}")
        """
        return len(self._available_embeddings)
    
    
    def get_tiles_for_topojson(self, topojson_path: Union[str, Path]) -> List[Tuple[float, float, str]]:
        """Find all embedding tiles that intersect with TopoJSON geometries.
        
        Analyzes a TopoJSON file containing geographic features and identifies
        which Tessera embedding tiles overlap with those features. This is useful
        for efficiently fetching only the tiles needed to cover a specific region
        or administrative boundary.
        
        Args:
            topojson_path: Path to a TopoJSON file containing one or more
                          geographic features (polygons, multipolygons, etc.).
            
        Returns:
            List of tuples containing (latitude, longitude, tile_path) for each
            tile that intersects with any geometry in the TopoJSON file. The
            tile_path can be used with the Pooch fetcher.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Find tiles covering a city boundary
            >>> tiles = gt.get_tiles_for_topojson("city_boundary.json")
            >>> print(f"Need {len(tiles)} tiles to cover the region")
            >>> # Fetch all tiles
            >>> for lat, lon, _ in tiles:
            ...     embedding = gt.get_embedding(lat, lon)
            
        Note:
            The method uses conservative intersection testing - a tile is included
            if any part of it overlaps with the TopoJSON geometries.
        """
        from shapely.geometry import box
        
        # Read the TopoJSON file
        gdf = gpd.read_file(topojson_path)
        
        # Create a unified geometry (union of all features)
        # This handles the convex hull of all shapes properly
        unified_geom = gdf.unary_union
        
        # Get the bounds to limit our search area
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Round to 0.1 degree grid (Tessera grid resolution) to get search bounds
        min_lon_grid = np.floor(min_lon * 10) / 10
        max_lon_grid = np.ceil(max_lon * 10) / 10
        min_lat_grid = np.floor(min_lat * 10) / 10
        max_lat_grid = np.ceil(max_lat * 10) / 10
        
        # Get all available tiles
        available_tiles = self.list_available_embeddings()
        
        # Filter tiles that actually intersect with the geometries
        overlapping_tiles = []
        
        for year, tile_lat, tile_lon in available_tiles:
            # First check if tile is within the bounding box (optimization)
            if (tile_lon >= min_lon_grid and tile_lon <= max_lon_grid and
                tile_lat >= min_lat_grid and tile_lat <= max_lat_grid):
                
                # Create a box representing the tile (0.1 degree grid)
                tile_box = box(tile_lon, tile_lat, tile_lon + 0.1, tile_lat + 0.1)
                
                # Check if the tile box intersects with the actual geometries
                # Conservative approach: if ANY part of the boundary is within the tile, include it
                if unified_geom.intersects(tile_box):
                    # Create the tile path for reference
                    tile_path = f"{year}/grid_{tile_lon:.2f}_{tile_lat:.2f}/grid_{tile_lon:.2f}_{tile_lat:.2f}.npy"
                    overlapping_tiles.append((tile_lat, tile_lon, tile_path))
        
        return overlapping_tiles
    
    def visualize_topojson_as_tiff(self, topojson_path: Union[str, Path], 
                                   output_path: str = "topojson_tiles.tiff",
                                   bands: List[int] = [0, 1, 2],
                                   normalize: bool = True) -> str:
        """Create a GeoTIFF mosaic of embeddings covering a TopoJSON region.
        
        Generates a georeferenced TIFF image by mosaicking all Tessera tiles that
        intersect with the geometries in a TopoJSON file. The output is a clean
        satellite-style visualization without any overlays or decorations.
        
        Args:
            topojson_path: Path to TopoJSON file defining the region of interest.
            output_path: Output filename for the GeoTIFF (default: "topojson_tiles.tiff").
            bands: Three embedding channel indices to map to RGB. Default [0,1,2]
                   uses the first three channels. Try different combinations to
                   highlight different features.
            normalize: If True, normalizes each band to 0-1 range for better
                      contrast. If False, uses raw embedding values.
            
        Returns:
            Path to the created GeoTIFF file.
            
        Raises:
            ImportError: If rasterio is not installed.
            ValueError: If no tiles overlap with the TopoJSON region.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Create false-color image of a national park
            >>> gt.visualize_topojson_as_tiff(
            ...     "park_boundary.json",
            ...     "park_tessera.tiff",
            ...     bands=[10, 20, 30]  # Custom band combination
            ... )
            
        Note:
            The output TIFF includes georeferencing information and can be
            opened in GIS software like QGIS or ArcGIS. Large regions may
            take significant time to process and require substantial memory.
        """
        try:
            import rasterio
            from rasterio.transform import from_bounds
        except ImportError:
            raise ImportError("Please install rasterio and pillow for TIFF export: pip install rasterio pillow")
        
        # Read the TopoJSON file
        gpd.read_file(topojson_path)
        
        # Get overlapping tiles
        tiles = self.get_tiles_for_topojson(topojson_path)
        
        if not tiles:
            print("No overlapping tiles found")
            return output_path
        
        # Calculate bounding box for all tiles
        lon_min = min(lon for _, lon, _ in tiles)
        lat_min = min(lat for lat, _, _ in tiles)
        lon_max = max(lon for _, lon, _ in tiles) + 0.1
        lat_max = max(lat for lat, _, _ in tiles) + 0.1
        
        # Download and process each tile
        tile_data_dict = {}
        print(f"Processing {len(tiles)} tiles for TIFF export...")
        
        for i, (lat, lon, tile_path) in enumerate(tiles):
            print(f"Processing tile {i+1}/{len(tiles)}: ({lat:.2f}, {lon:.2f})")
            
            try:
                # Download and dequantize the tile data
                data = self.fetch_embedding(lat=lat, lon=lon, progressbar=False)
                
                # Extract bands for visualization
                vis_data = data[:, :, bands].copy()
                
                # Normalize if requested
                if normalize:
                    for j in range(vis_data.shape[2]):
                        channel = vis_data[:, :, j]
                        min_val = np.min(channel)
                        max_val = np.max(channel)
                        if max_val > min_val:
                            vis_data[:, :, j] = (channel - min_val) / (max_val - min_val)
                
                # Ensure we have valid RGB data in [0,1] range
                vis_data = np.clip(vis_data, 0, 1)
                
                # Store the processed tile data
                tile_data_dict[(lat, lon)] = vis_data
                
            except Exception as e:
                print(f"WARNING: Failed to download tile ({lat:.2f}, {lon:.2f}): {e}")
                tile_data_dict[(lat, lon)] = None
        
        # Determine the resolution based on the first valid tile
        tile_height, tile_width = None, None
        for (lat, lon), tile_data in tile_data_dict.items():
            if tile_data is not None:
                tile_height, tile_width = tile_data.shape[:2]
                break
        
        if tile_height is None:
            raise ValueError("No valid tiles were downloaded")
        
        # Calculate the size of the output mosaic
        # Each tile covers 0.1 degrees, calculate pixels per degree
        pixels_per_degree_lat = tile_height / 0.1
        pixels_per_degree_lon = tile_width / 0.1
        
        # Calculate output dimensions
        mosaic_width = int((lon_max - lon_min) * pixels_per_degree_lon)
        mosaic_height = int((lat_max - lat_min) * pixels_per_degree_lat)
        
        # Create the mosaic array
        mosaic = np.zeros((mosaic_height, mosaic_width, 3), dtype=np.float32)
        
        # Place each tile in the mosaic
        for (lat, lon), tile_data in tile_data_dict.items():
            if tile_data is not None:
                # Calculate pixel coordinates for this tile
                x_start = int((lon - lon_min) * pixels_per_degree_lon)
                y_start = int((lat_max - lat - 0.1) * pixels_per_degree_lat)  # Flip Y axis
                
                # Get actual tile dimensions
                tile_h, tile_w = tile_data.shape[:2]
                
                # Calculate end positions
                y_end = y_start + tile_h
                x_end = x_start + tile_w
                
                # Clip to mosaic bounds
                y_start_clipped = max(0, y_start)
                x_start_clipped = max(0, x_start)
                y_end_clipped = min(mosaic_height, y_end)
                x_end_clipped = min(mosaic_width, x_end)
                
                # Calculate tile region to copy
                tile_y_start = y_start_clipped - y_start
                tile_x_start = x_start_clipped - x_start
                tile_y_end = tile_y_start + (y_end_clipped - y_start_clipped)
                tile_x_end = tile_x_start + (x_end_clipped - x_start_clipped)
                
                # Place tile in mosaic if there's any overlap
                if y_end_clipped > y_start_clipped and x_end_clipped > x_start_clipped:
                    mosaic[y_start_clipped:y_end_clipped, x_start_clipped:x_end_clipped] = \
                        tile_data[tile_y_start:tile_y_end, tile_x_start:tile_x_end]
        
        # Convert to uint8 for TIFF export
        mosaic_uint8 = (mosaic * 255).astype(np.uint8)
        
        # Create georeferencing transform
        transform = from_bounds(lon_min, lat_min, lon_max, lat_max, mosaic_width, mosaic_height)
        
        # Write the GeoTIFF
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=mosaic_height,
            width=mosaic_width,
            count=3,
            dtype='uint8',
            crs='EPSG:4326',  # WGS84
            transform=transform,
            compress='lzw'
        ) as dst:
            # Write RGB bands
            for i in range(3):
                dst.write(mosaic_uint8[:, :, i], i + 1)
        
        print(f"Exported high-resolution TIFF to {output_path}")
        print(f"Dimensions: {mosaic_width}x{mosaic_height} pixels")
        print(f"Geographic bounds: {lon_min:.4f}, {lat_min:.4f}, {lon_max:.4f}, {lat_max:.4f}")
        
        return output_path
    
    def export_single_tile_as_tiff(self, lat: float, lon: float, output_path: str,
                                   year: int = 2024, bands: List[int] = [0, 1, 2],
                                   normalize: bool = True) -> str:
        """Export a single Tessera embedding tile as a georeferenced GeoTIFF.
        
        Creates a GeoTIFF file from a single embedding tile, selecting three
        channels to visualize as RGB. The output includes proper georeferencing
        metadata for use in GIS applications.
        
        Args:
            lat: Latitude of tile in decimal degrees (rounded to 0.1° grid).
            lon: Longitude of tile in decimal degrees (rounded to 0.1° grid).
            output_path: Filename for the output GeoTIFF.
            year: Year of embeddings to export (2017-2024).
            bands: Three channel indices to map to RGB. Each index must be
                   between 0-127. Different combinations highlight different
                   features (e.g., vegetation, water, urban areas).
            normalize: If True, stretches values to use full 0-255 range for
                      better visualization. If False, preserves relative values.
            
        Returns:
            Path to the created GeoTIFF file.
            
        Raises:
            ImportError: If rasterio is not installed.
            ValueError: If bands list doesn't contain exactly 3 indices.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Export a tile over Paris with custom visualization
            >>> gt.export_single_tile_as_tiff(
            ...     lat=48.85, lon=2.35,
            ...     output_path="paris_2024.tiff",
            ...     bands=[25, 50, 75]  # Custom band selection
            ... )
            
        Note:
            Output files can be large (typically 10-50 MB per tile). The GeoTIFF
            uses LZW compression to reduce file size.
        """
        try:
            import rasterio
            from rasterio.transform import from_bounds
        except ImportError:
            raise ImportError("Please install rasterio for TIFF export: pip install rasterio")
        
        # Fetch and dequantize the embedding
        data = self.fetch_embedding(lat=lat, lon=lon, year=year, progressbar=True)
        
        # Extract bands for visualization
        vis_data = data[:, :, bands].copy()
        
        # Normalize if requested
        if normalize:
            for i in range(vis_data.shape[2]):
                channel = vis_data[:, :, i]
                min_val = np.min(channel)
                max_val = np.max(channel)
                if max_val > min_val:
                    vis_data[:, :, i] = (channel - min_val) / (max_val - min_val)
        
        # Ensure we have valid RGB data in [0,1] range
        vis_data = np.clip(vis_data, 0, 1)
        
        # Convert to uint8 for TIFF export
        vis_data_uint8 = (vis_data * 255).astype(np.uint8)
        
        # Get dimensions
        height, width = vis_data.shape[:2]
        
        # Calculate geographic bounds (each tile covers 0.1 degrees)
        lon_min = lon
        lat_min = lat
        lon_max = lon + 0.1
        lat_max = lat + 0.1
        
        # Create georeferencing transform
        transform = from_bounds(lon_min, lat_min, lon_max, lat_max, width, height)
        
        # Write the GeoTIFF
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=3,
            dtype='uint8',
            crs='EPSG:4326',  # WGS84
            transform=transform,
            compress='lzw'
        ) as dst:
            # Write RGB bands
            for i in range(3):
                dst.write(vis_data_uint8[:, :, i], i + 1)
        
        print(f"Exported tile to {output_path}")
        print(f"Dimensions: {width}x{height} pixels")
        print(f"Geographic bounds: {lon_min:.4f}, {lat_min:.4f}, {lon_max:.4f}, {lat_max:.4f}")
        
        return output_path
    
    def _merge_landmasks_for_region(self, bounds: Tuple[float, float, float, float], 
                              output_path: str, target_crs: str = "EPSG:4326") -> str:
        """Merge land mask tiles for a geographic region with proper alignment.
        
        Combines multiple land mask GeoTIFF tiles into a single file, handling
        coordinate system differences between tiles. Each tile may use a different
        optimal projection (e.g., different UTM zones), so this method reprojects
        all tiles to a common coordinate system before merging.
        
        The land masks provide:
        - Binary classification: 0 = water, 1 = land
        - Coordinate system metadata for accurate georeferencing
        - Projection information to avoid coordinate skew
        
        Args:
            bounds: Geographic bounds as (min_lon, min_lat, max_lon, max_lat)
                    in WGS84 decimal degrees.
            output_path: Filename for the merged GeoTIFF output.
            target_crs: Target coordinate reference system. Default "EPSG:4326"
                       (WGS84). Can be any CRS supported by rasterio.
            
        Returns:
            Path to the created merged land mask file.
            
        Raises:
            ImportError: If rasterio is not installed.
            ValueError: If no land mask tiles are found for the region.
            
        Note:
            This is an internal method used by merge_embeddings_for_region().
            Binary masks are automatically converted to visible grayscale
            (0 → 0, 1 → 255) for better visualization.
        """
        try:
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject
            from rasterio.enums import Resampling
            from rasterio.merge import merge
            import tempfile
            import shutil
        except ImportError:
            raise ImportError("Please install rasterio for TIFF merging: pip install rasterio")
        
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Find all land mask tiles that intersect with the bounds
        tiles_to_merge = []
        for lat, lon in self._list_available_landmasks():
            # Check if tile intersects with bounds (0.1 degree grid)
            tile_min_lon, tile_min_lat = lon, lat
            tile_max_lon, tile_max_lat = lon + 0.1, lat + 0.1
            
            if (tile_min_lon < max_lon and tile_max_lon > min_lon and
                tile_min_lat < max_lat and tile_max_lat > min_lat):
                tiles_to_merge.append((lat, lon))
        
        if not tiles_to_merge:
            raise ValueError("No land mask tiles found for the specified region")
        
        print(f"Found {len(tiles_to_merge)} land mask tiles to merge")
        
        # Download all required land mask tiles
        tile_paths = []
        for lat, lon in tiles_to_merge:
            try:
                tile_path = self._fetch_landmask(lat, lon, progressbar=True)
                tile_paths.append(tile_path)
            except Exception as e:
                print(f"Warning: Could not fetch land mask tile ({lat}, {lon}): {e}")
                continue
        
        if not tile_paths:
            raise ValueError("No land mask tiles could be downloaded")
        
        # Create temporary directory for reprojected tiles
        temp_dir = tempfile.mkdtemp(prefix="geotessera_merge_")
        
        try:
            # Reproject all tiles to target CRS if needed
            reprojected_paths = []
            
            for i, tile_path in enumerate(tile_paths):
                with rasterio.open(tile_path) as src:
                    if str(src.crs) != target_crs:
                        # Reproject to target CRS
                        reprojected_path = Path(temp_dir) / f"reprojected_{i}.tiff"
                        
                        # Calculate transform and dimensions for reprojection
                        transform, width, height = calculate_default_transform(
                            src.crs, target_crs, src.width, src.height, *src.bounds
                        )
                        
                        # Create reprojected raster
                        with rasterio.open(
                            reprojected_path,
                            'w',
                            driver='GTiff',
                            height=height,
                            width=width,
                            count=src.count,
                            dtype=src.dtypes[0],
                            crs=target_crs,
                            transform=transform,
                            compress='lzw'
                        ) as dst:
                            for band_idx in range(1, src.count + 1):
                                reproject(
                                    source=rasterio.band(src, band_idx),
                                    destination=rasterio.band(dst, band_idx),
                                    src_transform=src.transform,
                                    src_crs=src.crs,
                                    dst_transform=transform,
                                    dst_crs=target_crs,
                                    resampling=Resampling.nearest
                                )
                        
                        reprojected_paths.append(str(reprojected_path))
                    else:
                        reprojected_paths.append(tile_path)
            
            # Merge all reprojected tiles
            with rasterio.open(reprojected_paths[0]) as src:
                merged_array, merged_transform = merge([
                    rasterio.open(path) for path in reprojected_paths
                ])
                
                # Check if this appears to be a land/water mask (binary values)
                is_binary_mask = (merged_array.min() >= 0 and merged_array.max() <= 1 and 
                                 merged_array.dtype in ['uint8', 'int8'])
                
                if is_binary_mask:
                    print("Detected binary land/water mask - converting to visible format")
                    # Convert binary mask to visible grayscale (0->0, 1->255)
                    display_array = (merged_array * 255).astype('uint8')
                else:
                    display_array = merged_array
                
                # Write merged result
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=display_array.shape[1],
                    width=display_array.shape[2],
                    count=display_array.shape[0],
                    dtype=display_array.dtype,
                    crs=target_crs,
                    transform=merged_transform,
                    compress='lzw'
                ) as dst:
                    dst.write(display_array)
                
            print(f"Merged land mask saved to: {output_path}")
            return output_path
            
        finally:
            # Clean up temporary files
            shutil.rmtree(temp_dir)
    
    def merge_embeddings_for_region(self, bounds: Tuple[float, float, float, float], 
                                   output_path: str, target_crs: str = "EPSG:4326",
                                   bands: List[int] = [0, 1, 2], normalize: bool = True,
                                   year: int = 2024) -> str:
        """Create a seamless mosaic of Tessera embeddings for a geographic region.
        
        Merges multiple embedding tiles into a single georeferenced GeoTIFF,
        handling coordinate system differences and ensuring perfect alignment.
        This method uses land mask files to obtain optimal projection metadata
        for each tile, preventing coordinate skew when tiles span different
        UTM zones.
        
        The process:
        1. Identifies all tiles intersecting the bounding box
        2. Downloads embeddings and corresponding land masks
        3. Creates georeferenced temporary files using land mask CRS metadata
        4. Reprojects tiles to common coordinate system if needed
        5. Merges all tiles into seamless mosaic
        6. Applies normalization across entire mosaic if requested
        
        Args:
            bounds: Region bounds as (min_lon, min_lat, max_lon, max_lat) in
                    decimal degrees. Example: (-0.2, 51.4, 0.1, 51.6) for London.
            output_path: Filename for the output GeoTIFF mosaic.
            target_crs: Coordinate system for output. Default "EPSG:4326" (WGS84).
                       Use local projections (e.g., UTM) for accurate area measurements.
            bands: Three channel indices to visualize as RGB. Must be in range
                   0-127. Different combinations highlight different features.
            normalize: If True, applies global normalization across all merged
                      tiles for consistent visualization. If False, preserves
                      original embedding values.
            year: Year of embeddings to merge (2017-2024).
            
        Returns:
            Path to the created mosaic GeoTIFF file.
            
        Raises:
            ImportError: If rasterio is not installed.
            ValueError: If no tiles found for region or invalid parameters.
            RuntimeError: If land masks are not available for alignment.
            
        Example:
            >>> gt = GeoTessera()
            >>> # Create mosaic of San Francisco Bay Area
            >>> bounds = (-122.6, 37.2, -121.7, 38.0)
            >>> gt.merge_embeddings_for_region(
            ...     bounds=bounds,
            ...     output_path="sf_bay_tessera.tiff",
            ...     bands=[30, 60, 90],  # False color visualization
            ...     normalize=True
            ... )
            
        Note:
            Large regions require significant memory and processing time.
            The output file includes full georeferencing metadata and can
            be used in any GIS software. Normalization is applied globally
            across all tiles to ensure consistent coloring.
        """
        try:
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject
            from rasterio.enums import Resampling
            from rasterio.merge import merge
            import tempfile
            import shutil
        except ImportError:
            raise ImportError("Please install rasterio for embedding merging: pip install rasterio")
        
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Find all embedding tiles that intersect with the bounds
        tiles_to_merge = []
        for emb_year, lat, lon in self.list_available_embeddings():
            if emb_year != year:
                continue
                
            # Check if tile intersects with bounds (0.1 degree grid)
            tile_min_lon, tile_min_lat = lon, lat
            tile_max_lon, tile_max_lat = lon + 0.1, lat + 0.1
            
            if (tile_min_lon < max_lon and tile_max_lon > min_lon and
                tile_min_lat < max_lat and tile_max_lat > min_lat):
                tiles_to_merge.append((lat, lon))
        
        if not tiles_to_merge:
            raise ValueError(f"No embedding tiles found for the specified region in year {year}")
        
        print(f"Found {len(tiles_to_merge)} embedding tiles to merge for year {year}")
        
        # Create temporary directory for georeferenced TIFF files
        temp_dir = tempfile.mkdtemp(prefix="geotessera_embed_merge_")
        
        try:
            # Step 1: Create properly georeferenced temporary TIFF files
            temp_tiff_paths = []
            
            for lat, lon in tiles_to_merge:
                try:
                    # Get the numpy embedding
                    embedding = self.fetch_embedding(lat, lon, year, progressbar=True)
                    
                    # Get the corresponding landmask GeoTIFF for coordinate information
                    # The landmask TIFF provides the optimal projection metadata for this tile
                    landmask_path = self._fetch_landmask(lat, lon, progressbar=False)
                    
                    # Read coordinate information from the landmask GeoTIFF metadata
                    with rasterio.open(landmask_path) as landmask_src:
                        src_transform = landmask_src.transform
                        src_crs = landmask_src.crs
                        src_bounds = landmask_src.bounds
                        src_height, src_width = landmask_src.height, landmask_src.width
                    
                    # Extract the specified bands
                    if len(bands) == 3:
                        vis_data = embedding[:, :, bands].copy()
                    else:
                        raise ValueError("Exactly 3 bands must be specified for RGB visualization")
                    
                    # Keep data as float32 for now - normalization happens after merging
                    vis_data = vis_data.astype(np.float32)
                    
                    # Create temporary georeferenced TIFF file
                    temp_tiff_path = Path(temp_dir) / f"embed_{lat:.2f}_{lon:.2f}.tiff"
                    
                    # Handle potential coordinate system differences and reprojection
                    if str(src_crs) != str(target_crs):
                        # Calculate transform for reprojection
                        dst_transform, dst_width, dst_height = calculate_default_transform(
                            src_crs, target_crs, src_width, src_height,
                            left=src_bounds.left, bottom=src_bounds.bottom,
                            right=src_bounds.right, top=src_bounds.top
                        )
                        
                        # Create reprojected array
                        dst_data = np.zeros((dst_height, dst_width, 3), dtype=np.float32)
                        
                        # Reproject each band
                        for i in range(3):
                            reproject(
                                source=vis_data[:, :, i],
                                destination=dst_data[:, :, i],
                                src_transform=src_transform,
                                src_crs=src_crs,
                                dst_transform=dst_transform,
                                dst_crs=target_crs,
                                resampling=Resampling.bilinear  # Use bilinear for smoother results
                            )
                        
                        # Use reprojected data
                        final_data = dst_data
                        final_transform = dst_transform
                        final_crs = target_crs
                        final_height, final_width = dst_height, dst_width
                    else:
                        # Use original coordinate system
                        final_data = vis_data
                        final_transform = src_transform
                        final_crs = src_crs
                        final_height, final_width = vis_data.shape[:2]
                    
                    # Write georeferenced TIFF file (as float32 for now)
                    with rasterio.open(
                        temp_tiff_path,
                        'w',
                        driver='GTiff',
                        height=final_height,
                        width=final_width,
                        count=3,
                        dtype='float32',
                        crs=final_crs,
                        transform=final_transform,
                        compress='lzw',
                        tiled=True,
                        blockxsize=256,
                        blockysize=256
                    ) as dst:
                        for i in range(3):
                            dst.write(final_data[:, :, i], i + 1)
                    
                    temp_tiff_paths.append(str(temp_tiff_path))
                    
                except Exception as e:
                    print(f"Warning: Could not process embedding tile ({lat}, {lon}): {e}")
                    continue
            
            if not temp_tiff_paths:
                raise ValueError("No embedding tiles could be processed")
            
            print(f"Created {len(temp_tiff_paths)} temporary georeferenced TIFF files")
            
            # Step 2: Use rasterio.merge to properly merge the georeferenced TIFF files
            print("Merging georeferenced TIFF files...")
            
            # Open all TIFF files for merging
            src_files = [rasterio.open(path) for path in temp_tiff_paths]
            
            try:
                # Merge the files
                merged_array, merged_transform = merge(src_files, method='first')
                
                # Apply global normalization after merging if requested
                if normalize:
                    print("Applying global normalization across all merged tiles...")
                    for band_idx in range(merged_array.shape[0]):  # For each band
                        band_data = merged_array[band_idx]
                        
                        # Only normalize non-zero pixels to preserve background
                        mask = band_data != 0
                        if np.any(mask):
                            # Get global min/max for this band across all tiles
                            min_val = np.min(band_data[mask])
                            max_val = np.max(band_data[mask])
                            
                            if max_val > min_val:
                                # Apply normalization only to non-zero pixels
                                normalized = (band_data[mask] - min_val) / (max_val - min_val)
                                band_data[mask] = normalized
                
                # Convert to uint8 for final output
                # Clip to [0,1] range first, then scale to [0,255]
                merged_array = np.clip(merged_array, 0, 1)
                merged_array_uint8 = (merged_array * 255).astype(np.uint8)
                
                # Write the merged result
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=merged_array_uint8.shape[1],
                    width=merged_array_uint8.shape[2],
                    count=merged_array_uint8.shape[0],
                    dtype='uint8',
                    crs=target_crs,
                    transform=merged_transform,
                    compress='lzw'
                ) as dst:
                    dst.write(merged_array_uint8)
                
                print(f"Merged embedding visualization saved to: {output_path}")
                print(f"Dimensions: {merged_array_uint8.shape[2]}x{merged_array_uint8.shape[1]} pixels")
                
                return output_path
                
            finally:
                # Close all source files
                for src in src_files:
                    src.close()
            
        finally:
            # Clean up temporary files
            shutil.rmtree(temp_dir)
