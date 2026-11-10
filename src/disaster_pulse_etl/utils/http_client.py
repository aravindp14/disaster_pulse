import time
import requests

from disaster_pulse_etl.utils.logger import get_logger

logger = get_logger(__name__)

RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]

def get_with_retry(
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int = 30,
        max_attempts: int = 3
) -> requests.Response:
    """
    Perform a GET request with retry logic for specific status codes.

    Args:
        url (str): The URL to send the GET request to.
        params (dict | None): Optional query parameters to include in the request.
        headers (dict | None): Optional headers to include in the request.
        timeout (int): The timeout for the request in seconds. Default is 30 seconds.
        max_attempts (int): The maximum number of attempts for the request. Default is 3.

    Returns:
        requests.Response: The response object from the successful GET request.

    Raises:
        requests.exceptions.RequestException: If all attempts fail, the last exception will be raised.
    """

    if max_attempts <1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )

            response.raise_for_status()
            return response

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError
        ) as exc:

            if isinstance(exc, requests.exceptions.HTTPError):
                status_code = exc.response.status_code

                if status_code not in RETRYABLE_STATUS_CODES:
                    logger.error(
                        f"HTTP error occurred: {exc}. Status code: {status_code}. Not retrying."
                    )
                    raise

            if attempt == max_attempts:
                logger.error(
                    "HTTP request failed after %d attempts. Raising exception: %s", max_attempts,url
                )

                raise

            delay = 2 ** attempt

            logger.warning(
                "HTTP request failed (attempt %d/%d). Retrying in %d seconds. Error: %s",
                attempt,max_attempts,delay,exc
            )

            time.sleep(delay)
