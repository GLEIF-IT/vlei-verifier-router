import logging
from vlei_verifier_client import VerifierClient, VerifierResponse
from utils.router_state import RouterState

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class VerifierController:
    @staticmethod
    def _get_verifier_client(aid: str = None, said: str = None) -> VerifierClient:
        """
        Helper method to get a VerifierClient instance for the given AID or SAID.
        """
        router_state = RouterState.get_state()
        if aid:
            logger.debug(f"Getting verifier instance for AID: {aid}")
            verifier_base_url = router_state.get_verifier_instance_for_aid(aid)
        elif said:
            logger.debug(f"Getting verifier instance for SAID: {said}")
            verifier_base_url = router_state.get_verifier_instance_for_said(said)
        else:
            logger.error("Either `aid` or `said` must be provided.")
            raise ValueError("Either `aid` or `said` must be provided.")
        logger.info(f"Using verifier instance: {verifier_base_url}")
        return VerifierClient(verifier_base_url)

    @staticmethod
    def presentation(said: str, vlei: str) -> VerifierResponse:
        """
        Handle presentation logic for a given SAID and VLEI.
        """
        logger.info(f"Starting presentation for SAID: {said}")
        verifier_client = VerifierController._get_verifier_client(said=said)
        verifier_response = verifier_client.login(said=said, vlei=vlei)

        if verifier_response.code >= 300:
            logger.warning(f"Presentation failed for SAID: {said}. Code: {verifier_response.code}, Message: {verifier_response.message}")
            return VerifierResponse(code=verifier_response.code, message=verifier_response.message, body=verifier_response.body)

        # Map the verifier instance to the AID
        aid = verifier_response.body["aid"]
        RouterState.get_state().add_aid_to_verifier_mapping(aid, verifier_client.verifier_base_url)
        logger.info(f"Presentation successful for SAID: {said}. Mapped to AID: {aid}")
        return verifier_response

    @staticmethod
    def authorization(aid: str) -> VerifierResponse:
        """
        Handle authorization logic for a given AID.
        """
        logger.info(f"Starting authorization for AID: {aid}")
        verifier_client = VerifierController._get_verifier_client(aid=aid)
        verifier_response = verifier_client.check_login(aid=aid)

        if verifier_response.code >= 300:
            logger.warning(f"Authorization failed for AID: {aid}. Code: {verifier_response.code}, Message: {verifier_response.message}")
        else:
            logger.info(f"Authorization successful for AID: {aid}")

        return verifier_response

    @staticmethod
    def signed_headers_verification(aid: str, sig: str, ser: str) -> VerifierResponse:
        """
        Handle signed headers verification for a given AID, signature, and serialized data.
        """
        logger.info(f"Starting signed headers verification for AID: {aid}")
        verifier_client = VerifierController._get_verifier_client(aid=aid)
        verifier_response = verifier_client.verify_signed_headers(aid=aid, sig=sig, ser=ser)

        if verifier_response.code >= 300:
            logger.warning(f"Signed headers verification failed for AID: {aid}. Code: {verifier_response.code}, Message: {verifier_response.message}")
        else:
            logger.info(f"Signed headers verification successful for AID: {aid}")

        return verifier_response

    @staticmethod
    def signature_verification(aid: str, sig: str, digest: str) -> VerifierResponse:
        """
        Handle signature verification for a given AID, signature, and digest.
        """
        logger.info(f"Starting signature verification for AID: {aid}")
        verifier_client = VerifierController._get_verifier_client(aid=aid)
        verifier_response = verifier_client.verify_signature(signature=sig, signer_aid=aid, non_prefixed_digest=digest)

        if verifier_response.code >= 300:
            logger.warning(f"Signature verification failed for AID: {aid}. Code: {verifier_response.code}, Message: {verifier_response.message}")
        else:
            logger.info(f"Signature verification successful for AID: {aid}")

        return verifier_response

    @staticmethod
    def add_root_of_trust(aid: str, vlei: str, oobi: str) -> VerifierResponse:
        """
        Add a root of trust to all verifier instances for a given AID, VLEI, and OOBI.
        """
        logger.info(f"Adding root of trust for AID: {aid}")
        router_state = RouterState.get_state()
        verifier_responses = []

        for verifier_base_url in router_state.get_verifier_instances():
            logger.debug(f"Adding root of trust to verifier instance: {verifier_base_url}")
            verifier_client = VerifierClient(verifier_base_url)
            verifier_response = verifier_client.add_root_of_trust(aid, vlei, oobi)
            verifier_responses.append(verifier_response)

        last_response = verifier_responses[-1]
        if last_response.code >= 300:
            logger.warning(f"Failed to add root of trust for AID: {aid}. Code: {last_response.code}, Message: {last_response.message}")
        else:
            logger.info(f"Root of trust added successfully for AID: {aid}")

        return last_response