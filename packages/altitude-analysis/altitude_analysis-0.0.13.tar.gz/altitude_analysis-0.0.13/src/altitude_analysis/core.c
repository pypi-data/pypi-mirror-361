#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <float.h>       // For DBL_MAX
#include <curl/curl.h>
#include <jansson.h>

// Constants
#define MAX_POINTS 100000
#define MAX_LEVELS 1000
#define MAX_STRING 2048
#define HTTP_TIMEOUT 10
#define MIN_SAMPLES_RANGE_START 18
#define MIN_SAMPLES_RANGE_END 180
#define MIN_SAMPLES_STEP 18
#define DEFAULT_JUMP_THRESHOLD 5000
#define DEFAULT_WINDOW_SIZE 30
#define MIN_FLIGHT_DURATION 180  // 3 minutes in seconds
#define MAX_TIME_GAP 300         // 5 minutes in seconds
#define MIN_LEVEL_POINTS 10

// [REST OF THE IMPLEMENTATION REMAINS THE SAME AS BEFORE]
// ... (keep all the existing code as is)

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
FlightData fetch_data(int fid, const char *table);
FlightData simple_noise_filter(FlightData data, int jump_threshold, int window_size);
FlightData dbscan_noise_filter(FlightData data, double eps);
LevelFlightsResult detect_level_flights(FlightData data, int min_minutes, int min_altitude);
char* analyze_altitude(int fid, int minutes, int altitude, const char *noise_method, double dbscan_eps);
void sort_by_time(FlightData *data);
double calculate_median(double *values, size_t count);
double calculate_quantile(double *values, size_t count, double quantile);
double calculate_silhouette_score(double *values, size_t count, int *labels);
void free_flight_data(FlightData *data);
void free_level_flights(LevelFlightsResult *result);
size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp);

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

    qsort(sorted, count, sizeof(double), (int (*)(const void*, const void*))strcmp);

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

    qsort(sorted, count, sizeof(double), (int (*)(const void*, const void*))strcmp);

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
    CURLcode res;
    MemoryBuffer chunk = {NULL, 0};
    char url[MAX_STRING];

    // Build URL
    snprintf(url, MAX_STRING,
             "https://devops.azur.local/dev/airdataapi/data/%s/?fid=%d",
             table, fid);

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if (!curl) {
        fprintf(stderr, "Failed to initialize CURL\n");
        return data;
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
    if (res != CURLE_OK) {
        fprintf(stderr, "CURL failed: %s\n", curl_easy_strerror(res));
        curl_easy_cleanup(curl);
        free(chunk.memory);
        return data;
    }

    // Cleanup CURL
    curl_easy_cleanup(curl);
    curl_global_cleanup();

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
    if (!json_is_array(root)) {
        fprintf(stderr, "Expected JSON array\n");
        json_decref(root);
        return data;
    }

    // Allocate initial memory
    data.capacity = json_array_size(root);
    data.points = malloc(data.capacity * sizeof(DataPoint));
    if (!data.points) {
        json_decref(root);
        return data;
    }

    // Parse data points
    size_t index;
    json_t *value;
    json_array_foreach(root, index, value) {
        json_t *time_obj = json_object_get(value, "time");
        json_t *value_obj = json_object_get(value, "value");

        if (!time_obj || !value_obj) continue;

        const char *time_str = json_string_value(time_obj);
        double val = json_real_value(value_obj);

        if (!time_str || isnan(val)) continue;

        // Parse ISO 8601 time
        struct tm tm;
        if (strptime(time_str, "%Y-%m-%dT%H:%M:%SZ", &tm) == NULL) {
            continue;
        }
        tm.tm_isdst = -1;  // Let system determine DST

        DataPoint point;
        point.time = timegm(&tm);
        point.value = val;

        // Add to array
        if (data.count >= data.capacity) {
            size_t new_capacity = data.capacity * 2;
            DataPoint *new_points = realloc(data.points, new_capacity * sizeof(DataPoint));
            if (!new_points) break;
            data.points = new_points;
            data.capacity = new_capacity;
        }

        data.points[data.count++] = point;
    }

    json_decref(root);
    return data;
}

