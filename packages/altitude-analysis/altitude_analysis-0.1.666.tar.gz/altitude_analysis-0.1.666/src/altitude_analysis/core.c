#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <float.h>
#include <ctype.h>
#include <curl/curl.h>
#include <jansson.h>

// Constants
#define MAX_POINTS 100000
#define MAX_LEVELS 1000
#define MAX_STRING 2048
#define HTTP_TIMEOUT 30
#define MAX_RETRIES 2
#define DEFAULT_JUMP_THRESHOLD 5000
#define DEFAULT_WINDOW_SIZE 30

// Data structures
typedef struct {
    time_t time;
    double value;
} DataPoint;

typedef struct {
    time_t start_time;
    time_t end_time;
    double altitude;
    long duration;
} LevelFlight;

typedef struct {
    DataPoint *points;
    size_t count;
    size_t capacity;
} FlightData;

typedef struct {
    LevelFlight *flights;
    size_t count;
    size_t capacity;
} LevelFlightsResult;

typedef struct {
    char *memory;
    size_t size;
} MemoryBuffer;

// Function prototypes
time_t portable_timegm(struct tm *tm);
FlightData fetch_data(int fid, const char *table);
FlightData simple_noise_filter(FlightData data, int jump_threshold, int window_size);
FlightData dbscan_noise_filter(FlightData data, double eps);
LevelFlightsResult detect_level_flights(FlightData data, int min_flight_duration_seconds, int min_altitude, int max_gap_seconds, double altitude_tolerance, int min_level_points);
char* analyze_altitude(int fid, int minutes, int altitude, const char *noise_method, double dbscan_eps, int max_gap_seconds, double altitude_tolerance, int min_flight_duration_seconds, int min_level_points);
void sort_by_time(FlightData *data);
double calculate_median(double *values, size_t count);
double calculate_quantile(double *values, size_t count, double quantile);
double calculate_silhouette_score(double *values, size_t count, int *labels);
void free_flight_data(FlightData *data);
void free_level_flights(LevelFlightsResult *result);
size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp);
int compare_doubles(const void *a, const void *b);

// Function to get JSON type as string
const char* json_type_string(json_type type) {
    switch(type) {
        case JSON_OBJECT:  return "object";
        case JSON_ARRAY:   return "array";
        case JSON_STRING: return "string";
        case JSON_INTEGER: return "integer";
        case JSON_REAL:    return "real";
        case JSON_TRUE:    return "true";
        case JSON_FALSE:   return "false";
        case JSON_NULL:    return "null";
        default:           return "unknown";
    }
}

// Double comparison function for sorting
int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

time_t portable_timegm(struct tm *tm) {
    time_t ret;
    char *tz = getenv("TZ");
    setenv("TZ", "", 1);
    tzset();
    ret = mktime(tm);
    if (tz) {
        setenv("TZ", tz, 1);
    } else {
        unsetenv("TZ");
    }
    tzset();
    return ret;
}

// Helper function for sorting
int compare_points(const void *a, const void *b) {
    const DataPoint *pointA = (const DataPoint *)a;
    const DataPoint *pointB = (const DataPoint *)b;
    return (pointA->time > pointB->time) - (pointA->time < pointB->time);
}

// Sort flight data by time
void sort_by_time(FlightData *data) {
    qsort(data->points, data->count, sizeof(DataPoint), compare_points);
}

// Calculate median of values
double calculate_median(double *values, size_t count) {
    if (count == 0) return 0.0;

    // Create a copy to sort
    double *sorted = malloc(count * sizeof(double));
    if (!sorted) return 0.0;
    memcpy(sorted, values, count * sizeof(double));

    qsort(sorted, count, sizeof(double), compare_doubles);

    double median;
    if (count % 2 == 0) {
        median = (sorted[count/2 - 1] + sorted[count/2]) / 2.0;
    } else {
        median = sorted[count/2];
    }

    free(sorted);
    return median;
}

// Calculate quantile of values
double calculate_quantile(double *values, size_t count, double quantile) {
    if (count == 0) return 0.0;
    if (quantile < 0.0) quantile = 0.0;
    if (quantile > 1.0) quantile = 1.0;

    // Create a copy to sort
    double *sorted = malloc(count * sizeof(double));
    if (!sorted) return 0.0;
    memcpy(sorted, values, count * sizeof(double));

    qsort(sorted, count, sizeof(double), compare_doubles);

    double index = quantile * (count - 1);
    size_t lower = (size_t)floor(index);
    size_t upper = (size_t)ceil(index);

    if (lower == upper) {
        free(sorted);
        return sorted[lower];
    }

    double weight = index - lower;
    double result = sorted[lower] * (1.0 - weight) + sorted[upper] * weight;
    free(sorted);
    return result;
}

