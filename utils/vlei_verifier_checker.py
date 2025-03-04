from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
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
        verifier_url for verifier_url in router_state.get_verifier_instances()
        if not verifier_health_check(verifier_url)
    ]

    # Log and remove unhealthy instances from verifier_instances
    for unhealthy_instance in unhealthy_instances:
        logger.info(f"unhealthy verifier instance: {unhealthy_instance}")
        router_state.remove_verifier_instance(unhealthy_instance)


    # Remove entries from aid_to_verifier_instances_mapping that map to unhealthy instances
    aid_to_verifier_mapping = router_state.get_aid_to_verifier_mapping()
    for k, v in aid_to_verifier_mapping.items():
        if v in unhealthy_instances:
            router_state.remove_aid_to_verifier_mapping(k)

    logger.info(f"verifier_instances: {router_state.get_verifier_instances()}")
    logger.info(f"aid_to_verifier_instances_mapping: {router_state.get_aid_to_verifier_mapping()}")


def run_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the task to run every 10 seconds
    scheduler.add_job(
        check_verifier_instances,
        trigger=IntervalTrigger(seconds=10),
    )

    scheduler.start()