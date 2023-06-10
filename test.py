import time
import os
import sys
import pytest
import subprocess

# Add the project root directory to the system path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from client.client import Client

TEST_PPT_PATH = "/Users/damiantissembaum/Documents/year_3/TEMP/Tests-3.pptx"
API_PROCESS = None


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_system():
    # Start up the API and explainer
    api_process_1 = subprocess.Popen(['python', 'flaskServer/main.py'])
    api_process_2 = subprocess.Popen(['python', 'explainer/Explainer.py'])

    time.sleep(5)  # or however long they need to be ready
    yield

    if api_process_1 is not None:
        api_process_1.terminate()
        api_process_1 = None
        print("API process stopped")

    if api_process_2 is not None:
        api_process_2.terminate()
        api_process_2 = None
        print("explainer process stopped")


def test_end_to_end():
    # Step 1: Create client
    client = Client()

    # Step 2: Upload a presentation
    uid = client.upload_file(TEST_PPT_PATH)
    assert uid is not None

    # Step 3: Check the status
    status = None  # Declare the status variable outside the loop
    for _ in range(60):
        status = client.get_status(uid)
        if status.is_done():
            break
        time.sleep(2)

    # Check that the status is done
    assert status is not None  # Verify that status is assigned
    assert status.status == 'done'


if __name__ == '__main__':
    pytest.main()