// Calculate silhouette score (simplified for performance)
double calculate_silhouette_score(double *values, size_t count, int *labels) {
    if (count < 2) return -1.0;

    // Count clusters and points per cluster
    int max_cluster = 0;
    for (size_t i = 0; i < count; i++) {
        if (labels[i] > max_cluster) max_cluster = labels[i];
    }

    if (max_cluster <= 0) return -1.0;  // Only noise

    size_t *cluster_counts = calloc(max_cluster + 1, sizeof(size_t));
    if (!cluster_counts) return -1.0;

    for (size_t i = 0; i < count; i++) {
        if (labels[i] > 0) cluster_counts[labels[i]]++;
    }

    // Calculate average silhouette
    double total_score = 0.0;
    size_t valid_points = 0;

    for (size_t i = 0; i < count; i++) {
        if (labels[i] <= 0) continue;  // Skip noise

        double a_i = 0.0;  // Average intra-cluster distance
        double b_i = DBL_MAX;  // Smallest average inter-cluster distance

        // Calculate intra-cluster distance
        size_t intra_count = 0;
        for (size_t j = 0; j < count; j++) {
            if (labels[j] == labels[i]) {
                a_i += fabs(values[i] - values[j]);
                intra_count++;
            }
        }
        if (intra_count > 1) a_i /= (intra_count - 1);

        // Calculate inter-cluster distances
        for (int c = 1; c <= max_cluster; c++) {
            if (c == labels[i] || cluster_counts[c] == 0) continue;

            double inter_dist = 0.0;
            size_t inter_count = 0;

            for (size_t j = 0; j < count; j++) {
                if (labels[j] == c) {
                    inter_dist += fabs(values[i] - values[j]);
                    inter_count++;
                }
            }

            if (inter_count > 0) {
                inter_dist /= inter_count;
                if (inter_dist < b_i) b_i = inter_dist;
            }
        }

        if (b_i == DBL_MAX) continue;  // No other clusters

        double s_i = (b_i - a_i) / fmax(a_i, b_i);
        total_score += s_i;
        valid_points++;
    }

    free(cluster_counts);
    return valid_points > 0 ? total_score / valid_points : -1.0;
}

// Memory callback for CURL
size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    MemoryBuffer *mem = (MemoryBuffer *)userp;

    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (!ptr) return 0;

    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

