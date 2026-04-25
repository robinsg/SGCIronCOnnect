# tests/test_hmc_and_logo.py

import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
sys.path.append(os.getcwd())

from framework.libraries.IBMiLibrary import IBMiLibrary
from framework.core.terminal_driver import TmuxDriver

def test_hmc_and_logo():
    print("--- Testing Full HMC Sequence and Logo Keywords ---")

    lib = IBMiLibrary()

    # Mock the TmuxDriver
    mock_driver = MagicMock(spec=TmuxDriver)

    # Screens based on the provided text screenshots
    screens = {
        "language": ["Welcome to Remote 5250 Console", "Select one of the following and press Enter", "Language: 23"],
        "login": ["Remote 5250 Console Sign on", "Enter your management console userid and password", "User:", "grobinson"],
        "system": ["Remote 5250 Console System Selection", "System: 1"],
        "partition": ["Remote 5250 Console Partition Selection", "10: F4I400X"],
        "session_key": ["Remote 5250 Console Session Key", "A session key is required", "Enter your session key:"],
        "logo": ["ROBOT FRAMEWORK"]
    }

    with patch('framework.core.p5250_client.TmuxDriver', return_value=mock_driver):
        mock_driver.is_input_inhibited.return_value = False
        mock_driver.get_dimensions.return_value = (80, 24)

        # Test: Full HMC Connection Sequence
        print("Testing: connect_to_lpar_via_hmc (Full Sequence)")

        # side_effect for get_buffer to handle ALL calls during the sequence
        # We'll just return the correct screen based on the current context
        current_context = ["language"]
        def get_buffer_side_effect():
            return screens[current_context[0]]

        mock_driver.get_buffer.side_effect = get_buffer_side_effect

        # We need to hook into _switch_to to update the current_context
        from framework.screens.hmc_console_screen import HMCConsoleScreen
        original_switch_to = HMCConsoleScreen._switch_to
        def patched_switch_to(self, screen_key):
            if screen_key == "hmc_login": current_context[0] = "login"
            elif screen_key == "hmc_system_selection": current_context[0] = "system"
            elif screen_key == "hmc_partition_selection": current_context[0] = "partition"
            elif screen_key == "hmc_session_key": current_context[0] = "session_key"
            return original_switch_to(self, screen_key)

        with patch('framework.screens.hmc_console_screen.HMCConsoleScreen._switch_to', patched_switch_to):
            lib.connect_to_lpar_via_hmc(
                hmc_host="wat-hmc-cr2",
                hmc_user="grobinson",
                hmc_password="password",
                partition_name="10",
                session_key="secret"
            )

        print("✓ Full HMC sequence successful (mocked)")

        # Test: Verify Robot Framework Logo
        print("Testing: verify_robot_framework_logo")
        mock_driver.get_buffer.side_effect = None
        mock_driver.get_buffer.return_value = ["ROBOT FRAMEWORK"]

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
