# Example usage
import logging
import os

from amazon.opentelemetry.distro.exporter.aws.metrics.aws_cloudwatch_emf_exporter import AwsCloudWatchEmfExporter

if __name__ == "__main__":
    import random
    import time

    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource

    # Setup basic logging
    logging.basicConfig(level=logging.DEBUG)

    # Force exponential histogram aggregation
    os.environ.setdefault(
        "OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION", "base2_exponential_bucket_histogram"
    )

    # Create a resource
    resource = Resource.create(
        {"service.name": "my-service", "service.version": "0.1.0", "deployment.environment": "production"}
    )

    # Create EMF exporter directly
    emf_exporter = AwsCloudWatchEmfExporter(
        namespace="MyApplication1", log_group_name="/aws/otel/my-app", aws_region="us-east-1"
    )

    # Create metric reader
    metric_reader = PeriodicExportingMetricReader(
        exporter=emf_exporter, export_interval_millis=5000  # Export every 5 seconds for testing
    )

    # Create meter provider with resource
    meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)

    # Set global meter provider
    metrics.set_meter_provider(meter_provider)

    # Create a meter
    meter = meter_provider.get_meter("my-app-meter")

    # Create some metrics
    request_counter = meter.create_counter(name="http_requests_total", description="Total HTTP requests", unit="1")

    request_duration = meter.create_histogram(
        name="http_request_duration_seconds", description="HTTP request duration", unit="s"
    )

    cpu_usage_gauge = meter.create_gauge(
        name="system_cpu_usage_percent", description="Current CPU usage percentage", unit="Percent"
    )

    # Create a new histogram for file sizes with exponential distribution
    # This will use exponential histogram aggregation because of the environment variable
    # and the wide range of values it will record
    file_sizes = meter.create_histogram(
        name="file_size_bytes", description="File sizes in bytes showing exponential distribution", unit="By"
    )

    # Use the metrics in a loop to simulate traffic with different attribute sets
    print("Generating metrics with different attribute sets. Press Ctrl+C to stop...")
    try:
        while True:
            # Group 1: Method GET, Status 200
            request_counter.add(1, {"method": "GET", "status": "200"})

            cpu_usage_gauge.set(0.2, {"host": "server-01", "region": "us-east-1"})
            request_duration.record(0.1 + (0.5 * random.random()), {"method": "GET", "status": "200"})

            # Group 2: Method POST, Status 201
            request_counter.add(1, {"method": "POST", "status": "201"})
            request_duration.record(0.2 + (0.7 * random.random()), {"method": "POST", "status": "201"})

            # Group 3: Method GET, Status 500 (error case)
            if random.random() < 0.1:  # 10% error rate
                request_counter.add(1, {"method": "GET", "status": "500"})
                request_duration.record(1.0 + (1.0 * random.random()), {"method": "GET", "status": "500"})

            # Record exponentially-distributed file sizes to test exponential histogram
            # Use file types as additional dimensions
            file_sizes.record(2 ** random.randint(1, 10), {"file_type": "text", "operation": "read"})  # 2B to 1KB
            file_sizes.record(2 ** random.randint(10, 15), {"file_type": "image", "operation": "read"})  # 1KB to 32KB
            file_sizes.record(2 ** random.randint(15, 20), {"file_type": "video", "operation": "read"})  # 32KB to 1MB
            file_sizes.record(
                2 ** random.randint(20, 25), {"file_type": "archive", "operation": "write"}
            )  # 1MB to 32MB

            # Sleep between 100ms and 300ms
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping metric generation.")
        # Force flush metrics
        print("Flushing metrics...")
        metric_reader.force_flush()
    #
