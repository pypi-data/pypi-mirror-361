"""
Public API for altitude analysis package
"""
import ctypes
import json
import os
import platform
import glob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AltitudeAnalyzer:
    def __init__(self, fid, minutes=3, altitude=10000,
                 noise_method='simple', dbscan_eps=0.51,
                 max_gap_minutes=10,
                 jump_threshold=5000, window_size=30,  # Simple filter params
                 min_samples_range_start=18, min_samples_range_end=180,  # DBSCAN params
                 min_samples_step=18,
                 min_flight_duration=3,  # in minutes
                 min_level_points=10,
                 altitude_tolerance=50.0, # Altitude tolerance for level flight (feet)
                 timeout=30, max_retries=2):

        self.fid = fid
        self.minutes = minutes
        self.altitude = altitude
        self.noise_method = noise_method
        self.dbscan_eps = dbscan_eps
        self.max_gap_minutes = max_gap_minutes
        self.jump_threshold = jump_threshold
        self.window_size = window_size
        self.min_samples_range_start = min_samples_range_start
        self.min_samples_range_end = min_samples_range_end
        self.min_samples_step = min_samples_step
        self.min_flight_duration = min_flight_duration
        self.min_level_points = min_level_points
        self.altitude_tolerance = altitude_tolerance
        self.timeout = timeout
        self.max_retries = max_retries

        # Load compiled core
        self._core = self._load_core()
        logger.info(f"Core engine loaded for FID: {fid}")

    def _load_core(self):
        """Load the compiled core library"""
        # Determine platform-specific file extension
        ext = '.dll' if platform.system() == 'Windows' else '.so'

        # Get the path to the compiled library
        lib_dir = os.path.dirname(__file__)
        full_pattern = os.path.join(lib_dir, f"*core*{ext}")
        lib_paths = glob.glob(full_pattern)

        if not lib_paths:
            raise RuntimeError(f"Core engine not found. Pattern: {full_pattern}")

        lib_path = lib_paths[0]
        logger.info(f"Loading core library: {lib_path}")

        if not os.path.exists(lib_path):
            raise RuntimeError(f"Core engine not found at: {lib_path}")

        # Define argtypes and restype for analyze_altitude_api
        self._core.analyze_altitude_api.argtypes = [
            ctypes.c_int,  # fid
            ctypes.c_int,  # minutes
            ctypes.c_int,  # altitude
            ctypes.c_char_p, # noise_method
            ctypes.c_double, # dbscan_eps
            ctypes.c_int,  # max_gap_seconds
            ctypes.c_int,  # jump_threshold
            ctypes.c_int,  # window_size
            ctypes.c_int,  # min_samples_range_start
            ctypes.c_int,  # min_samples_range_end
            ctypes.c_int,  # min_samples_step
            ctypes.c_int,  # min_flight_duration
            ctypes.c_int,  # min_level_points
            ctypes.c_double, # altitude_tolerance
            ctypes.c_char_p, # output buffer
            ctypes.c_int   # output buffer size
        ]
        self._core.analyze_altitude_api.restype = None # Returns void, output via buffer

        return ctypes.CDLL(lib_path)

    def analyze(self):
        """Execute analysis with detailed diagnostics"""
        # Prepare inputs
        fid = ctypes.c_int(self.fid)
        minutes = ctypes.c_int(self.minutes)
        altitude = ctypes.c_int(self.altitude)
        noise_method = ctypes.c_char_p(self.noise_method.encode('utf-8')) # Encode to bytes
        dbscan_eps = ctypes.c_double(self.dbscan_eps)
        max_gap_seconds = ctypes.c_int(self.max_gap_minutes * 60)  # Convert to seconds
        jump_threshold = ctypes.c_int(self.jump_threshold)
        window_size = ctypes.c_int(self.window_size)
        min_samples_range_start = ctypes.c_int(self.min_samples_range_start)
        min_samples_range_end = ctypes.c_int(self.min_samples_range_end)
        min_samples_step = ctypes.c_int(self.min_samples_step)
        min_flight_duration_seconds = ctypes.c_int(self.min_flight_duration * 60) # Convert to seconds
        min_level_points = ctypes.c_int(self.min_level_points)
        altitude_tolerance = ctypes.c_double(self.altitude_tolerance)

        # Prepare output buffer - increased to 2MB
        buffer_size = 2 * 1024 * 1024  # 2MB buffer
        result_buffer = ctypes.create_string_buffer(buffer_size)

        # Call core function
        logger.info(f"Starting analysis for FID: {self.fid}")
        logger.debug(f"Parameters: minutes={self.minutes}, altitude={self.altitude}, "
                     f"noise_method={self.noise_method}, dbscan_eps={self.dbscan_eps}, "
                     f"max_gap_minutes={self.max_gap_minutes}, jump_threshold={self.jump_threshold}, "
                     f"window_size={self.window_size}, min_samples_range_start={self.min_samples_range_start}, "
                     f"min_samples_range_end={self.min_samples_range_end}, min_samples_step={self.min_samples_step}, "
                     f"min_flight_duration_minutes={self.min_flight_duration}, min_level_points={self.min_level_points}, "
                     f"altitude_tolerance={self.altitude_tolerance}")

        try:
            self._core.analyze_altitude_api(
                fid,
                minutes,
                altitude,
                noise_method,
                dbscan_eps,
                max_gap_seconds,
                jump_threshold,
                window_size,
                min_samples_range_start,
                min_samples_range_end,
                min_samples_step,
                min_flight_duration_seconds, # Pass in seconds
                min_level_points,
                altitude_tolerance,
                result_buffer,
                ctypes.c_int(buffer_size)
            )
        except Exception as e:
            logger.exception(f"Error calling core engine for FID {self.fid}: {e}")
            return {
                "status": "error",
                "message": f"Error calling core engine: {str(e)}",
                "fid": self.fid
            }


        # Process result
        raw_result = result_buffer.value
        if not raw_result:
            logger.error(f"Empty response from core for FID: {self.fid}")
            return {
                "status": "error",
                "message": "Core engine returned empty response",
                "fid": self.fid
            }

        try:
            result_str = raw_result.decode('utf-8')
        except UnicodeDecodeError as e:
            logger.exception(f"Decoding failed for FID: {self.fid}")
            return {
                "status": "error",
                "message": f"Response decoding failed: {str(e)}",
                "fid": self.fid,
                "raw_bytes": str(raw_result[:200])  # Log first 200 bytes for debug
            }

        try:
            result = json.loads(result_str)
            logger.info(f"Analysis completed for FID: {self.fid}. Status: {result.get('status', 'unknown')}")

            # Extract and log diagnostics from the C core's output
            diagnostics = result.get('diagnostics', {})
            for key, value in diagnostics.items():
                if key == 'message':
                    # Log the C core's message at INFO level
                    logger.info(f"Core Diagnostic Message: {value}")
                else:
                    # Log other diagnostics at DEBUG level
                    logger.debug(f"Core Diagnostic: {key}={value}")

            if result.get('status') == 'error':
                logger.error(f"Core engine reported an error: {result.get('message', 'No message provided')}")
            elif result.get('status') == 'no_data':
                logger.warning(f"Core engine reported no data for analysis: {result.get('message', 'No message provided')}")
            elif result.get('status') == 'no_data_after_filter':
                logger.warning(f"Core engine reported no data after filtering: {result.get('message', 'No message provided')}")
            elif result.get('status') == 'no_level_flights':
                logger.info(f"Core engine reported no level flights found: {result.get('message', 'No message provided')}")


            # Add Python-side diagnostics to response (if not already present)
            result['diagnostics'] = result.get('diagnostics', {})
            result['diagnostics']['fid_python'] = self.fid # Differentiate from C's fid
            result['diagnostics']['buffer_size_python'] = buffer_size
            result['diagnostics']['result_length_python'] = len(result_str)

            # Ensure all parameters passed are reflected in the output for transparency
            result['parameters'] = result.get('parameters', {})
            result['parameters']['max_gap_minutes'] = self.max_gap_minutes # Re-add for consistency in minutes
            result['parameters']['jump_threshold'] = self.jump_threshold
            result['parameters']['window_size'] = self.window_size
            result['parameters']['min_samples_range_start'] = self.min_samples_range_start
            result['parameters']['min_samples_range_end'] = self.min_samples_range_end
            result['parameters']['min_samples_step'] = self.min_samples_step
            result['parameters']['min_flight_duration_minutes'] = self.min_flight_duration
            result['parameters']['min_level_points'] = self.min_level_points
            result['parameters']['altitude_tolerance'] = self.altitude_tolerance

            return result
        except json.JSONDecodeError as e:
            logger.exception(f"JSON parsing failed for FID: {self.fid}. Raw response start: '{result_str[:500]}'...")
            return {
                "status": "error",
                "message": f"Invalid JSON from core: {str(e)}",
                "fid": self.fid,
                "raw_response_truncated": result_str[:2000]  # First 2000 characters
            }