// Fetch data from API
FlightData fetch_data(int fid, const char *table) {
    FlightData data = {NULL, 0, 0};
    CURL *curl;
    CURLcode res = CURLE_OK;
    MemoryBuffer chunk = {NULL, 0};
    char url[MAX_STRING];
    int retry_count = 0;

    // Build URL
    snprintf(url, MAX_STRING,
             "https://devops.azur.local/dev/airdataapi/data/%s/?fid=%d",
             table, fid);

    curl_global_init(CURL_GLOBAL_DEFAULT);

    // Retry loop
    while (retry_count <= MAX_RETRIES) {
        curl = curl_easy_init();
        if (!curl) {
            fprintf(stderr, "Failed to initialize CURL\n");
            break;
        }

        // Reset memory buffer for each attempt
        if (chunk.memory) {
            free(chunk.memory);
            chunk.memory = NULL;
            chunk.size = 0;
        }

        // Set CURL options
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, HTTP_TIMEOUT);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);

        // Perform request
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if (res == CURLE_OK) {
            break;  // Success, exit retry loop
        }

        fprintf(stderr, "CURL attempt %d failed: %s\n",
                retry_count + 1, curl_easy_strerror(res));

        retry_count++;

        // Add delay between retries (1 second)
        if (retry_count <= MAX_RETRIES) {
            // Portable sleep using C standard
            struct timespec ts;
            ts.tv_sec = 1;
            ts.tv_nsec = 0;
            nanosleep(&ts, NULL);
        }
    }

    curl_global_cleanup();

    // If all retries failed
    if (res != CURLE_OK) {
        fprintf(stderr, "All CURL attempts failed\n");
        if (chunk.memory) free(chunk.memory);
        return data;
    }

    // Parse JSON response
    json_t *root;
    json_error_t error;
    root = json_loads(chunk.memory, 0, &error);
    free(chunk.memory);

    if (!root) {
        fprintf(stderr, "JSON error on line %d: %s\n", error.line, error.text);
        return data;
    }

    // Check if it's an array
    json_type type = json_typeof(root);
    if (type != JSON_ARRAY) {
        const char *type_str = json_type_string(type);
        fprintf(stderr, "Expected JSON array but got: %s\n", type_str);
        json_decref(root);
        return data;
    }

    // Get array size
    size_t array_size = json_array_size(root);
    if (array_size == 0) {
        fprintf(stderr, "Empty data array received\n");
        json_decref(root);
        return data;
    }

    // Allocate memory
    data.capacity = array_size;
    data.points = malloc(data.capacity * sizeof(DataPoint));
    if (!data.points) {
        fprintf(stderr, "Memory allocation failed for %zu points\n", array_size);
        json_decref(root);
        return data;
    }

    // Parse data points
    size_t index;
    json_t *value;
    json_array_foreach(root, index, value) {
        if (!json_is_object(value)) {
            fprintf(stderr, "Skipping non-object element at index %zu\n", index);
            continue;
        }

        json_t *time_obj = json_object_get(value, "time");
        json_t *value_obj = json_object_get(value, "value");

        if (!time_obj || !value_obj) {
            fprintf(stderr, "Missing time or value field at index %zu\n", index);
            continue;
        }

        const char *time_str = json_string_value(time_obj);
        double val = 0.0;

        // Handle different number types
        if (json_is_real(value_obj)) {
            val = json_real_value(value_obj);
        } else if (json_is_integer(value_obj)) {
            val = (double)json_integer_value(value_obj);
        } else {
            fprintf(stderr, "Non-numeric value at index %zu\n", index);
            continue;
        }

        // Validate values
        if (!time_str) {
            fprintf(stderr, "Invalid time format at index %zu\n", index);
            continue;
        }

        // Check for NaN
        if (val != val) {
            fprintf(stderr, "NaN value at index %zu\n", index);
            continue;
        }

        // Parse ISO 8601 time - handle fractional seconds
        struct tm tm;
        memset(&tm, 0, sizeof(struct tm));
        char* parse_result;
        int valid_time = 0;

        // Try format with fractional seconds
        parse_result = strptime(time_str, "%Y-%m-%dT%H:%M:%S", &tm);
        if (parse_result) {
            // Skip fractional seconds if present
            if (*parse_result == '.') {
                parse_result++;  // Skip the decimal point
                // Skip digits
                while (parse_result && *parse_result && isdigit((unsigned char)*parse_result)) {
                    parse_result++;
                }
            }
            // Expect UTC 'Z' at end
            if (parse_result && *parse_result == 'Z') {
                valid_time = 1;
            }
        }

        // If not valid, try without fractional seconds
        if (!valid_time) {
            parse_result = strptime(time_str, "%Y-%m-%dT%H:%M:%SZ", &tm);
            if (parse_result) valid_time = 1;
        }

        // Try alternative format
        if (!valid_time) {
            parse_result = strptime(time_str, "%Y-%m-%d %H:%M:%S", &tm);
            if (parse_result) valid_time = 1;
        }

        if (!valid_time) {
            fprintf(stderr, "Time parse failed: %s\n", time_str);
            continue;
        }

        tm.tm_isdst = -1;

        DataPoint point;
        point.time = portable_timegm(&tm);
        point.value = val;

        // Add to array
        if (data.count < data.capacity) {
            data.points[data.count++] = point;
        } else {
            fprintf(stderr, "Data capacity exceeded at index %zu\n", index);
        }
    }

    json_decref(root);

    if (data.count == 0) {
        fprintf(stderr, "No valid data points found after parsing\n");
    } else {
        fprintf(stderr, "Successfully parsed %zu/%zu data points\n", data.count, array_size);
    }

    return data;
}

