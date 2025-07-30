"""
Advanced Aircraft Altitude Analysis Tool
Combines simple filtering and DBSCAN-based noise detection methods
"""

import time
import logging
import argparse
import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from typing import Dict, List, Optional, Tuple, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_API_URL = "https://devops.azur.local/dev/airdataapi/data/"
DEFAULT_JUMP_THRESHOLD = 5000
DEFAULT_WINDOW_SIZE = 30
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)


def _create_session() -> requests.Session:
    """Create configured HTTP session with retry logic"""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=DEFAULT_RETRY_STRATEGY)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class AltitudeAnalyzer:
    """Core class for processing altitude data with multiple noise detection methods"""

    def __init__(self, table: str, fid: Union[int, List[int]],
                 minutes: int = 3, altitude: int = 10000,
                 timezone: str = 'UTC', api_url: str = DEFAULT_API_URL,
                 noise_method: str = 'simple',
                 dbscan_eps: float = 0.51,
                 simple_jump_threshold: int = DEFAULT_JUMP_THRESHOLD,
                 simple_window_size: int = DEFAULT_WINDOW_SIZE):
        """
        Initialize analyzer with configuration parameters

        :param table: Data table identifier
        :param fid: Flight ID or list of Flight IDs
        :param minutes: Minimum duration for level flight (minutes)
        :param altitude: Minimum altitude threshold (feet)
        :param timezone: Timezone for output formatting
        :param api_url: Base URL for data API
        :param noise_method: Noise detection method ('simple' or 'dbscan')
        :param dbscan_eps: DBSCAN epsilon parameter
        :param simple_jump_threshold: Jump threshold for simple method
        :param simple_window_size: Window size for simple method
        """
        self.table = table
        self.fid = [fid] if isinstance(fid, int) else fid
        self.minutes = minutes
        self.altitude = altitude
        self.timezone = timezone
        self.api_url = api_url
        self.noise_method = noise_method.lower()
        self.dbscan_eps = dbscan_eps
        self.simple_jump_threshold = simple_jump_threshold
        self.simple_window_size = simple_window_size
        self.session = _create_session()

    def fetch_data(self, fid: int) -> Tuple[Optional[pd.DataFrame], float]:
        """Fetch data from API endpoint for a single flight"""
        logger.debug(f"Fetching data for {self.table}/{fid}")
        url = f'{self.api_url}{self.table}/?fid={fid}'
        start_time = time.time()

        try:
            response = self.session.get(
                url,
                timeout=DEFAULT_TIMEOUT,
                verify=False
            )
            response.raise_for_status()

            df = pd.DataFrame(response.json())
            df['time'] = pd.to_datetime(df['time'], utc=True)
            elapsed = time.time() - start_time

            logger.debug(f"Fetched {len(df)} records in {elapsed:.2f}s")
            return df[['time', 'value']], elapsed

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for FID {fid}: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for FID {fid}: {str(e)}")

        return None, time.time() - start_time

    def simple_noise_filter(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], float]:
        """Simple noise detection using Z-scores and difference filtering"""
        if df.empty:
            logger.warning("Empty DataFrame received for filtering")
            return df, 0.0

        logger.debug("Applying simple noise filters")
        start_time = time.time()

        try:
            # Make working copy to avoid mutating original
            df = df.copy().sort_values('time')

            # Remove extreme jumps
            df['value_diff'] = df['value'].diff().abs()
            df = df[(df['value_diff'] < self.simple_jump_threshold) |
                    (df['value_diff'].isna())]

            # Calculate adaptive window size
            window = min(self.simple_window_size, len(df) // 2 or 1)

            # Compute rolling statistics
            df['median'] = df['value'].rolling(
                window=window, min_periods=1, center=True
            ).median()
            df['q1'] = df['value'].rolling(
                window=window, min_periods=1, center=True
            ).quantile(0.25)
            df['q3'] = df['value'].rolling(
                window=window, min_periods=1, center=True
            ).quantile(0.75)
            df['iqr'] = df['q3'] - df['q1']

            # Filter outliers
            lower_bound = df['q1'] - 1.5 * df['iqr']
            upper_bound = df['q3'] + 1.5 * df['iqr']
            filtered = df[(df['value'] >= lower_bound) &
                          (df['value'] <= upper_bound)]

            # Cleanup intermediate columns
            result = filtered.drop(columns=[
                'value_diff', 'median', 'q1', 'q3', 'iqr'
            ])

            elapsed = time.time() - start_time
            logger.debug(f"Filtered {len(result)}/{len(df)} records in {elapsed:.2f}s")
            return result, elapsed

        except Exception as e:
            logger.error(f"Simple filtering failed: {str(e)}")
            return None, time.time() - start_time

    def dbscan_noise_filter(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], float]:
        """DBSCAN-based noise detection with parameter optimization"""
        if df.empty or len(df) < 20:
            logger.warning("Insufficient data for DBSCAN filtering")
            return df, 0.0

        logger.debug("Applying DBSCAN noise detection")
        start_time = time.time()

        try:
            X = df[['value']].values

            # Parameter search space
            min_samples_range = range(18, 180, 18)  # Reduced search space
            best_score = -1
            best_params = None

            # Find optimal min_samples parameter
            for min_samples in min_samples_range:
                db = DBSCAN(eps=self.dbscan_eps, min_samples=min_samples, n_jobs=-1)
                labels = db.fit_predict(X)
                unique_labels = np.unique(labels)

                # Skip if only noise or one cluster
                if len(unique_labels) < 2 or -1 not in unique_labels:
                    continue

                try:
                    # Only calculate score if we have multiple clusters
                    score = silhouette_score(X, labels)
                    if score > best_score:
                        best_score = score
                        best_params = min_samples
                except:
                    continue

            # Apply best parameters found
            min_samples = best_params if best_params else 18
            logger.debug(f"Using DBSCAN params: eps={self.dbscan_eps}, min_samples={min_samples}")

            db = DBSCAN(eps=self.dbscan_eps, min_samples=min_samples, n_jobs=-1)
            labels = db.fit_predict(X)
            non_noise_mask = labels != -1  # Filter out noise points

            # Create final mask with same length as original DataFrame
            final_mask = np.zeros(len(df), dtype=bool)

            if np.any(non_noise_mask):
                # Get indices of non-noise points
                non_noise_indices = np.flatnonzero(non_noise_mask)
                non_noise_values = df.loc[non_noise_mask, 'value'].values

                # Compute differences between consecutive non-noise points
                if non_noise_values.shape[0] > 1:
                    diffs = np.abs(non_noise_values[1:] - non_noise_values[:-1])
                    # First point always included, others based on jump threshold
                    diff_mask = np.concatenate(([True], diffs < 5000))
                else:
                    diff_mask = np.array([True])  # Single point case

                # Apply difference mask to non-noise points
                if diff_mask.shape[0] == non_noise_indices.shape[0]:
                    final_mask[non_noise_indices] = diff_mask
                else:
                    # Fallback to simple mask if lengths don't match
                    logger.warning("Length mismatch in DBSCAN filtering, using simple mask")
                    final_mask[non_noise_indices] = True

            result = df.loc[final_mask]
            elapsed = time.time() - start_time
            logger.debug(f"DBSCAN filtered {len(result)}/{len(df)} records in {elapsed:.2f}s")
            return result, elapsed

        except Exception as e:
            logger.error(f"DBSCAN filtering failed: {str(e)}")
            return None, time.time() - start_time

    def detect_level_flights(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """Identify level flight segments"""
        logger.debug("Detecting level flights")
        start_time = time.time()

        try:
            # Create working copy
            df = df.sort_values('time').copy()

            # Calculate rounded altitude
            df['altitude'] = (df['value'] / 100).round() * 100

            # Create segment groups
            df['group_marker'] = (
                    (df['altitude'] != df['altitude'].shift(1)) |
                    (df['time'].diff() > pd.Timedelta(minutes=5))
            ).cumsum()

            # Aggregate segments
            segments = df.groupby('group_marker').agg(
                start_time=('time', 'min'),
                end_time=('time', 'max'),
                altitude=('altitude', 'first')
            )
            segments['duration'] = segments['end_time'] - segments['start_time']

            # Filter by duration and altitude
            min_duration = pd.Timedelta(minutes=self.minutes)
            level_flights = segments[
                (segments['duration'] > min_duration) &
                (segments['altitude'] > self.altitude)
                ].copy()

            if level_flights.empty:
                logger.debug("No level flights detected")
                return pd.DataFrame(), time.time() - start_time

            # Merge consecutive segments
            level_flights['merge_group'] = (
                    level_flights['altitude'] != level_flights['altitude'].shift(1)
            ).cumsum()

            merged = level_flights.groupby(['merge_group', 'altitude']).agg(
                start_time=('start_time', 'min'),
                end_time=('end_time', 'max'),
                duration=('duration', 'sum')
            ).reset_index()

            # Format results
            merged['duration'] = merged['end_time'] - merged['start_time']
            merged['duration_str'] = merged['duration'].apply(
                lambda td: str(td).split()[-1].zfill(8)
            )
            merged['altitude'] = merged['altitude'].astype(int)

            # Convert timezones
            merged['start_time'] = (
                merged['start_time'].dt.tz_convert(
                    self.timezone).dt.strftime(
                    '%Y-%m-%d %H:%M:%S')
            )
            merged['end_time'] = (
                merged['end_time'].dt.tz_convert(
                    self.timezone).dt.strftime(
                    '%Y-%m-%d %H:%M:%S')
            )

            result = merged[['start_time', 'end_time', 'duration_str', 'altitude']]
            result.columns = ['start_time', 'end_time', 'duration', 'altitude']

            elapsed = time.time() - start_time
            logger.debug(f"Detected {len(result)} level flights in {elapsed:.2f}s")
            return result.sort_values('start_time'), elapsed

        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            return pd.DataFrame(), time.time() - start_time

    def analyze_flight(self, fid: int) -> Dict[str, Any]:
        """Analyze a single flight"""
        logger.debug(f"Starting analysis for flight {fid}")
        metrics = {}
        results = {}

        # Data acquisition
        df, fetch_time = self.fetch_data(fid)
        metrics['fetch'] = fetch_time

        if df is None or df.empty:
            logger.error(f"No data available for flight {fid}")
            return {
                'fid': fid,
                'result': pd.DataFrame(),
                'metrics': metrics,
                'error': 'DATA_FETCH_FAILED'
            }

        # Data processing
        if self.noise_method == 'dbscan':
            filtered_df, filter_time = self.dbscan_noise_filter(df)
        else:
            filtered_df, filter_time = self.simple_noise_filter(df)
        metrics['filter'] = filter_time

        if filtered_df is None or filtered_df.empty:
            logger.error(f"Filtering produced no usable data for flight {fid}")
            return {
                'fid': fid,
                'result': pd.DataFrame(),
                'metrics': metrics,
                'error': 'FILTERING_FAILED'
            }

        # Flight detection
        result_df, detect_time = self.detect_level_flights(filtered_df)
        metrics['detect'] = detect_time
        metrics['total'] = sum(metrics.values())

        logger.debug(f"Analysis for flight {fid} completed in {metrics['total']:.2f}s")
        return {
            'fid': fid,
            'result': result_df,
            'metrics': metrics,
            'error': None
        }

    def analyze(self) -> List[Dict[str, Any]]:
        """Analyze all configured flights"""
        results = []
        for fid in self.fid:
            results.append(self.analyze_flight(fid))
        return results


def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(
        description='Advanced Aircraft Altitude Analysis',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--table', default='adc_l_r_a_4_alt_1013',
                        help='Data table identifier')
    parser.add_argument('--fid', type=int, nargs='+', required=True,
                        help='Flight ID(s) to analyze')
    parser.add_argument('--minutes', type=int, default=3,
                        help='Minimum level flight duration (minutes)')
    parser.add_argument('--altitude', type=int, default=10000,
                        help='Minimum altitude threshold (feet)')
    parser.add_argument('--timezone', default='UTC',
                        help='Output timezone')
    parser.add_argument('--noise-method', choices=['simple', 'dbscan'], default='simple',
                        help='Noise detection method')
    parser.add_argument('--dbscan-eps', type=float, default=0.51,
                        help='DBSCAN epsilon parameter')
    parser.add_argument('--simple-threshold', type=int, default=DEFAULT_JUMP_THRESHOLD,
                        help='Jump threshold for simple method')
    parser.add_argument('--simple-window', type=int, default=DEFAULT_WINDOW_SIZE,
                        help='Window size for simple method')
    parser.add_argument('--loglevel', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging verbosity level')
    parser.add_argument('--silent', type=bool, default=False,
                        help='Silent mode. No any outputs')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Execute analysis
    analyzer = AltitudeAnalyzer(
        table=args.table,
        fid=args.fid,
        minutes=args.minutes,
        altitude=args.altitude,
        timezone=args.timezone,
        noise_method=args.noise_method,
        dbscan_eps=args.dbscan_eps,
        simple_jump_threshold=args.simple_threshold,
        simple_window_size=args.simple_window
    )

    results = analyzer.analyze()
    overall_metrics = {'fetch': 0, 'filter': 0, 'detect': 0, 'total': 0}
    silent = args.silent
    # Output results
    for result in results:
        fid = result['fid']
        if not silent:
            print(f"\n{'=' * 60}")
            print(f"FLIGHT {fid} RESULTS")
            print('=' * 60)

        if result['error']:
            if not silent:
                print(f"Analysis failed: {result['error']}")
            continue

        if not result['result'].empty:
            if not silent:
                print("\nLEVEL FLIGHTS DETECTED:")
                print(result['result'].to_string(index=False))
        else:
            if not silent:
                print("\nNO LEVEL FLIGHTS DETECTED")

        # Print metrics
        if not silent:
            print("\nPROCESSING METRICS:")
            print('-' * 60)
            print(f"Data Fetch:    {result['metrics']['fetch']:.4f}s")
            print(f"Filtering:     {result['metrics']['filter']:.4f}s")
            print(f"Detection:     {result['metrics']['detect']:.4f}s")
            print(f"TOTAL TIME:    {result['metrics']['total']:.4f}s")

        # Aggregate metrics
        for k in overall_metrics:
            overall_metrics[k] += result['metrics'].get(k, 0)

    # Print summary
    if not silent:
        print(f"\n{'=' * 60}")
        print("SUMMARY ACROSS ALL FLIGHTS")
        print('=' * 60)
        print(f"Total Flights Processed: {len(results)}")
        print(f"Total Fetch Time:        {overall_metrics['fetch']:.4f}s")
        print(f"Total Filter Time:       {overall_metrics['filter']:.4f}s")
        print(f"Total Detect Time:       {overall_metrics['detect']:.4f}s")
        print(f"GRAND TOTAL TIME:        {overall_metrics['total']:.4f}s")

    return result['result']


if __name__ == '__main__':
    main()
