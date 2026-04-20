# demo.py

from framework.core.terminal_driver import TmuxDriver
from framework.core.base_screen import BaseScreen
from framework.core.handler_registry import HandlerRegistry

def run_demo():
    print("--- IronConnect Framework Demo ---")
    
    # In a real environment, this would launch tmux and tn5250
    # For demo purposes, we'll mock the driver's buffer
    class MockTmuxDriver(TmuxDriver):
        def start_session(self):
            print("Mock: Starting tn5250 session...")
            
        def get_buffer(self):
            return [
                "                                Order Entry - Main                              ",
                " Order # 12345678                                                               ",
                "                                                                                ",
                " Customer ID: CUST001                                                           ",
                "                                                                                ",
                " Items:                                                                         ",
                "   1. Widget A                                                                  ",
                "   2. Widget B                                                                  ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                "                                                  Total:      1234.56           ",
                "                                                                                ",
                "                                                                                ",
                "                                                                                ",
                " System Ready                                                                   "
            ]
        
        def is_input_inhibited(self):
            return False
            
        def get_dimensions(self):
            return (80, 24)

    print("Initialising Mock Driver...")
    driver = MockTmuxDriver()
    driver.start_session()

    print("Loading Order Entry Screen with Handlers...")
    # Using the YAML we created earlier
    try:
        screen = BaseScreen(driver, "framework/config/order_processing_screen.yaml", "order_entry_main")
        
        print("Verifying Sign On...")
        # (Simulated login logic here)
        
        print("Checking for optional Sign-on Information screen...")
        # Specific handler for optional info screen
        info_screen = BaseScreen(driver, "framework/config/signon_info_screen.yaml", "signon_info")
        if info_screen.matches():
            print("Optional 'Sign-on Information' screen detected. Sending 'Enter' to bypass.")
            driver.send_keys("Enter")
        else:
            print("Sign-on Information screen not present, skipping.")
            
        print("Verifying Main Order Entry Screen...")
        screen.verify()  # This runs the indicators and executes the handlers
        
        print("Verification Successful!")
        
        # Check handler results
        total_result = screen.get_handler_result("extract_total")
        if total_result and total_result.get('success'):
            print(f"Extracted Order Total: £{total_result['value']:.2f}")
        
        error_result = screen.get_handler_result("find_error")
        if error_result and error_result.get('found'):
            print(f"Warning: Found text '{error_result['matched_text']}' at Row {error_result['row']}")
        else:
            print("No errors found in status area.")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    run_demo()
