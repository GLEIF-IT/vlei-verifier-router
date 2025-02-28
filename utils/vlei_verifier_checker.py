from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import logging
import requests
from utils.router_state import RouterState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verifier_health_check(verifier_url: str) -> bool:
    try:
        requests.get(f"{verifier_url}/health")
    except requests.exceptions.RequestException as e:
        return False
    return True


def check_verifier_instances():
    router_state = RouterState.get_state()
    # Identify unhealthy instances
    unhealthy_instances = [
        verifier_url for verifier_url in router_state.verifier_instances
        if not verifier_health_check(verifier_url)
    ]

    # Log unhealthy instances
    for unhealthy_instance in unhealthy_instances:
        logger.info(f"unhealthy verifier instance: {unhealthy_instance}")

    # Remove unhealthy instances from verifier_instances
    router_state.verifier_instances = [
        verifier_url for verifier_url in router_state.verifier_instances
        if verifier_url not in unhealthy_instances
    ]

    # Remove entries from aid_to_verifier_instances_mapping that map to unhealthy instances
    router_state.aid_to_verifier_instances_mapping = {
        aid: verifier_url for aid, verifier_url in router_state.aid_to_verifier_instances_mapping.items()
        if verifier_url not in unhealthy_instances
    }

    logger.info(f"Updated verifier_instances: {router_state.verifier_instances}")
    logger.info(f"Updated aid_to_verifier_instances_mapping: {router_state.aid_to_verifier_instances_mapping}")


def run_api_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the task to run every 10 seconds
    scheduler.add_job(
        check_verifier_instances,
        trigger=IntervalTrigger(seconds=10),
    )

    scheduler.start()