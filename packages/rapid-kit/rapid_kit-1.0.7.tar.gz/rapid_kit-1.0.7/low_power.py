#!/usr/bin/env python3

import os
import sys
import json
import time
import rapid_kit
from rapid_kit.log import upload_logging
from rapid_kit.http import http_post

DEVICE_ID = "3D3Y3ZG3KY55"
APP_ID = "5920020"
PACKAGE_NAME = "com.tange365.icam365"
ACCESS_TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6Im8xWnkzWE5TSGhxOCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjMwODI0IiwiaXNzIjoiYXBwL2xvZ2luIiwiaWF0IjoxNzQ3MTQ3NDAyLCJleHAiOjE3NDc3NTIyMDIsImF1ZCI6WyJhcHAvYmFja2VuZCJdLCJ1aWQiOjE2MzA4MjQsImFwcF9pZCI6IjU5MjAwMjAifQ._yQ9Gh9v3cCWPakI6Fm5KTJVlh0t07lC5P0l48lRCBBPbI70BVLkzMWdvpILgCuVhNrPFqKyPxD0iTSO1PAkBw"
USER_ACCOUNT = "13810929428"
USER_PASSWORD = "10929422"

CONSOLE_LOGGING = True
total_tests = 3
test_interval = 10  # seconds
dormant_check_interval = 30  # seconds

