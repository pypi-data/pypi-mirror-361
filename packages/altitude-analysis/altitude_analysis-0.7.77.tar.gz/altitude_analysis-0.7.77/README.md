### Just works like a charm.

# Key Features
## Noise Detection Methods

### Simple Method (default):
 - **Statistical filtering using rolling percentiles**

 - **Faster processing**

 - **Use for cleaner datasets**

### DBSCAN Method:

- **Cluster-based noise detection**

- **Better for noisy data**

- **Automatically optimizes parameters**

- **Enable with --noise-method dbscan**

### Usage:

- **pip install altitude_analysis**
~~~python
from altitude_analysis import AltitudeAnalyzer
analyzer = AltitudeAnalyzer(fid=0000)
results = analyzer.analyze()
print(f"Analysis results: {results}")
~~~
- **Enjoy**