// Simple noise filter
FlightData simple_noise_filter(FlightData data, int jump_threshold, int window_size) {
    FlightData filtered = {NULL, 0, 0};
    if (data.count == 0) return filtered;

    // Allocate memory
    filtered.capacity = data.count;
    filtered.points = malloc(filtered.capacity * sizeof(DataPoint));
    if (!filtered.points) {
        fprintf(stderr, "Memory allocation failed in simple_noise_filter\n");
        return filtered;
    }

    // Sort by time
    sort_by_time(&data);

    // Filter based on jump threshold
    filtered.points[filtered.count++] = data.points[0];
    for (size_t i = 1; i < data.count; i++) {
        double diff = fabs(data.points[i].value - data.points[i-1].value);
        if (diff < jump_threshold) {
            if (filtered.count >= filtered.capacity) {
                size_t new_capacity = filtered.capacity * 2;
                DataPoint *new_points = realloc(filtered.points, new_capacity * sizeof(DataPoint));
                if (!new_points) {
                    fprintf(stderr, "Memory reallocation failed in simple_noise_filter\n");
                    free(filtered.points);
                    filtered.points = NULL;
                    filtered.count = 0;
                    filtered.capacity = 0;
                    return filtered;
                }
                filtered.points = new_points;
                filtered.capacity = new_capacity;
            }
            filtered.points[filtered.count++] = data.points[i];
        }
    }

    // If not enough points, return original
    if (filtered.count < 10) {
        free(filtered.points);
        return data;
    }

    // Calculate adaptive window size
    size_t window = (size_t)window_size;
    if (filtered.count / 2 < window) {
        window = filtered.count / 2;
    }
    if (window < 1) window = 1;

    // Prepare for rolling statistics
    FlightData final = {NULL, 0, filtered.count};
    final.points = malloc(final.capacity * sizeof(DataPoint));
    if (!final.points) {
        fprintf(stderr, "Memory allocation failed for rolling stats\n");
        free(filtered.points);
        filtered.points = NULL;
        return filtered;
    }

    // Calculate rolling statistics
    for (size_t i = 0; i < filtered.count; i++) {
        size_t start = (i > window/2) ? i - window/2 : 0;
        size_t end = (i + window/2 < filtered.count) ? i + window/2 + 1 : filtered.count;
        size_t num = end - start;

        double *window_values = malloc(num * sizeof(double));
        if (!window_values) {
            fprintf(stderr, "Memory allocation failed for window values\n");
            continue;
        }

        for (size_t j = 0; j < num; j++) {
            window_values[j] = filtered.points[start + j].value;
        }

        double q1 = calculate_quantile(window_values, num, 0.25);
        double q3 = calculate_quantile(window_values, num, 0.75);
        double iqr = q3 - q1;
        double lower_bound = q1 - 1.5 * iqr;
        double upper_bound = q3 + 1.5 * iqr;

        free(window_values);

        if (filtered.points[i].value >= lower_bound && filtered.points[i].value <= upper_bound) {
            if (final.count >= final.capacity) {
                fprintf(stderr, "Final capacity exceeded in simple filter\n");
                break;
            }
            final.points[final.count++] = filtered.points[i];
        }
    }

    free(filtered.points);
    return final;
}

