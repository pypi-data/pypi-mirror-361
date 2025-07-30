"""
STAC Item Collections module - Enhanced with fixed pattern matching
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

class STACItemCollection:
    """
    Enhanced STAC Item Collection with fixed pattern matching and comprehensive functionality.
    """
    
    def __init__(self, items: List[Dict], provider: str = "unknown"):
        """
        Initialize STAC Item Collection.
        
        Args:
            items: List of STAC item dictionaries
            provider: Provider name (e.g., "planetary_computer", "earthsearch")
        """
        self._items = items
        self.provider = provider
        self._cached_dataframe = None
    
    def __len__(self):
        """Return number of items in collection."""
        return len(self._items)
    
    def __getitem__(self, index):
        """Get item by index."""
        return self._items[index]
    
    def __iter__(self):
        """Iterate over items."""
        return iter(self._items)
    
    @property
    def items(self):
        """Get all items as list."""
        return self._items
    
    def get_assets_by_pattern(self, pattern: str, match_type: str = "extension") -> List[str]:
        """
        🔧 FIXED: Get asset names that match the specified pattern.
        
        Args:
            pattern: Pattern to search for (e.g., ".xml", ".jp2", ".tif")
            match_type: Type of matching to perform:
                - "extension": Match actual file extensions from URLs (default)
                - "mime": Match MIME types
                - "name": Match asset names (original behavior)
                - "url": Match full URLs
                
        Returns:
            List of asset names that match the pattern
        """
        matching_assets = []
        
        for item in self._items:
            assets = item.get('assets', {})
            
            for asset_key, asset_data in assets.items():
                if self._asset_matches_pattern(asset_key, asset_data, pattern, match_type):
                    if asset_key not in matching_assets:
                        matching_assets.append(asset_key)
        
        return matching_assets
    
    def _asset_matches_pattern(self, asset_key: str, asset_data: Dict, 
                              pattern: str, match_type: str) -> bool:
        """
        🔧 FIXED: Check if an asset matches the specified pattern.
        
        Args:
            asset_key: Asset name/key
            asset_data: Asset metadata dictionary
            pattern: Pattern to match
            match_type: Type of matching to perform
            
        Returns:
            True if asset matches the pattern
        """
        pattern_lower = pattern.lower()
        
        if match_type == "extension":
            # Check actual file extension from URL
            return self._check_extension_match(asset_data, pattern_lower)
        
        elif match_type == "mime":
            # Check MIME type
            return self._check_mime_match(asset_data, pattern_lower)
        
        elif match_type == "name":
            # Check asset name (original behavior)
            return pattern_lower in asset_key.lower()
        
        elif match_type == "url":
            # Check full URL
            asset_url = asset_data.get('href', '')
            return pattern_lower in asset_url.lower()
        
        else:
            # Default to extension matching
            return self._check_extension_match(asset_data, pattern_lower)
    
    def _check_extension_match(self, asset_data: Dict, pattern: str) -> bool:
        """
        🔧 FIXED: Check if asset's actual file extension matches pattern.
        
        Args:
            asset_data: Asset metadata dictionary
            pattern: Pattern to match (e.g., ".xml", ".jp2")
            
        Returns:
            True if extension matches
        """
        asset_url = asset_data.get('href', '')
        if not asset_url:
            return False
        
        try:
            # Parse URL to get the path
            parsed_url = urlparse(asset_url)
            url_path = parsed_url.path
            
            # Extract file extension
            file_extension = Path(url_path).suffix.lower()
            
            # Remove leading dot from pattern if present for comparison
            pattern_clean = pattern.lstrip('.')
            extension_clean = file_extension.lstrip('.')
            
            return extension_clean == pattern_clean or pattern in file_extension
            
        except Exception:
            return False
    
    def _check_mime_match(self, asset_data: Dict, pattern: str) -> bool:
        """
        🔧 FIXED: Check if asset's MIME type matches pattern.
        
        Args:
            asset_data: Asset metadata dictionary
            pattern: Pattern to match (e.g., "image/tiff", "application/xml")
            
        Returns:
            True if MIME type matches
        """
        asset_type = asset_data.get('type', '').lower()
        return pattern in asset_type
    
    def _get_complete_items(self) -> List[Dict]:
        """
        🔧 FIXED: Get complete items using fallback strategy if available.
        
        Returns:
            List of complete items (with fallback if possible)
        """
        # Try to access the parent search object to get complete items
        if hasattr(self, '_parent_search') and self._parent_search:
            try:
                # Get all items from the parent search object
                complete_collection = self._parent_search.get_all_items()
                return complete_collection._items
            except Exception:
                pass
        
        # Fallback to current items if no parent search available
        return self._items

    def _calculate_comprehensive_stats(self, items: List[Dict]) -> Dict[str, Any]:
        """
        🔧 FIXED: Calculate comprehensive statistics from complete items.
        
        Args:
            items: List of items to analyze
            
        Returns:
            Dictionary with comprehensive statistics
        """
        # Collect all assets across all items
        all_assets = set()
        asset_counts = {}
        collections = set()
        dates = []
        cloud_covers = []
        
        for item in items:
            # Collections
            collection = item.get('collection', '')
            if collection:
                collections.add(collection)
            
            # Assets
            assets = item.get('assets', {})
            for asset_key in assets.keys():
                all_assets.add(asset_key)
                asset_counts[asset_key] = asset_counts.get(asset_key, 0) + 1
            
            # Dates
            properties = item.get('properties', {})
            datetime_str = properties.get('datetime', '')
            if datetime_str:
                try:
                    if PANDAS_AVAILABLE:
                        dates.append(pd.to_datetime(datetime_str))
                    else:
                        dates.append(datetime_str)
                except:
                    pass
            
            # Cloud cover
            cloud_cover = properties.get('eo:cloud_cover')
            if cloud_cover is not None:
                cloud_covers.append(cloud_cover)
        
        # Calculate date range
        if dates and PANDAS_AVAILABLE:
            date_range = {
                'start': min(dates).strftime('%Y-%m-%d'),
                'end': max(dates).strftime('%Y-%m-%d')
            }
        elif dates:
            date_range = {'start': min(dates), 'end': max(dates)}
        else:
            date_range = {'start': 'unknown', 'end': 'unknown'}
        
        # Find common assets (present in most items)
        total_items = len(items)
        common_threshold = total_items * 0.8  # Assets present in 80% of items
        common_assets = [asset for asset, count in asset_counts.items() if count >= common_threshold]
        
        # Cloud cover statistics
        cloud_stats = None
        if cloud_covers:
            cloud_stats = {
                'min': min(cloud_covers),
                'max': max(cloud_covers),
                'mean': sum(cloud_covers) / len(cloud_covers),
                'count': len(cloud_covers)
            }
        
        # Extension and MIME type analysis
        extensions = self._analyze_extensions(items)
        mime_types = self._analyze_mime_types(items)
        
        return {
            'provider': self.provider,
            'total_items': total_items,
            'unique_collections': list(collections),
            'date_range': date_range,
            'all_assets': sorted(list(all_assets)),
            'common_assets': sorted(common_assets),
            'available_extensions': extensions,
            'available_mime_types': mime_types,
            'cloud_cover': cloud_stats
        }

    def _analyze_extensions(self, items: List[Dict]) -> Dict[str, List[str]]:
        """Analyze file extensions from complete items."""
        extensions_map = {}
        
        for item in items:
            assets = item.get('assets', {})
            for asset_key, asset_data in assets.items():
                asset_url = asset_data.get('href', '')
                if asset_url:
                    try:
                        parsed_url = urlparse(asset_url)
                        file_extension = Path(parsed_url.path).suffix.lower()
                        
                        if file_extension:
                            if file_extension not in extensions_map:
                                extensions_map[file_extension] = []
                            if asset_key not in extensions_map[file_extension]:
                                extensions_map[file_extension].append(asset_key)
                    except Exception:
                        continue
        
        return extensions_map

    def _analyze_mime_types(self, items: List[Dict]) -> Dict[str, List[str]]:
        """Analyze MIME types from complete items."""
        mime_types_map = {}
        
        for item in items:
            assets = item.get('assets', {})
            for asset_key, asset_data in assets.items():
                mime_type = asset_data.get('type', '')
                if mime_type:
                    if mime_type not in mime_types_map:
                        mime_types_map[mime_type] = []
                    if asset_key not in mime_types_map[mime_type]:
                        mime_types_map[mime_type].append(asset_key)
        
        return mime_types_map


    def get_assets_by_extension(self, extension: str) -> List[str]:
        """
        🆕 NEW: Convenience method to get assets by file extension.
        
        Args:
            extension: File extension (e.g., "xml", "jp2", "tif")
            
        Returns:
            List of asset names with the specified extension
        """
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = '.' + extension
        
        return self.get_assets_by_pattern(extension, match_type="extension")
    
    def get_assets_by_mime_type(self, mime_type: str) -> List[str]:
        """
        🆕 NEW: Convenience method to get assets by MIME type.
        
        Args:
            mime_type: MIME type (e.g., "image/tiff", "application/xml")
            
        Returns:
            List of asset names with the specified MIME type
        """
        return self.get_assets_by_pattern(mime_type, match_type="mime")
    
    def list_asset_extensions(self) -> Dict[str, List[str]]:
        """
        🆕 NEW: List all unique file extensions and which assets have them.
        
        Returns:
            Dictionary mapping extensions to asset names
        """
        extensions_map = {}
        
        for item in self._items:
            assets = item.get('assets', {})
            
            for asset_key, asset_data in assets.items():
                asset_url = asset_data.get('href', '')
                if asset_url:
                    try:
                        parsed_url = urlparse(asset_url)
                        file_extension = Path(parsed_url.path).suffix.lower()
                        
                        if file_extension:
                            if file_extension not in extensions_map:
                                extensions_map[file_extension] = []
                            if asset_key not in extensions_map[file_extension]:
                                extensions_map[file_extension].append(asset_key)
                    except Exception:
                        continue
        
        return extensions_map
    
    def list_asset_mime_types(self) -> Dict[str, List[str]]:
        """
        🆕 NEW: List all unique MIME types and which assets have them.
        
        Returns:
            Dictionary mapping MIME types to asset names
        """
        mime_types_map = {}
        
        for item in self._items:
            assets = item.get('assets', {})
            
            for asset_key, asset_data in assets.items():
                mime_type = asset_data.get('type', '')
                if mime_type:
                    if mime_type not in mime_types_map:
                        mime_types_map[mime_type] = []
                    if asset_key not in mime_types_map[mime_type]:
                        mime_types_map[mime_type].append(asset_key)
        
        return mime_types_map
    
    def debug_asset_info(self, pattern: str = None) -> Dict[str, Any]:
        """
        🆕 NEW: Debug information about assets and pattern matching.
        
        Args:
            pattern: Optional pattern to test matching for
            
        Returns:
            Debug information dictionary
        """
        debug_info = {
            'total_items': len(self._items),
            'extensions': self.list_asset_extensions(),
            'mime_types': self.list_asset_mime_types(),
        }
        
        if pattern:
            debug_info['pattern_results'] = {
                'pattern': pattern,
                'extension_match': self.get_assets_by_pattern(pattern, "extension"),
                'mime_match': self.get_assets_by_pattern(pattern, "mime"),
                'name_match': self.get_assets_by_pattern(pattern, "name"),
                'url_match': self.get_assets_by_pattern(pattern, "url")
            }
        
        return debug_info
    
    def get_all_urls(self, asset_keys: Optional[List[str]] = None, 
                    signed: Optional[bool] = None) -> Dict[str, Dict[str, str]]:
        """
        Get URLs from all items in the collection.
        
        Args:
            asset_keys: Specific assets to get URLs for (optional)
            signed: Override signing behavior (optional)
            
        Returns:
            Dictionary of {item_id: {asset_key: url}}
        """
        all_urls = {}
        
        for item in self._items:
            from .items import STACItem
            stac_item = STACItem(item, provider=self.provider)
            item_id = item.get('id', f'item_{len(all_urls)}')
            
            if asset_keys:
                # Get specific assets
                item_urls = {}
                for asset_key in asset_keys:
                    if stac_item.has_asset(asset_key):
                        item_urls[asset_key] = stac_item.get_asset_url(asset_key, signed=signed)
                all_urls[item_id] = item_urls
            else:
                # Get all assets
                all_urls[item_id] = stac_item.get_all_asset_urls(signed=signed)
        
        return all_urls
    
    def to_dataframe(self, include_geometry: bool = True) -> 'pd.DataFrame':
        """
        Convert collection to pandas/geopandas DataFrame.
        
        Args:
            include_geometry: Include spatial geometry (requires geopandas)
            
        Returns:
            DataFrame with item metadata
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for to_dataframe(). Install with: pip install pandas")
        
        # Use cached dataframe if available
        if self._cached_dataframe is not None:
            return self._cached_dataframe
        
        # Build DataFrame from items
        df_data = []
        for item in self._items:
            # Flatten item properties
            row = {
                'id': item.get('id', ''),
                'collection': item.get('collection', ''),
                'datetime': item.get('properties', {}).get('datetime', ''),
                'provider': self.provider
            }
            
            # Add all properties
            properties = item.get('properties', {})
            for key, value in properties.items():
                if key not in row:  # Avoid duplicates
                    row[key] = value
            
            # Add geometry info
            geometry = item.get('geometry', {})
            if geometry:
                row['geometry_type'] = geometry.get('type', '')
                
            # Add bbox if available
            bbox = item.get('bbox', [])
            if bbox and len(bbox) >= 4:
                row['bbox_west'] = bbox[0]
                row['bbox_south'] = bbox[1]
                row['bbox_east'] = bbox[2]
                row['bbox_north'] = bbox[3]
            
            # Add asset count
            assets = item.get('assets', {})
            row['asset_count'] = len(assets)
            
            df_data.append(row)
        
        # Create DataFrame
        if include_geometry and GEOPANDAS_AVAILABLE:
            try:
                import geopandas as gpd
                from shapely.geometry import shape
                
                # Convert to GeoDataFrame with geometry
                geometries = []
                for item in self._items:
                    geom = item.get('geometry')
                    if geom:
                        geometries.append(shape(geom))
                    else:
                        geometries.append(None)
                
                df = gpd.GeoDataFrame(df_data, geometry=geometries)
            except Exception:
                # Fallback to regular DataFrame
                df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame(df_data)
        
        # Cache for future use
        self._cached_dataframe = df
        
        return df
    
    def export_urls_json(self, filename: str, asset_keys: Optional[List[str]] = None, 
    signed: Optional[bool] = None, use_fallback: bool = True):
        """
        🔧 FIXED: Export all URLs to JSON file for external processing.
        
        Args:
            filename: Output JSON filename
            asset_keys: Specific assets to export (optional)
            signed: Whether to sign URLs (optional, auto-detected by provider)
            use_fallback: Whether to use complete collection from fallback (default: True)
        """
        # 🔧 FIXED: Get complete items using fallback strategy
        if use_fallback:
            # Try to get complete items from parent search object if available
            items_to_process = self._get_complete_items()
        else:
            # Use only the items currently in the collection
            items_to_process = self._items
        
        # Process URLs from all items
        all_urls = {}
        processed_count = 0
        
        for item in items_to_process:
            from .items import STACItem
            stac_item = STACItem(item, provider=self.provider)
            item_id = item.get('id', f'item_{processed_count}')
            
            try:
                if asset_keys:
                    # Get specific assets
                    item_urls = {}
                    for asset_key in asset_keys:
                        if stac_item.has_asset(asset_key):
                            item_urls[asset_key] = stac_item.get_asset_url(asset_key, signed=signed)
                    all_urls[item_id] = item_urls
                else:
                    # Get all assets
                    all_urls[item_id] = stac_item.get_all_asset_urls(signed=signed)
                
                processed_count += 1
                
            except Exception as e:
                print(f"⚠️ Error processing item {item_id}: {e}")
                continue
        
        # 🔧 FIXED: Enhanced export data with complete information
        export_data = {
            'provider': self.provider,
            'total_items': len(items_to_process),
            'processed_items': processed_count,
            'exported_at': pd.Timestamp.now().isoformat() if PANDAS_AVAILABLE else 'unknown',
            'asset_keys': asset_keys or 'all',
            'signed_urls': signed,
            'fallback_used': use_fallback and len(items_to_process) > len(self._items),
            'original_count': len(self._items),
            'urls': all_urls
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {processed_count} items to {filename}")
        if use_fallback and len(items_to_process) > len(self._items):
            print(f"🔄 Used fallback strategy: {len(self._items)} → {len(items_to_process)} items")
        print(f"💡 Load with: import json; data = json.load(open('{filename}'))")

    
    def filter_by_cloud_cover(self, max_cloud_cover: float) -> 'STACItemCollection':
        """
        Filter items by cloud cover percentage.
        
        Args:
            max_cloud_cover: Maximum cloud cover percentage (0-100)
            
        Returns:
            New STACItemCollection with filtered items
        """
        filtered_items = []
        
        for item in self._items:
            cloud_cover = item.get('properties', {}).get('eo:cloud_cover', 0)
            if cloud_cover <= max_cloud_cover:
                filtered_items.append(item)
        
        return STACItemCollection(filtered_items, provider=self.provider)
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> 'STACItemCollection':
        """
        Filter items by date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            New STACItemCollection with filtered items
        """
        if not PANDAS_AVAILABLE:
            print("⚠️ pandas required for date filtering. Install with: pip install pandas")
            return self
        
        filtered_items = []
        
        for item in self._items:
            item_datetime = item.get('properties', {}).get('datetime', '')
            if item_datetime:
                try:
                    item_date = pd.to_datetime(item_datetime).date()
                    start = pd.to_datetime(start_date).date()
                    end = pd.to_datetime(end_date).date()
                    
                    if start <= item_date <= end:
                        filtered_items.append(item)
                except Exception:
                    continue
        
        return STACItemCollection(filtered_items, provider=self.provider)
    
    def get_unique_collections(self) -> List[str]:
        """
        Get list of unique collection names in this collection.
        
        Returns:
            List of unique collection names
        """
        collections = set()
        for item in self._items:
            collection = item.get('collection', '')
            if collection:
                collections.add(collection)
        return list(collections)
    
    def get_date_range(self) -> Dict[str, str]:
        """
        Get date range of items in collection.
        
        Returns:
            Dictionary with 'start' and 'end' dates
        """
        if not PANDAS_AVAILABLE:
            return {'start': 'unknown', 'end': 'unknown'}
        
        dates = []
        for item in self._items:
            item_datetime = item.get('properties', {}).get('datetime', '')
            if item_datetime:
                try:
                    dates.append(pd.to_datetime(item_datetime))
                except Exception:
                    continue
        
        if dates:
            return {
                'start': min(dates).strftime('%Y-%m-%d'),
                'end': max(dates).strftime('%Y-%m-%d')
            }
        
        return {'start': 'unknown', 'end': 'unknown'}
    
    def get_details(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'total_items': len(self._items),
            'provider': self.provider,
            'unique_collections': self.get_unique_collections(),
            'date_range': self.get_date_range(),
            'available_extensions': self.list_asset_extensions(),
            'available_mime_types': self.list_asset_mime_types()
        }
        
        # Cloud cover statistics
        if PANDAS_AVAILABLE:
            cloud_covers = []
            for item in self._items:
                cloud_cover = item.get('properties', {}).get('eo:cloud_cover')
                if cloud_cover is not None:
                    cloud_covers.append(cloud_cover)
            
            if cloud_covers:
                stats['cloud_cover'] = {
                    'min': min(cloud_covers),
                    'max': max(cloud_covers),
                    'mean': sum(cloud_covers) / len(cloud_covers),
                    'count': len(cloud_covers)
                }
        
        return stats
    
    def print_collection_summary(self, use_fallback: bool = True):
        """
        🔧 FIXED: Print a comprehensive summary of the complete collection.
        
        Args:
            use_fallback: Whether to use complete collection from fallback (default: True)
        """
        # 🔧 FIXED: Get complete items using fallback strategy
        if use_fallback:
            items_to_analyze = self._get_complete_items()
        else:
            items_to_analyze = self._items
        
        # Calculate statistics from complete items
        stats = self._calculate_comprehensive_stats(items_to_analyze)
        
        print(f"📦 STAC Collection Summary")
        print(f"=" * 50)
        print(f"🔗 Provider: {stats['provider']}")
        print(f"📊 Total Items: {stats['total_items']}")
        
        if use_fallback and stats['total_items'] > len(self._items):
            print(f"🔄 Fallback Used: {len(self._items)} → {stats['total_items']} items")
        
        print(f"📁 Collections: {stats['unique_collections']}")
        print(f"📅 Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
        
        # Cloud cover statistics
        if 'cloud_cover' in stats and stats['cloud_cover']:
            cc = stats['cloud_cover']
            print(f"☁️ Cloud Cover: {cc['min']:.1f}% - {cc['max']:.1f}% (avg: {cc['mean']:.1f}%)")
        
        # Asset information
        extensions = stats['available_extensions']
        mime_types = stats['available_mime_types']
        
        print(f"🎯 Available Assets ({len(stats['all_assets'])}): {stats['all_assets'][:10]}{'...' if len(stats['all_assets']) > 10 else ''}")
        print(f"🔗 Common Assets: {stats['common_assets']}")
        
        # Extension breakdown
        print(f"\n📋 File Extensions:")
        for ext, assets in list(extensions.items())[:5]:  # Show top 5
            print(f"  {ext}: {len(assets)} assets")
        
        # Usage examples
        print(f"\n💡 Usage Examples:")
        print(f"  # Export all URLs: collection.export_urls_json('urls.json')")
        print(f"  # Get specific assets: collection.get_assets_by_extension('tif')")
        print(f"  # Filter by cloud cover: collection.filter_by_cloud_cover(20)")
        print(f"  # Convert to DataFrame: df = collection.to_dataframe()")

    
    def __repr__(self):
        """String representation of the collection."""
        return f"STACItemCollection({len(self._items)} items, provider='{self.provider}')"
    
    def __str__(self):
        """Human-readable string representation."""
        stats = self.get_details()
        return f"STACItemCollection: {len(self._items)} items from {self.provider} ({stats['date_range']['start']} to {stats['date_range']['end']})"
