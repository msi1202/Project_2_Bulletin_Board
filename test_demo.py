#!/usr/bin/env python3
"""
Simple test script to demonstrate the bulletin board system functionality
"""

import socket
import json
import time
import threading


def test_client(username, port=8888):
    """Test client function"""
    try:
        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", port))

        # Register
        request = {"command": "REGISTER", "username": username}
        sock.send(json.dumps(request).encode('utf-8'))
        response = json.loads(sock.recv(4096).decode('utf-8'))
        print(f"[{username}] {response.get('message')}")

        if response.get("status") != "SUCCESS":
            sock.close()
            return

        # Join public group
        request = {"command": "JOIN"}
        sock.send(json.dumps(request).encode('utf-8'))
        response = json.loads(sock.recv(4096).decode('utf-8'))
        print(f"[{username}] Joined public group. Users: {response.get('users')}")

        # Post a message
        time.sleep(1)
        request = {
            "command": "POST",
            "subject": f"Hello from {username}",
            "content": f"This is a test message from {username}!"
        }
        sock.send(json.dumps(request).encode('utf-8'))
        response = json.loads(sock.recv(4096).decode('utf-8'))
        print(f"[{username}] Posted message ID: {response.get('msg_id')}")

        # Keep connection alive for a bit
        time.sleep(3)

        # Leave
        request = {"command": "LEAVE"}
        sock.send(json.dumps(request).encode('utf-8'))
        response = json.loads(sock.recv(4096).decode('utf-8'))
        print(f"[{username}] {response.get('message')}")

        sock.close()

    except Exception as e:
        print(f"[{username}] Error: {e}")


def main():
    """Main test function"""
    print("="*60)
    print("Bulletin Board System - Test Demo")
    print("="*60)
    print("\nMake sure the server is running on port 8888")
    print("Press Ctrl+C to stop\n")

    try:
        # Start multiple test clients
        threads = []
        usernames = ["Alice", "Bob", "Charlie"]

        for username in usernames:
            t = threading.Thread(target=test_client, args=(username,))
            t.start()
            threads.append(t)
            time.sleep(0.5)  # Stagger client connections

        # Wait for all threads
        for t in threads:
            t.join()

        print("\n" + "="*60)
        print("Test completed successfully!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")


if __name__ == "__main__":
    main()