// DBSCAN noise filter
FlightData dbscan_noise_filter(FlightData data, double eps) {
    FlightData filtered = {NULL, 0, 0};
    if (data.count < 20) {
        fprintf(stderr, "Insufficient data for DBSCAN (%zu points)\n", data.count);
        return data;
    }

    // Create value array
    double *values = malloc(data.count * sizeof(double));
    if (!values) {
        fprintf(stderr, "Memory allocation failed for DBSCAN values\n");
        return data;
    }
    for (size_t i = 0; i < data.count; i++) {
        values[i] = data.points[i].value;
    }

    // Find optimal min_samples
    int best_min_samples = 18;
    double best_score = -1.0;

    for (int min_samples = 18; min_samples < 180; min_samples += 18) {
        // Allocate labels
        int *labels = calloc(data.count, sizeof(int));
        if (!labels) {
            fprintf(stderr, "Memory allocation failed for DBSCAN labels\n");
            free(values);
            return data;
        }

        // Initialize as unvisited
        for (size_t i = 0; i < data.count; i++) {
            labels[i] = -1; // Unvisited
        }

        int cluster_id = 0;

        // Main DBSCAN loop
        for (size_t i = 0; i < data.count; i++) {
            if (labels[i] != -1) continue; // Already visited

            // Find neighbors
            size_t *neighbors = malloc(data.count * sizeof(size_t));
            if (!neighbors) {
                fprintf(stderr, "Memory allocation failed for DBSCAN neighbors\n");
                free(labels);
                free(values);
                return data;
            }
            size_t neighbor_count = 0;

            for (size_t j = 0; j < data.count; j++) {
                if (fabs(values[i] - values[j]) <= eps) {
                    neighbors[neighbor_count++] = j;
                }
            }

            if (neighbor_count < (size_t)min_samples) {
                labels[i] = 0; // Noise
                free(neighbors);
                continue;
            }

            // Start new cluster
            cluster_id++;
            labels[i] = cluster_id;

            // Process neighbors
            for (size_t j = 0; j < neighbor_count; j++) {
                size_t idx = neighbors[j];

                if (labels[idx] == 0) {
                    labels[idx] = cluster_id; // Change noise to border point
                }

                if (labels[idx] != -1) continue; // Already processed

                labels[idx] = cluster_id;

                // Find neighbors of this neighbor
                size_t *new_neighbors = malloc(data.count * sizeof(size_t));
                if (!new_neighbors) {
                    fprintf(stderr, "Memory allocation failed for DBSCAN new_neighbors\n");
                    free(neighbors);
                    free(labels);
                    free(values);
                    return data;
                }
                size_t new_count = 0;

                for (size_t k = 0; k < data.count; k++) {
                    if (fabs(values[idx] - values[k]) <= eps) {
                        new_neighbors[new_count++] = k;
                    }
                }

                // Expand neighborhood if necessary
                if (new_count >= (size_t)min_samples) {
                    size_t *temp = realloc(neighbors, (neighbor_count + new_count) * sizeof(size_t));
                    if (!temp) {
                        fprintf(stderr, "Memory reallocation failed for DBSCAN neighbors expansion\n");
                        free(new_neighbors);
                        free(neighbors);
                        free(labels);
                        free(values);
                        return data;
                    }
                    neighbors = temp;
                    for (size_t k = 0; k < new_count; k++) {
                        neighbors[neighbor_count++] = new_neighbors[k];
                    }
                }

                free(new_neighbors);
            }

            free(neighbors);
        }

        // Calculate silhouette score
        double score = calculate_silhouette_score(values, data.count, labels);
        if (score > best_score) {
            best_score = score;
            best_min_samples = min_samples;
        }

        free(labels);
    }

    // Run DBSCAN with best parameters
    int *labels = calloc(data.count, sizeof(int));
    if (!labels) {
        fprintf(stderr, "Memory allocation failed for final DBSCAN labels\n");
        free(values);
        return data;
    }

    // Initialize as unvisited
    for (size_t i = 0; i < data.count; i++) {
        labels[i] = -1; // Unvisited
    }

    int cluster_id = 0;

    // Main DBSCAN loop
    for (size_t i = 0; i < data.count; i++) {
        if (labels[i] != -1) continue;

        // Find neighbors
        size_t *neighbors = malloc(data.count * sizeof(size_t));
        if (!neighbors) {
            fprintf(stderr, "Memory allocation failed for final DBSCAN neighbors\n");
            free(labels);
            free(values);
            return data;
        }
        size_t neighbor_count = 0;

        for (size_t j = 0; j < data.count; j++) {
            if (fabs(values[i] - values[j]) <= eps) {
                neighbors[neighbor_count++] = j;
            }
        }

        if (neighbor_count < (size_t)best_min_samples) {
            labels[i] = 0; // Noise
            free(neighbors);
            continue;
        }

        // Start new cluster
        cluster_id++;
        labels[i] = cluster_id;

        // Process neighbors
        for (size_t j = 0; j < neighbor_count; j++) {
            size_t idx = neighbors[j];

            if (labels[idx] == 0) {
                labels[idx] = cluster_id; // Change noise to border point
            }

            if (labels[idx] != -1) continue;

            labels[idx] = cluster_id;

            // Find neighbors of this neighbor
            size_t *new_neighbors = malloc(data.count * sizeof(size_t));
            if (!new_neighbors) {
                fprintf(stderr, "Memory allocation failed for final DBSCAN new_neighbors\n");
                free(neighbors);
                free(labels);
                free(values);
                return data;
            }
            size_t new_count = 0;

            for (size_t k = 0; k < data.count; k++) {
                if (fabs(values[idx] - values[k]) <= eps) {
                    new_neighbors[new_count++] = k;
                }
            }

            // Expand neighborhood if necessary
            if (new_count >= (size_t)best_min_samples) {
                size_t *temp = realloc(neighbors, (neighbor_count + new_count) * sizeof(size_t));
                if (!temp) {
                    fprintf(stderr, "Memory reallocation failed for final DBSCAN neighbors expansion\n");
                    free(new_neighbors);
                    free(neighbors);
                    free(labels);
                    free(values);
                    return data;
                }
                neighbors = temp;
                for (size_t k = 0; k < new_count; k++) {
                    neighbors[neighbor_count++] = new_neighbors[k];
                }
            }

            free(new_neighbors);
        }

        free(neighbors);
    }

    // Create filtered data (remove noise)
    filtered.capacity = data.count;
    filtered.points = malloc(filtered.capacity * sizeof(DataPoint));
    if (!filtered.points) {
        fprintf(stderr, "Memory allocation failed for DBSCAN filtered points\n");
        free(labels);
        free(values);
        return data;
    }

    for (size_t i = 0; i < data.count; i++) {
        if (labels[i] != 0) {  // Keep non-noise points
            if (filtered.count >= filtered.capacity) {
                fprintf(stderr, "DBSCAN filtered capacity exceeded\n");
                break;
            }
            filtered.points[filtered.count++] = data.points[i];
        }
    }

    // Additional difference filtering
    if (filtered.count > 1) {
        FlightData final = {NULL, 0, filtered.count};
        final.points = malloc(final.capacity * sizeof(DataPoint));
        if (!final.points) {
            fprintf(stderr, "Memory allocation failed for DBSCAN final points\n");
            free(filtered.points);
            free(labels);
            free(values);
            return filtered;
        }

        final.points[final.count++] = filtered.points[0];
        for (size_t i = 1; i < filtered.count; i++) {
            double diff = fabs(filtered.points[i].value - filtered.points[i-1].value);
            if (diff < DEFAULT_JUMP_THRESHOLD) {
                if (final.count >= final.capacity) {
                    fprintf(stderr, "DBSCAN final capacity exceeded\n");
                    break;
                }
                final.points[final.count++] = filtered.points[i];
            }
        }

        free(filtered.points);
        filtered = final;
    }

    free(labels);
    free(values);
    return filtered;
}

