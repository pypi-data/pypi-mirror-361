"""
Public API for altitude analysis package
"""
import ctypes
import json
import os
import platform


class AltitudeAnalyzer:
    def __init__(self, fid, minutes=3, altitude=10000,
                 noise_method='simple', dbscan_eps=0.51):
        self.fid = fid
        self.minutes = minutes
        self.altitude = altitude
        self.noise_method = noise_method
        self.dbscan_eps = dbscan_eps

        # Load compiled core
        self._core = self._load_core()

    def _load_core(self):
        """Load the compiled core library"""
        # Determine platform-specific file extension
        ext = '.dll' if platform.system() == 'Windows' else '.so'

        # Get the path to the compiled library
        lib_path = os.path.join(
            os.path.dirname(__file__),
            f'core{ext}'
        )

        if not os.path.exists(lib_path):
            raise RuntimeError("Core engine not found. Please reinstall package.")

        return ctypes.CDLL(lib_path)

    def analyze(self):
        """Execute analysis through core engine"""
        # Prepare inputs
        fid = ctypes.c_int(self.fid)
        minutes = ctypes.c_int(self.minutes)
        altitude = ctypes.c_int(self.altitude)
        noise_method = ctypes.c_char_p(self.noise_method.encode())
        dbscan_eps = ctypes.c_double(self.dbscan_eps)

        # Prepare output buffer
        result_buffer = ctypes.create_string_buffer(1024)

        # Call core function
        self._core.analyze_altitude(
            fid,
            minutes,
            altitude,
            noise_method,
            dbscan_eps,
            result_buffer,
            ctypes.c_int(1024)
        )

        # Return results as JSON
        return json.loads(result_buffer.value.decode())


def main():
    """CLI entry point"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--fid', type=int, required=True)
    parser.add_argument('--minutes', type=int, default=3)
    parser.add_argument('--altitude', type=int, default=10000)
    parser.add_argument('--noise-method', default='simple')
    parser.add_argument('--dbscan-eps', type=float, default=0.51)

    args = parser.parse_args()

    analyzer = AltitudeAnalyzer(
        fid=args.fid,
        minutes=args.minutes,
        altitude=args.altitude,
        noise_method=args.noise_method,
        dbscan_eps=args.dbscan_eps
    )

    result = analyzer.analyze()
    print(json.dumps(result, indent=2))