def main():
    """CLI entry point with enhanced logging"""
    import argparse
    parser = argparse.ArgumentParser(description="Altitude Analysis Tool")
    parser.add_argument('--fid', type=int, required=True, help="Flight ID for data retrieval.")
    parser.add_argument('--minutes', type=int, default=3,
                        help="Minimum duration in minutes for a detected level flight segment.")
    parser.add_argument('--altitude', type=int, default=10000,
                        help="Minimum altitude (feet) for a detected level flight segment.")
    parser.add_argument('--noise-method', type=str, default='simple', choices=['simple', 'dbscan'],
                        help="Noise filtering method to apply (simple or dbscan).")
    parser.add_argument('--dbscan-eps', type=float, default=0.51,
                        help="DBSCAN epsilon parameter (maximum distance between two samples for one to be considered as in the neighborhood of the other).")
    parser.add_argument('--max-gap-minutes', type=int, default=10,
                        help="Maximum gap between points in minutes to consider same level flight.")
    parser.add_argument('--jump-threshold', type=int, default=5000,
                        help="Threshold for altitude jumps in simple filter (feet).")
    parser.add_argument('--window-size', type=int, default=30,
                        help="Window size for rolling statistics in simple filter.")
    parser.add_argument('--min-samples-range-start', type=int, default=18,
                        help="DBSCAN: Starting value for min_samples search range.")
    parser.add_argument('--min-samples-range-end', type=int, default=180,
                        help="DBSCAN: Ending value for min_samples search range.")
    parser.add_argument('--min-samples-step', type=int, default=18,
                        help="DBSCAN: Step value for min_samples search range.")
    parser.add_argument('--min-flight-duration-minutes', type=int, default=3,
                        help="Minimum duration in minutes for a detected level flight segment to be considered valid.")
    parser.add_argument('--min-level-points', type=int, default=10,
                        help="Minimum number of data points required for a segment to be considered a level flight.")
    parser.add_argument('--altitude-tolerance', type=float, default=50.0,
                        help="Altitude tolerance (feet) for points within a level flight segment.")
    parser.add_argument('--timeout', type=int, default=30,
                        help="Timeout for API data fetching (seconds).")
    parser.add_argument('--max-retries', type=int, default=2,
                        help="Maximum number of retries for API data fetching.")
    parser.add_argument('--verbose', action='store_true', help="Enable debug logging.")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG) # Set root logger level for full verbosity
    else:
        logging.getLogger().setLevel(logging.INFO)

    analyzer = AltitudeAnalyzer(
        fid=args.fid,
        minutes=args.minutes,
        altitude=args.altitude,
        noise_method=args.noise_method,
        dbscan_eps=args.dbscan_eps,
        max_gap_minutes=args.max_gap_minutes,
        jump_threshold=args.jump_threshold,
        window_size=args.window_size,
        min_samples_range_start=args.min_samples_range_start,
        min_samples_range_end=args.min_samples_range_end,
        min_samples_step=args.min_samples_step,
        min_flight_duration=args.min_flight_duration_minutes,
        min_level_points=args.min_level_points,
        altitude_tolerance=args.altitude_tolerance,
        timeout=args.timeout,
        max_retries=args.max_retries
    )

    result = analyzer.analyze()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