// Detect level flights with tolerance band
LevelFlightsResult detect_level_flights(FlightData data, int min_flight_duration_seconds, int min_altitude, int max_gap_seconds, double altitude_tolerance, int min_level_points) {
    LevelFlightsResult result = {NULL, 0, 0};
    if (data.count == 0) return result;

    // Sort by time
    sort_by_time(&data);

    // Group by altitude
    result.capacity = 16;
    result.flights = malloc(result.capacity * sizeof(LevelFlight));
    if (!result.flights) {
        fprintf(stderr, "Memory allocation failed for level flights\n");
        return result;
    }

    double current_flight_level = round(data.points[0].value / 100.0) * 100.0;
    time_t start_time = data.points[0].time;
    time_t end_time = data.points[0].time;
    size_t group_size = 1;

    for (size_t i = 1; i < data.count; i++) {
        double alt = data.points[i].value;
        time_t current_time = data.points[i].time;

        // Check if point is within tolerance of current flight level and within time gap
        if (fabs(alt - current_flight_level) <= altitude_tolerance &&
            (current_time - end_time) <= max_gap_seconds) {
            end_time = current_time;
            group_size++;
        } else {
            // Save current group if it meets criteria
            if (group_size >= min_level_points) {
                long duration = end_time - start_time;
                if (duration >= min_flight_duration_seconds && current_flight_level >= min_altitude) {
                    if (result.count >= result.capacity) {
                        size_t new_capacity = result.capacity * 2;
                        LevelFlight *new_flights = realloc(result.flights, new_capacity * sizeof(LevelFlight));
                        if (!new_flights) {
                            fprintf(stderr, "Memory reallocation failed for level flights\n");
                            break;
                        }
                        result.flights = new_flights;
                        result.capacity = new_capacity;
                    }

                    result.flights[result.count].start_time = start_time;
                    result.flights[result.count].end_time = end_time;
                    result.flights[result.count].altitude = current_flight_level;
                    result.flights[result.count].duration = duration;
                    result.count++;
                }
            }

            // Start new group
            current_flight_level = round(alt / 100.0) * 100.0;
            start_time = current_time;
            end_time = current_time;
            group_size = 1;
        }
    }

    // Save last group
    if (group_size >= min_level_points) {
        long duration = end_time - start_time;
        if (duration >= min_flight_duration_seconds && current_flight_level >= min_altitude) {
            if (result.count >= result.capacity) {
                size_t new_capacity = result.capacity * 2;
                LevelFlight *new_flights = realloc(result.flights, new_capacity * sizeof(LevelFlight));
                if (new_flights) {
                    result.flights = new_flights;
                    result.capacity = new_capacity;
                }
            }

            if (result.count < result.capacity) {
                result.flights[result.count].start_time = start_time;
                result.flights[result.count].end_time = end_time;
                result.flights[result.count].altitude = current_flight_level;
                result.flights[result.count].duration = duration;
                result.count++;
            }
        }
    }

    return result;
}