// Simple noise filter
FlightData simple_noise_filter(FlightData data, int jump_threshold, int window_size) {
    FlightData filtered = {NULL, 0, 0};
    if (data.count == 0) return filtered;

    // Allocate memory
    filtered.capacity = data.count;
    filtered.points = malloc(filtered.capacity * sizeof(DataPoint));
    if (!filtered.points) return filtered;

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
                if (!new_points) break;
                filtered.points = new_points;
                filtered.capacity = new_capacity;
            }
            filtered.points[filtered.count++] = data.points[i];
        }
    }

    // If not enough points, return original
    if (filtered.count < MIN_LEVEL_POINTS) {
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
        free(filtered.points);
        return filtered;
    }

    // Calculate rolling statistics
    for (size_t i = 0; i < filtered.count; i++) {
        size_t start = (i > window/2) ? i - window/2 : 0;
        size_t end = (i + window/2 < filtered.count) ? i + window/2 + 1 : filtered.count;
        size_t num = end - start;

        double *window_values = malloc(num * sizeof(double));
        if (!window_values) continue;

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
            final.points[final.count++] = filtered.points[i];
        }
    }

    free(filtered.points);
    return final;
}

// DBSCAN noise filter
FlightData dbscan_noise_filter(FlightData data, double eps) {
    FlightData filtered = {NULL, 0, 0};
    if (data.count < 20) return data;

    // Create value array
    double *values = malloc(data.count * sizeof(double));
    if (!values) return data;
    for (size_t i = 0; i < data.count; i++) {
        values[i] = data.points[i].value;
    }

    // Find optimal min_samples
    int best_min_samples = 18;
    double best_score = -1.0;

    for (int min_samples = MIN_SAMPLES_RANGE_START;
         min_samples < MIN_SAMPLES_RANGE_END;
         min_samples += MIN_SAMPLES_STEP) {

        // Allocate labels
        int *labels = calloc(data.count, sizeof(int));
        if (!labels) continue;

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
                    // Add new neighbors to the list
                    neighbors = realloc(neighbors, (neighbor_count + new_count) * sizeof(size_t));
                    if (!neighbors) {
                        free(new_neighbors);
                        free(labels);
                        free(values);
                        return data;
                    }
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
                neighbors = realloc(neighbors, (neighbor_count + new_count) * sizeof(size_t));
                if (!neighbors) {
                    free(new_neighbors);
                    free(labels);
                    free(values);
                    return data;
                }
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
        free(labels);
        free(values);
        return data;
    }

    for (size_t i = 0; i < data.count; i++) {
        if (labels[i] != 0) {  // Keep non-noise points
            filtered.points[filtered.count++] = data.points[i];
        }
    }

    // Additional difference filtering
    if (filtered.count > 1) {
        FlightData final = {NULL, 0, filtered.count};
        final.points = malloc(final.capacity * sizeof(DataPoint));
        if (!final.points) {
            free(filtered.points);
            free(labels);
            free(values);
            return filtered;
        }

        final.points[final.count++] = filtered.points[0];
        for (size_t i = 1; i < filtered.count; i++) {
            double diff = fabs(filtered.points[i].value - filtered.points[i-1].value);
            if (diff < DEFAULT_JUMP_THRESHOLD) {
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

// Detect level flights
LevelFlightsResult detect_level_flights(FlightData data, int min_minutes, int min_altitude) {
    LevelFlightsResult result = {NULL, 0, 0};
    if (data.count == 0) return result;

    // Sort by time
    sort_by_time(&data);

    // Group by altitude
    result.capacity = 16;
    result.flights = malloc(result.capacity * sizeof(LevelFlight));
    if (!result.flights) return result;

    double current_altitude = round(data.points[0].value / 100) * 100;
    time_t start_time = data.points[0].time;
    time_t end_time = data.points[0].time;
    size_t group_size = 1;

    for (size_t i = 1; i < data.count; i++) {
        double altitude = round(data.points[i].value / 100) * 100;
        time_t current_time = data.points[i].time;

        // Check if same altitude group continues
        if (altitude == current_altitude &&
            (current_time - end_time) <= MAX_TIME_GAP) {
            end_time = current_time;
            group_size++;
            continue;
        }

        // Save current group if valid
        if (group_size >= MIN_LEVEL_POINTS) {
            long duration = end_time - start_time;
            if (duration >= min_minutes * 60 && current_altitude >= min_altitude) {
                if (result.count >= result.capacity) {
                    size_t new_capacity = result.capacity * 2;
                    LevelFlight *new_flights = realloc(result.flights, new_capacity * sizeof(LevelFlight));
                    if (!new_flights) break;
                    result.flights = new_flights;
                    result.capacity = new_capacity;
                }

                result.flights[result.count].start_time = start_time;
                result.flights[result.count].end_time = end_time;
                result.flights[result.count].altitude = current_altitude;
                result.flights[result.count].duration = duration;
                result.count++;
            }
        }

        // Start new group
        current_altitude = altitude;
        start_time = current_time;
        end_time = current_time;
        group_size = 1;
    }

    // Save last group
    if (group_size >= MIN_LEVEL_POINTS) {
        long duration = end_time - start_time;
        if (duration >= min_minutes * 60 && current_altitude >= min_altitude) {
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
                result.flights[result.count].altitude = current_altitude;
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
char* analyze_altitude(int fid, int minutes, int altitude, const char *noise_method, double dbscan_eps) {
    // Create default result
    json_t *root = json_object();
    json_object_set_new(root, "status", json_string("success"));
    json_object_set_new(root, "flight_id", json_integer(fid));
    json_object_set_new(root, "flights", json_array());

    // Fetch data
    FlightData raw_data = fetch_data(fid, "adc_l_r_a_4_alt_1013");
    if (raw_data.count == 0) {
        json_object_set_new(root, "status", json_string("no_data"));
        char *result = json_dumps(root, JSON_INDENT(2));
        json_decref(root);
        return result;
    }

    // Apply noise filtering
    FlightData filtered_data;
    if (strcmp(noise_method, "dbscan") == 0) {
        filtered_data = dbscan_noise_filter(raw_data, dbscan_eps);
    } else {
        filtered_data = simple_noise_filter(raw_data, DEFAULT_JUMP_THRESHOLD, DEFAULT_WINDOW_SIZE);
    }

    free_flight_data(&raw_data);

    // Detect level flights
    LevelFlightsResult flights = detect_level_flights(filtered_data, minutes, altitude);
    free_flight_data(&filtered_data);

    // Build flights array
    json_t *flights_array = json_array();
    for (size_t i = 0; i < flights.count; i++) {
        LevelFlight flight = flights.flights[i];

        // Format times
        char start_str[MAX_STRING], end_str[MAX_STRING], duration_str[MAX_STRING];
        struct tm *tm;

        tm = gmtime(&flight.start_time);
        strftime(start_str, MAX_STRING, "%Y-%m-%d %H:%M:%S", tm);

        tm = gmtime(&flight.end_time);
        strftime(end_str, MAX_STRING, "%Y-%m-%d %H:%M:%S", tm);

        long secs = flight.duration;
        snprintf(duration_str, MAX_STRING, "%02ld:%02ld:%02ld",
                 secs / 3600, (secs % 3600) / 60, secs % 60);

        // Create flight object
        json_t *flight_obj = json_object();
        json_object_set_new(flight_obj, "start_time", json_string(start_str));
        json_object_set_new(flight_obj, "end_time", json_string(end_str));
        json_object_set_new(flight_obj, "duration", json_string(duration_str));
        json_object_set_new(flight_obj, "altitude", json_real(flight.altitude));

        json_array_append_new(flights_array, flight_obj);
    }

    json_object_set_new(root, "flights", flights_array);
    free_level_flights(&flights);

    // Serialize and return
    char *result = json_dumps(root, JSON_INDENT(2));
    json_decref(root);
    return result;
}

// API function for external call
void analyze_altitude_api(int fid, int minutes, int altitude,
                          char* noise_method, double dbscan_eps,
                          char* output, int output_size) {
    char *result = analyze_altitude(fid, minutes, altitude, noise_method, dbscan_eps);
    strncpy(output, result, output_size - 1);
    output[output_size - 1] = '\0';
    free(result);
}