import random
import time
def call_api(url):
    """
    Simulate calling an API.
    This function may raise errors randomly.
    """
    r = random.random()
    if r < 0.4:
        raise TimeoutError("Timeout")
    elif r < 0.7:
        raise ConnectionError("Connection failed")
    else:
        return {
            "status": 200,
            "data": "OK",
            "url": url
        }
def call_api_with_retry(url, max_retries=3, delay=1, backoff=2):
    """
    Call API with retry mechanism.
    Args:
        url (str): API endpoint.
        max_retries (int): Maximum number of retry attempts.
        delay (float): Base delay time in seconds.
        backoff (float): Multiplier to increase delay after each failed attempt.

    Returns:
        dict: API response if successful.

    Raises:
        Exception: Last exception if all retries fail.
    """
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if delay < 0:
        raise ValueError("delay must be non-negative")

    if backoff < 1:
        raise ValueError("backoff must be greater than or equal to 1")

    retryable_errors = (TimeoutError, ConnectionError)

    for attempt in range(max_retries + 1):
        try:
            print(f"[ATTEMPT] Calling API, attempt {attempt + 1}/{max_retries + 1}")

            response = call_api(url)

            print("[SUCCESS] API call successful")
            return response

        except retryable_errors as error:
            print(f"[ERROR] {type(error).__name__}: {error}")

            if attempt == max_retries:
                print("[FAILED] Max retries reached")
                raise

            wait_time = delay * (backoff ** attempt)

            print(f"[RETRY] Waiting {wait_time} seconds before next retry...")
            time.sleep(wait_time)

        except Exception as error:
            print(f"[NON-RETRYABLE ERROR] {type(error).__name__}: {error}")
            raise
def main():
    url = ""

    try:
        result = call_api_with_retry(
            url=url,
            max_retries=3,
            delay=1,
            backoff=2
        )

        print("\nFinal result:")
        print(result)

    except Exception as error:
        print("\nAPI call failed after retries.")
        print(f"Final error: {error}")


if __name__ == "__main__":
    main()