// Free flight data memory
void free_flight_data(FlightData *data) {
    if (data && data->points) {
        free(data->points);
        data->points = NULL;
        data->count = 0;
        data->capacity = 0;
    }
}

// Free level flights memory
void free_level_flights(LevelFlightsResult *result) {
    if (result && result->flights) {
        free(result->flights);
        result->flights = NULL;
        result->count = 0;
        result->capacity = 0;
    }
}

// Main analysis function
char* analyze_altitude(int fid, int minutes, int altitude, const char *noise_method, double dbscan_eps, int max_gap_seconds,
                       double altitude_tolerance, int min_flight_duration_seconds, int min_level_points) {
    // Create default result with diagnostic info
    json_t *root = json_object();
    if (!root) {
        fprintf(stderr, "Failed to create root JSON object\n");
        return strdup("{\"status\":\"error\",\"message\":\"JSON object creation failed\"}");
    }

    json_object_set_new(root, "status", json_string("started"));
    json_object_set_new(root, "flight_id", json_integer(fid));

    json_t *params = json_object();
    if (!params) {
        fprintf(stderr, "Failed to create parameters JSON object\n");
        json_decref(root);
        return strdup("{\"status\":\"error\",\"message\":\"Parameters object creation failed\"}");
    }
    json_object_set_new(root, "parameters", params);

    json_t *diag = json_object();
    if (!diag) {
        fprintf(stderr, "Failed to create diagnostics JSON object\n");
        json_decref(root);
        return strdup("{\"status\":\"error\",\"message\":\"Diagnostics object creation failed\"}");
    }
    json_object_set_new(root, "diagnostics", diag);

    json_t *flights_array = json_array();
    if (!flights_array) {
        fprintf(stderr, "Failed to create flights JSON array\n");
        json_decref(root);
        return strdup("{\"status\":\"error\",\"message\":\"Flights array creation failed\"}");
    }
    json_object_set_new(root, "flights", flights_array);

    // Add parameters
    json_object_set_new(params, "minutes", json_integer(minutes));
    json_object_set_new(params, "altitude", json_integer(altitude));
    json_object_set_new(params, "noise_method", json_string(noise_method));
    json_object_set_new(params, "dbscan_eps", json_real(dbscan_eps));
    json_object_set_new(params, "max_gap_seconds", json_integer(max_gap_seconds));
    json_object_set_new(params, "altitude_tolerance", json_real(altitude_tolerance));
    json_object_set_new(params, "min_flight_duration_seconds", json_integer(min_flight_duration_seconds));
    json_object_set_new(params, "min_level_points", json_integer(min_level_points));

    // Add diagnostics
    clock_t start_time = clock();

    // Fetch data
    json_object_set_new(diag, "fetch_start", json_string("true"));
    FlightData raw_data = fetch_data(fid, "adc_l_r_a_4_alt_1013");
    json_object_set_new(diag, "raw_data_points", json_integer(raw_data.count));

    if (raw_data.count == 0) {
        json_object_set_new(root, "status", json_string("no_data"));
        char *result = json_dumps(root, JSON_COMPACT);
        json_decref(root);
        return result;
    }

    // Apply noise filtering
    json_object_set_new(diag, "filter_start", json_string("true"));
    FlightData filtered_data;
    if (strcmp(noise_method, "dbscan") == 0) {
        filtered_data = dbscan_noise_filter(raw_data, dbscan_eps);
    } else {
        filtered_data = simple_noise_filter(raw_data, DEFAULT_JUMP_THRESHOLD, DEFAULT_WINDOW_SIZE);
    }
    json_object_set_new(diag, "filtered_data_points", json_integer(filtered_data.count));
    free_flight_data(&raw_data);

    // Check if filtering failed
    if (filtered_data.count == 0) {
        json_object_set_new(root, "status", json_string("no_data_after_filter"));
        char *result = json_dumps(root, JSON_COMPACT);
        json_decref(root);
        return result;
    }

    // Detect level flights
    json_object_set_new(diag, "detection_start", json_string("true"));
    LevelFlightsResult flights = detect_level_flights(
        filtered_data,
        min_flight_duration_seconds,
        altitude,
        max_gap_seconds,
        altitude_tolerance,
        min_level_points
    );
    json_object_set_new(diag, "level_flights_found", json_integer(flights.count));
    free_flight_data(&filtered_data);

    // Build flights array
    for (size_t i = 0; i < flights.count; i++) {
        LevelFlight flight = flights.flights[i];

        // Format times
        char start_str[MAX_STRING], end_str[MAX_STRING], duration_str[MAX_STRING];
        struct tm *tm;

        tm = gmtime(&flight.start_time);
        if (tm) {
            strftime(start_str, MAX_STRING, "%Y-%m-%d %H:%M:%S", tm);
        } else {
            strcpy(start_str, "invalid_time");
        }

        tm = gmtime(&flight.end_time);
        if (tm) {
            strftime(end_str, MAX_STRING, "%Y-%m-%d %H:%M:%S", tm);
        } else {
            strcpy(end_str, "invalid_time");
        }

        long secs = flight.duration;
        snprintf(duration_str, MAX_STRING, "%02ld:%02ld:%02ld",
                 secs / 3600, (secs % 3600) / 60, secs % 60);

        // Create flight object
        json_t *flight_obj = json_object();
        if (!flight_obj) {
            fprintf(stderr, "Failed to create flight JSON object\n");
            continue;
        }

        json_object_set_new(flight_obj, "start_time", json_string(start_str));
        json_object_set_new(flight_obj, "end_time", json_string(end_str));
        json_object_set_new(flight_obj, "duration", json_string(duration_str));
        json_object_set_new(flight_obj, "altitude", json_real(flight.altitude));

        json_array_append_new(flights_array, flight_obj);
    }

    // Add diagnostics
    clock_t end_time = clock();
    double elapsed = (double)(end_time - start_time) / CLOCKS_PER_SEC;
    json_object_set_new(diag, "processing_time_sec", json_real(elapsed));
    json_object_set_new(diag, "result_flight_count", json_integer(flights.count));

    // Final status
    if (flights.count > 0) {
        json_object_set_new(root, "status", json_string("success"));
    } else {
        json_object_set_new(root, "status", json_string("no_level_flights"));
    }

    free_level_flights(&flights);

    // Serialize and return
    char *result = json_dumps(root, JSON_COMPACT);
    json_decref(root);

    if (!result) {
        fprintf(stderr, "JSON serialization failed\n");
        return strdup("{\"status\":\"error\",\"message\":\"JSON serialization failed\"}");
    }

    return result;
}

