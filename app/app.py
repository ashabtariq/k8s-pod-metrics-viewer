import eventlet

eventlet.monkey_patch()

import time
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from kubernetes import client, config
from dotenv import load_dotenv
import os
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

# -----------------------
# Redis connection
# -----------------------
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
try:
    redis_client = redis.StrictRedis(
        host=redis_host, port=redis_port, decode_responses=True
    )
    logger.info("Redis connected successfully")
except Exception as ex:
    logger.critical(f"Redis connection failed: {ex}")
    redis_client = None

socketio = SocketIO(app, cors_allowed_origins="*")
pod_data_cache = []  # Initialize as empty list instead of dict

# -----------------------
# Kubernetes config
# -----------------------
k8s_configured = False
try:
    config.load_incluster_config()
    k8s_configured = True
    logger.info("Loaded in-cluster config.")
except config.config_exception.ConfigException:
    logger.info("Falling back to local kubeconfig.")
    try:
        config.load_kube_config()
        k8s_configured = True
        logger.info("Loaded local kubeconfig.")
    except Exception as e:
        logger.error(f"Could not load kubeconfig: {e}")


def fetch_pod_metrics():
    """Fetches pod metrics safely."""
    if not k8s_configured:
        logger.warning("Kubernetes not configured, returning cached data")
        return pod_data_cache or []

    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace="default")

        pod_list = []

        # Try to get metrics, but don't fail if metrics-server is unavailable
        metrics_dict = {}
        try:
            api_client = client.CustomObjectsApi()
            pod_metrics = api_client.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace="default",
                plural="pods",
            )
            metrics_dict = {
                item["metadata"]["name"]: item for item in pod_metrics.get("items", [])
            }
            logger.info(f"Fetched metrics for {len(metrics_dict)} pods")
        except Exception as metrics_error:
            logger.warning(
                f"Metrics API not available (metrics-server may not be installed): {metrics_error}"
            )

        for pod in pods.items:
            pod_name = pod.metadata.name
            metrics = metrics_dict.get(pod_name, {})
            cpu_usage = "N/A"
            memory_usage = "N/A"

            if metrics and "containers" in metrics:
                try:
                    total_cpu = sum(
                        int(c["usage"]["cpu"].strip("n")) for c in metrics["containers"]
                    )
                    total_memory = sum(
                        int(c["usage"]["memory"].strip("Ki"))
                        for c in metrics["containers"]
                    )
                    cpu_usage = f"{total_cpu / 1_000_000_000:.2f} cores"
                    memory_usage = f"{total_memory / 1024:.2f} Mi"
                except Exception as parse_error:
                    logger.warning(
                        f"Error parsing metrics for {pod_name}: {parse_error}"
                    )

            pod_list.append(
                {
                    "name": pod_name,
                    "status": pod.status.phase,
                    "ip": pod.status.pod_ip or "N/A",
                    "cpu": cpu_usage,
                    "memory": memory_usage,
                }
            )

        logger.info(f"Fetched {len(pod_list)} pods")
        return pod_list

    except Exception as e:
        logger.error(f"Pod fetch failed: {e}", exc_info=True)
        return pod_data_cache or []


def background_thread():
    global pod_data_cache
    logger.info("Background thread started")
    while True:
        try:
            pod_data_cache = fetch_pod_metrics()
            logger.debug(f"Broadcasting metrics for {len(pod_data_cache)} pods")
            socketio.emit(
                "pod_metrics",
                {"pods": pod_data_cache, "pod_count": len(pod_data_cache)},
            )
        except Exception as se:
            logger.error(f"Error in background thread: {se}", exc_info=True)

        eventlet.sleep(5)


@app.route("/")
def pods_page():
    try:
        if redis_client:
            count = redis_client.incr("visitor_count")
        else:
            count = "N/A"
    except Exception as ex:
        logger.error(f"Redis error: {ex}")
        count = "N/A"

    pod_data = fetch_pod_metrics()
    pod_count = len(pod_data)

    logger.info(f"Rendering page with {pod_count} pods and visitor count: {count}")
    return render_template("pods.html", pods=pod_data, pod_count=pod_count, count=count)


@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")
    emit("pod_metrics", {"pods": pod_data_cache, "pod_count": len(pod_data_cache)})


if __name__ == "__main__":
    # Fetch initial pod data before starting
    logger.info("Fetching initial pod data...")
    pod_data_cache = fetch_pod_metrics()
    logger.info(f"Initial pod count: {len(pod_data_cache)}")

    socketio.start_background_task(background_thread)
    socketio.run(app, host="0.0.0.0", port=5000)