def main():
    print("=== Low Power Device Wake-up Test ===")
    print("=== 1. Initializing SDK ===")
    
    success = rapid_kit.initialize(
        app_id=APP_ID,
        package_name=PACKAGE_NAME,
        console_logging=CONSOLE_LOGGING
    )
    
    if not success:
        print("Error: SDK initialization failed")
        sys.exit(1)
    
    print("SDK initialized successfully")
    print(f"  |__ Version: {rapid_kit.version_name()}")
    print(f"  |__ Build ID: {rapid_kit.build_id()}")
    print(f"  |__ Commit Hash: {rapid_kit.commit_hash()}")

    print("\n=== 2. Authentication ===")
    
    access_token = ACCESS_TOKEN
    if USER_ACCOUNT and USER_PASSWORD.strip():
        print(f"Logging in with account: {USER_ACCOUNT}")
        login_result = rapid_kit.http_post(
            path="/v2/user/login",
            content=f'{{"username": "{USER_ACCOUNT}", "pwd": "{USER_PASSWORD}", "area_code": "86"}}'
        )

        if not login_result or not login_result["success"]:
            error_message = login_result["message"] if login_result else "Unknown error"
            error_code = login_result["code"] if login_result else -1
            print(f"Error: Login failed: {error_message} (code: {error_code})")
            sys.exit(1)

        data = json.loads(login_result["data"])
        access_token = data["access_token"]
        print(f"Login successful, received access token")
    else:
        print("Using provided access token")

    auth_result = rapid_kit.authenticate(access_token)
    if not auth_result or not auth_result["success"]:
        error_message = auth_result["message"] if auth_result else "Unknown error"
        error_code = auth_result["code"] if auth_result else -1
        print(f"Error: Authentication failed: {error_message} (code: {error_code})")
        sys.exit(1)
    
    print("Authentication successful")

    print("\n=== 3. Low Power Device Wake-up Loop Test ===")
    
    test_results = []


    for test_index in range(total_tests):
        print(f"\n--- Test {test_index + 1}/{total_tests} ---")
        
        print("Checking device dormant status...")
        
        while True:
            # Ensure device is in dormant state
            online_result = http_post(
                path="/v2/device/online",
                content=f'{{"device_id": "{DEVICE_ID}"}}'
            )
            
            if not online_result or not online_result.get('success'):
                print("Failed to get device online status, will retry later ...")
                sys.exit(1)
            
            try:
                data_str = online_result.get('data', '{}')
                data = json.loads(data_str)
                device_info = data.get(DEVICE_ID, {})
                            
                dormant_status = device_info.get('dormant_status')
                is_online = device_info.get('is_online', False)
                
                if dormant_status is None or dormant_status == {}:
                    print("Detected regular power device, checking online status...")
                    if not is_online:
                        print("Regular power device is not online, cannot proceed with test")
                        sys.exit(1)
                    else:
                        print("Regular power device is online, ready for test")
                        break
                else:
                    is_alive = dormant_status.get('is_alive', False)
                    print(f"Detected low power device, dormant alive status: {is_alive}")
                    
                    if is_alive:
                        print("Low power device is in dormant state, ready ^_^")
                        break
                    else:
                        print("Low power device is not in dormant state, waiting ...")
                        time.sleep(dormant_check_interval)
                        continue
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing device status: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"Error checking device status: {e}")
                sys.exit(1)
        
        player_started = False
        start_time = None
        end_time = None
        
        def on_status_change(state):
            state_name = rapid_kit.PipeState(state).name
            print(f"Connection status: {state_name}")
            
            if state in [rapid_kit.PipeState.FAILED, rapid_kit.PipeState.BROKEN, 
                         rapid_kit.PipeState.SHUTDOWN_BY_REMOTE, rapid_kit.PipeState.TOKEN_NOT_AVAILABLE]:
                print(f"Connection failed: {state_name}")
                return
        
        pipe = rapid_kit.Pipe(DEVICE_ID)
        pipe.listen(on_status_change)
        
        live_stream = rapid_kit.LiveStream(pipe)
        live_stream.switch_high_quality()
        player = rapid_kit.MediaPlayer()
        
        player.prepare(live_stream.provider())
        player.set_aout(rapid_kit.create_silence_aout())
        player.set_vout(rapid_kit.create_silence_vout())
        player.start()
        live_stream.start()
        
        print("Triggering connection and starting timing...")
        start_time = time.time()
        pipe.establish()
        
        test_timeout = 50  # seconds
        test_start_time = time.time()
        
        while time.time() - test_start_time < test_timeout:
            current_state = player.state()
            state_name = rapid_kit.MediaRenderState(current_state).name
          
            if current_state == rapid_kit.MediaRenderState.STARTED:
                player_started = True
                end_time = time.time()
                print("Player started successfully")
                break
                
            time.sleep(0.05)
        
        duration = end_time - start_time if end_time and start_time else None
        
        if player_started and duration is not None:
            print(f"Test {test_index + 1} completed successfully in {duration:.2f} seconds")
            test_results.append({
                'test_index': test_index + 1,
                'success': True,
                'duration': duration,
                'error': None
            })
        else:
            error_msg = f"Player failed to start after {test_timeout} seconds"
            print(f"Test {test_index + 1} failed: {error_msg}")
            test_results.append({
                'test_index': test_index + 1,
                'success': False,
                'duration': None,
                'error': error_msg
            })
        
        print("Cleaning up resources...")
        player.stop()
        live_stream.stop()
        pipe.abolish()
        
        if test_index < total_tests - 1:
            print(f"Waiting {test_interval} seconds before next test...")
            time.sleep(test_interval)
    
    print("\n=== Test Results Summary ===")
    successful_tests = [r for r in test_results if r['success']]
    failed_tests = [r for r in test_results if not r['success']]
    
    print(f"Total tests: {total_tests}")
    print(f"Successful tests: {len(successful_tests)}")
    print(f"Failed tests: {len(failed_tests)}")
    print(f"Success rate: {len(successful_tests)/total_tests*100:.1f}%")
    
    if successful_tests:
        durations = [r['duration'] for r in successful_tests]
        print(f"\nTiming statistics:")
        print(f"Average duration: {sum(durations)/len(durations):.2f} seconds")
        print(f"Minimum duration: {min(durations):.2f} seconds")
        print(f"Maximum duration: {max(durations):.2f} seconds")
        
        print(f"\nDetailed results:")
        for result in successful_tests:
            print(f"  Test {result['test_index']}: {result['duration']:.2f}s")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for result in failed_tests:
            print(f"  Test {result['test_index']}: {result['error']}")
    
    print("\n=== Uploading Logs ===")
    try:
        log_result = upload_logging()
        if log_result:
            print(f"Log upload successful: {log_result}")
        else:
            print("Log upload returned no data")
    except Exception as e:
        print(f"Log upload failed: {e}")
    
    print("\n=== Low Power Device Wake-up Test Completed ===")

if __name__ == "__main__":
    main() 