// API function for external call
void analyze_altitude_api(int fid, int minutes, int altitude,
                          char* noise_method, double dbscan_eps,
                          int max_gap_seconds,
                          int jump_threshold, int window_size,
                          int min_samples_range_start, int min_samples_range_end, int min_samples_step,
                          int min_flight_duration_seconds, int min_level_points, double altitude_tolerance,
                          char* output, int output_size)
{
    // Simply call the existing analyze_altitude function with the parameters it expects
    char *result = analyze_altitude(
        fid,
        minutes,
        altitude,
        noise_method,
        dbscan_eps,
        max_gap_seconds,
        altitude_tolerance,
        min_flight_duration_seconds,
        min_level_points
    );

    // Handle NULL result from analyze_altitude
    if (result == NULL) {
        const char *error_msg = "{\"status\":\"error\",\"message\":\"Core engine returned NULL result\"}";
        strncpy(output, error_msg, output_size - 1);
        output[output_size - 1] = '\0';
        return;
    }

    // Copy result to output buffer
    size_t result_len = strlen(result);
    if (result_len >= (size_t)output_size) {
        fprintf(stderr, "Result too large for buffer (%zu vs %d)\n", result_len, output_size);
        const char *error_msg = "{\"status\":\"error\",\"message\":\"Result too large for buffer\"}";
        strncpy(output, error_msg, output_size - 1);
    } else {
        strncpy(output, result, output_size - 1);
    }
    output[output_size - 1] = '\0';
    free(result);
}