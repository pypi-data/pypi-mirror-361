"""
Public API for altitude analysis package
"""
import ctypes
import json
import os
import platform
import glob
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AltitudeAnalyzer:
    def __init__(self, fid, minutes=3, altitude=10000,
                 noise_method='simple', dbscan_eps=0.51, timeout=30, max_retries=2):
        self.fid = fid
        self.minutes = minutes
        self.altitude = altitude
        self.noise_method = noise_method
        self.dbscan_eps = dbscan_eps
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

        return ctypes.CDLL(lib_path)

    def analyze(self):
        """Execute analysis with detailed diagnostics"""
        # Prepare inputs
        fid = ctypes.c_int(self.fid)
        minutes = ctypes.c_int(self.minutes)
        altitude = ctypes.c_int(self.altitude)
        noise_method = ctypes.c_char_p(self.noise_method.encode())
        dbscan_eps = ctypes.c_double(self.dbscan_eps)

        # Prepare output buffer - increased to 2MB
        buffer_size = 2 * 1024 * 1024  # 2MB buffer
        result_buffer = ctypes.create_string_buffer(buffer_size)

        # Call core function
        logger.info(f"Starting analysis for FID: {self.fid}")
        self._core.analyze_altitude_api(
            fid,
            minutes,
            altitude,
            noise_method,
            dbscan_eps,
            result_buffer,
            ctypes.c_int(buffer_size)
        )

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
                "raw_bytes": str(raw_result[:200])  # First 200 bytes
            }

        try:
            result = json.loads(result_str)
            logger.info(f"Analysis completed for FID: {self.fid}. Status: {result.get('status', 'unknown')}")

            # Add diagnostics to response
            result['diagnostics'] = result.get('diagnostics', {})
            result['diagnostics']['fid'] = self.fid
            result['diagnostics']['buffer_size'] = buffer_size
            result['diagnostics']['result_length'] = len(result_str)

            return result
        except json.JSONDecodeError as e:
            logger.exception(f"JSON parsing failed for FID: {self.fid}")
            return {
                "status": "error",
                "message": f"Invalid JSON from core: {str(e)}",
                "fid": self.fid,
                "raw_response": result_str[:2000]  # First 2000 characters
            }

def main():
    """CLI entry point with enhanced logging"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--fid', type=int, required=True)
    parser.add_argument('--minutes', type=int, default=3)
    parser.add_argument('--altitude', type=int, default=10000)
    parser.add_argument('--noise-method', default='simple')
    parser.add_argument('--dbscan-eps', type=float, default=0.51)
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--max-retries', type=int, default=2)
    parser.add_argument('--verbose', action='store_true', help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    analyzer = AltitudeAnalyzer(
        fid=args.fid,
        minutes=args.minutes,
        altitude=args.altitude,
        noise_method=args.noise_method,
        dbscan_eps=args.dbscan_eps,
        timeout=args.timeout,
        max_retries=args.max_retries
    )

    result = analyzer.analyze()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
