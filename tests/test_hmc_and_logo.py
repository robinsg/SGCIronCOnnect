# tests/test_hmc_and_logo.py

import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
sys.path.append(os.getcwd())

from framework.libraries.IBMiLibrary import IBMiLibrary
from framework.core.terminal_driver import TmuxDriver

def test_hmc_and_logo():
    print("--- Testing HMC and Logo Keywords ---")

    lib = IBMiLibrary()

    # Mock the TmuxDriver
    mock_driver = MagicMock(spec=TmuxDriver)

    # Mock screens
    hmc_login_buffer = [
        "                                                                                ",
        "         Hardware Management Console                                            ",
        "                                                                                ",
        "         Login                                                                  ",
        "                                                                                ",
        "         User:                                                                  ",
        "         Password:                                                              ",
        "                                                                                ",
        "                                                                                "
    ]

    logo_buffer = [
        "           _              _                                                     ",
        "          | |            | |                                                    ",
        "     _ __ | |__   ___  __| |                                                    ",
        "    | '__|| '_ \\ / _ \\/ _` |                                                    ",
        "    | |   | |_) | (_) \\ (_| |                                                    ",
        "    |_|   |_.__/ \\___/ \\__,_|                                                    ",
        "                                                                                ",
        "      ROBOT FRAMEWORK                                                           ",
        "                                                                                "
    ]

    with patch('framework.core.p5250_client.TmuxDriver', return_value=mock_driver):
        # Test 1: Connect to LPAR via HMC
        print("Testing: connect_to_lpar_via_hmc")
        mock_driver.get_buffer.return_value = hmc_login_buffer
        mock_driver.is_input_inhibited.return_value = False
        mock_driver.get_dimensions.return_value = (80, 24)

        lib.connect_to_lpar_via_hmc("hmc_host", "user", "pass", "PART01")

        # Verify that initialize_connection was called with partition_name as lu_name
        assert lib.client.lu_name == "PART01"
        print("✓ HMC login successful (mocked)")

        # Test 2: Verify Robot Framework Logo
        print("Testing: verify_robot_framework_logo")
        mock_driver.get_buffer.return_value = logo_buffer

        lib.verify_robot_framework_logo()
        print("✓ Logo verification successful (mocked)")

    print("--- All Tests Passed ---")

if __name__ == "__main__":
    try:
        test_hmc_and_logo()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
