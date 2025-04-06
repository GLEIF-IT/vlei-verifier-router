import json
import os
import time
import asyncio
from typing import List

from vlei_verifier_client import VerifierClient, VerifierResponse, AsyncVerifierClient
successful_requests = 0
failed_requests = 0
total_latency = 0

async def send_post_request(aid, said, vlei):
    try:
        client = AsyncVerifierClient("http://localhost:7676")
        start_time = time.perf_counter()

        presentations_response: VerifierResponse = await client.presentation(said, vlei)
        auth_response: VerifierResponse = await client.authorization(aid)

        end_time = time.perf_counter()
        latency = end_time - start_time

        return {
            "success": presentations_response.code == 202,
            "response": auth_response.body,
            "latency": latency
        }

    except Exception as e:
        return {"error": f"Failed to send POST request: {e}"}

# Extract credential data from JSON
def extract_cred_data(data):
    try:
        aid = data["credential"]["raw"]["sad"]["a"]["i"]
        said = data["credential"]["raw"]["sad"]["d"]
        vlei = data["credential"]["cesr"]

        return {
            "aid": aid,
            "said": said,
            "vlei": vlei
        }
    except KeyError as e:
        return {"error": f"Key not found in the data: {e}"}

# Semaphore wrapper for concurrency limiting
async def post_with_semaphore(semaphore, aid, said, vlei):
    async with semaphore:
        return await send_post_request(aid, said, vlei)

# The main load testing function
async def load_test():
    global successful_requests, failed_requests, total_latency

    folder_path = os.path.join(os.path.dirname(__file__), "test_data")
    credentials_files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    total_requests = 0
    tasks: List[asyncio.Task] = []

    # Define concurrency limit
    concurrency_limit = 50
    semaphore = asyncio.Semaphore(concurrency_limit)

    print(f"Starting load test with {concurrency_limit} concurrent requests...")

    start_time = time.perf_counter()

    # Iterate over all credential files and create tasks
    for cred_file in credentials_files:
        cred_path = os.path.join(folder_path, cred_file)
        with open(cred_path, "r") as f:
            data = json.load(f)
            cred_data = extract_cred_data(data)

            # If there was a problem extracting, skip
            if "error" in cred_data:
                print(f"Error in credential file {cred_file}: {cred_data['error']}")
                continue

            # Submit amount of requests per credential
            for _ in range(20):
                task = asyncio.create_task(
                    post_with_semaphore(
                        semaphore,
                        aid=cred_data["aid"],
                        said=cred_data["said"],
                        vlei=cred_data["vlei"]
                    )
                )
                tasks.append(task)
                total_requests += 1

    print(f"Total tasks queued: {total_requests}")

    # Process tasks as they complete
    for coro in asyncio.as_completed(tasks):
        result = await coro

        if "error" in result or not result.get("success", False):
            failed_requests += 1
        else:
            successful_requests += 1
            total_latency += result.get("latency", 0)

        print("POST Request Result:", result)

    end_time = time.perf_counter()

    # Metrics calculation
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
    average_response_time = total_latency / successful_requests if successful_requests > 0 else 0
    throughput = total_requests / (end_time - start_time) if (end_time - start_time) > 0 else 0

    # Final results
    print("\n=== Load Test Metrics ===")
    print(f"Total Requests: {total_requests}")
    print(f"Average Response Time: {average_response_time:.4f} seconds")
    print(f"Throughput: {throughput:.2f} requests/second")
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(load_test())
