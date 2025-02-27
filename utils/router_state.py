from dataclasses import dataclass, field
import random
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouterState:
    """
    Singleton class to manage verifier instances and their mappings to AIDs.
    """
    verifier_instances: List[str] = field(default_factory=list)
    aid_to_verifier_instances_mapping: Dict[str, str] = field(default_factory=dict)

    _instance: "RouterState" = None

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
        logger.info("RouterState initialized successfully.")

    @classmethod
    def initialize(cls, **kwargs) -> "RouterState":
        """
        Initialize the singleton instance with custom arguments. Can only be called once.
        """
        if cls._instance is None:
            logger.debug("Initializing RouterState with custom arguments.")
            cls._instance = cls(**kwargs)
        else:
            logger.warning("RouterState is already initialized. Returning existing instance.")
        return cls._instance

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

    def get_verifier_instance_for_aid(self, aid: str) -> str:
        """
        Get a verifier instance for the given AID. If no mapping exists, assign a random instance.
        """
        if aid in self.aid_to_verifier_instances_mapping:
            logger.debug(f"Found existing verifier instance for AID: {aid}")
            return self.aid_to_verifier_instances_mapping[aid]

        logger.debug(f"No verifier instance mapped for AID: {aid}. Assigning a random instance.")
        return self._get_random_verifier_instance()

    def get_verifier_instance_for_said(self, said: str) -> str:
        """
        Get a random verifier instance for the given SAID.
        """
        logger.debug(f"Getting random verifier instance for SAID: {said}")
        return self._get_random_verifier_instance()

    def set_verifier_instance_for_aid(self, aid: str, verifier_instance: str) -> None:
        """
        Map a verifier instance to the given AID.
        """
        logger.info(f"Mapping verifier instance {verifier_instance} to AID: {aid}")
        self.aid_to_verifier_instances_mapping[aid] = verifier_instance

    def _get_random_verifier_instance(self) -> str:
        """
        Helper method to get a random verifier instance.
        """
        if not self.verifier_instances:
            logger.error("No verifier instances available.")
            raise ValueError("No verifier instances available.")

        instance = random.choice(self.verifier_instances)
        logger.debug(f"Selected random verifier instance: {instance}")
        return instance