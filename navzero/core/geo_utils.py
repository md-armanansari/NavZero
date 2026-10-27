"""
Geo-transformation utilities for NavZero.
Maps pixel coordinates (x, y) on the satellite map to real-world Latitude & Longitude.
"""

class GeoReference:
    def __init__(self, top_left_lat=34.2500, top_left_lon=77.5000, 
                 bottom_right_lat=34.1000, bottom_right_lon=77.7000,
                 map_width=2000, map_height=2000):
        """
        Default coordinates set around Leh / Eastern Ladakh tactical sector.
        """
        self.top_left_lat = top_left_lat
        self.top_left_lon = top_left_lon
        self.bottom_right_lat = bottom_right_lat
        self.bottom_right_lon = bottom_right_lon
        self.map_width = map_width
        self.map_height = map_height
        
        self.lat_span = bottom_right_lat - top_left_lat # usually negative as south is lower
        self.lon_span = bottom_right_lon - top_left_lon

    def pixel_to_latlon(self, px, py):
        """Converts pixel coordinate (x, y) to (latitude, longitude)"""
        lon = self.top_left_lon + (px / self.map_width) * self.lon_span
        lat = self.top_left_lat + (py / self.map_height) * self.lat_span
        return lat, lon

    def latlon_to_pixel(self, lat, lon):
        """Converts (latitude, longitude) to pixel coordinate (x, y)"""
        px = int(((lon - self.top_left_lon) / self.lon_span) * self.map_width)
        py = int(((lat - self.top_left_lat) / self.lat_span) * self.map_height)
        return px, py
