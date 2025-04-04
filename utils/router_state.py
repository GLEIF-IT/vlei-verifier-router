import json
import os
from dataclasses import dataclass
import redis
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class RouterState:
    """
    Singleton class to manage verifier instances and their mappings to AIDs using Redis.
    """

    _instance: Optional["RouterState"] = None
    _current_verifier_instance_num: int = 0

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of RouterState exists (singleton pattern).
        """
        if cls._instance is None:
            logger.debug("Creating new RouterState instance.")
            cls._instance = super().__new__(cls)
            object.__setattr__(cls._instance, '_initialized', False)
        return cls._instance

    def __post_init__(self):
        """
        Prevent re-initialization of the singleton instance.
        """
        if getattr(self, '_initialized', False):
            logger.error("RouterState is a singleton and cannot be re-initialized.")
            raise RuntimeError("RouterState is a singleton and cannot be re-initialized.")
        object.__setattr__(self, '_initialized', True)
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.verifier_instances = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.aid_to_verifier_mapping = redis.Redis(host=redis_host, port=redis_port, db=1)
        logger.info("RouterState initialized successfully.")

    @classmethod
    def initialize(cls, **kwargs) -> "RouterState":
        """
        Initialize the singleton instance with custom arguments. Can only be called once.
        """
        if cls._instance is None:
            logger.debug("Initializing RouterState with custom arguments.")
            cls._instance = cls()
            cls._instance.preload_verifier_instances(**kwargs)
        else:
            logger.warning("RouterState is already initialized. Returning existing instance.")
        return cls._instance

    def preload_verifier_instances(self, verifier_instances: list):
        self.verifier_instances.set("verifier_instances", json.dumps(verifier_instances))

    @classmethod
    def get_state(cls) -> "RouterState":
        """
        Get the existing instance of RouterState. Raises an error if not initialized.
        """
        if cls._instance is None:
            logger.error("RouterState has not been initialized.")
            raise RuntimeError("RouterState has not been initialized.")
        logger.debug("Returning existing RouterState instance.")
        return cls._instance

    def get_verifier_instances(self) -> List[str]:
        """
        Retrieve the list of verifier instances from Redis (DB 0).
        """
        verifier_instances = self.verifier_instances.get("verifier_instances")
        if verifier_instances:
            return json.loads(verifier_instances)
        return []

    def add_verifier_instance(self, verifier_instance: str) -> None:
        """
        Add a single verifier instance to Redis (DB 0).
        """
        verifier_instances = self.get_verifier_instances()
        if verifier_instance not in verifier_instances:
            verifier_instances.append(verifier_instance)
            self.verifier_instances.set("verifier_instances", json.dumps(verifier_instances))
            logger.info(f"Added verifier instance: {verifier_instance}")
        else:
            logger.warning(f"Verifier instance already exists: {verifier_instance}")

    def remove_verifier_instance(self, verifier_instance: str) -> None:
        """
        Remove a single verifier instance from Redis (DB 0).
        """
        verifier_instances = self.get_verifier_instances()
        if verifier_instance in verifier_instances:
            verifier_instances.remove(verifier_instance)
            self.verifier_instances.set("verifier_instances", json.dumps(verifier_instances))
            logger.info(f"Removed verifier instance: {verifier_instance}")
        else:
            logger.warning(f"Verifier instance not found: {verifier_instance}")

    def get_aid_to_verifier_mapping(self) -> Dict[str, str]:
        """
        Retrieve all AID-to-verifier mappings from Redis.
        """
        # Get all keys matching the pattern (in this case, all keys)
        keys = self.aid_to_verifier_mapping.keys("*")
        mappings = {}
        for key in keys:
            aid = key.decode("utf-8")  # Decode bytes to string
            verifier_instance = self.aid_to_verifier_mapping.get(aid).decode("utf-8")
            mappings[aid] = verifier_instance
        return mappings

    def add_aid_to_verifier_mapping(self, aid: str, verifier_instance: str) -> None:
        """
        Add a single AID-to-verifier mapping to Redis (DB 1).
        """
        self.aid_to_verifier_mapping.set(aid, verifier_instance)

    def remove_aid_to_verifier_mapping(self, aid: str) -> None:
        """
        Remove a single AID-to-verifier mapping from Redis (DB 1).
        """
        self.aid_to_verifier_mapping.delete(aid)
        logger.info(f"Removed AID-to-verifier mapping: {aid}")

    def get_verifier_instance_for_aid(self, aid: str) -> str:
        """
        Get a verifier instance for the given AID. If no mapping exists, assign a random instance.
        """
        verifier_instance = self.aid_to_verifier_mapping.get(aid)
        if verifier_instance:
            logger.debug(f"Found existing verifier instance for AID: {aid}")
            return verifier_instance.decode("utf-8")

        logger.debug(f"No verifier instance mapped for AID: {aid}. Assigning a random instance.")
        return self._get_next_verifier_instance()

    def get_verifier_instance_for_said(self, said: str) -> str:
        """
        Get a random verifier instance for the given SAID.
        """
        logger.debug(f"Getting random verifier instance for SAID: {said}")
        return self._get_next_verifier_instance()

    def _get_next_verifier_instance(self) -> str:
        """
        Helper method to get a random verifier instance using round-robin.
        """
        verifier_instances = self.get_verifier_instances()
        if not verifier_instances:
            logger.error("No verifier instances available.")
            raise ValueError("No verifier instances available.")

        # Round-robin selection
        if self._current_verifier_instance_num >= len(verifier_instances):
            self._current_verifier_instance_num = 0
        instance = verifier_instances[self._current_verifier_instance_num]
        self._current_verifier_instance_num += 1
        logger.debug(f"Selected verifier instance: {instance}")
        return instance
