#!/usr/bin/env python3
"""
Bulletin Board Client
A client implementation for connecting to the bulletin board server
and interacting with the message board system.
"""

import socket
import json
import threading
import sys


class BulletinBoardClient:
    """Main bulletin board client class"""

    def __init__(self):
        self.socket = None
        self.username = None
        self.connected = False
        self.running = True

    def connect(self, host: str, port: int, username: str):
        """Connect to the bulletin board server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.username = username

            # Register with the server
            request = {
                "command": "REGISTER",
                "username": username
            }
            self.socket.send(json.dumps(request).encode('utf-8'))

            # Wait for response
            response = self._receive_response()

            if response.get("status") == "SUCCESS":
                self.connected = True
                print(f"\n{response.get('message')}")
                print("Type 'help' for a list of available commands.\n")

                # Start listening for notifications in a separate thread
                listener_thread = threading.Thread(target=self._listen_for_notifications)
                listener_thread.daemon = True
                listener_thread.start()

                return True
            else:
                print(f"\nError: {response.get('message')}")
                self.socket.close()
                return False

        except Exception as e:
            print(f"\nError connecting to server: {e}")
            return False

    def _receive_response(self):
        """Receive a response from the server"""
        try:
            data = self.socket.recv(4096).decode('utf-8')
            return json.loads(data)
        except Exception as e:
            print(f"\nError receiving response: {e}")
            return {"status": "ERROR", "message": "Connection error"}

    def _listen_for_notifications(self):
        """Listen for notifications from the server"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                message = json.loads(data)

                if message.get("type") == "NOTIFICATION":
                    print(f"\n[NOTIFICATION] {message.get('message')}")
                    print(f"{self.username}> ", end="", flush=True)

            except Exception as e:
                if self.running:
                    print(f"\nConnection to server lost: {e}")
                    self.connected = False
                break

    def send_command(self, command: str, **kwargs):
        """Send a command to the server"""
        if not self.connected:
            print("Error: Not connected to server. Use %connect first.")
            return

        request = {"command": command, **kwargs}

        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self._receive_response()
            return response
        except Exception as e:
            print(f"Error sending command: {e}")
            return {"status": "ERROR", "message": "Connection error"}

    def cmd_join(self, args):
        """Join the public message board"""
        response = self.send_command("JOIN")

        if response.get("status") == "SUCCESS":
            print(f"\n{response.get('message')}")
            print("\nUsers in this group:")
            for user in response.get("users", []):
                print(f"  - {user}")

            recent_messages = response.get("recent_messages", [])
            if recent_messages:
                print("\nRecent messages:")
                for msg in recent_messages:
                    print(f"  {msg}")
            else:
                print("\nNo recent messages.")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_post(self, args):
        """Post a message to the public board"""
        if len(args) < 2:
            print("Usage: %post <subject> <message content>")
            return

        subject = args[0]
        content = " ".join(args[1:])

        response = self.send_command("POST", subject=subject, content=content)

        if response.get("status") == "SUCCESS":
            print(f"\nMessage posted successfully (ID: {response.get('msg_id')})")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_users(self, args):
        """Retrieve list of users in the public group"""
        response = self.send_command("USERS")

        if response.get("status") == "SUCCESS":
            users = response.get("users", [])
            print(f"\nUsers in public group ({len(users)} total):")
            for user in users:
                print(f"  - {user}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_leave(self, args):
        """Leave the public group"""
        response = self.send_command("LEAVE")

        if response.get("status") == "SUCCESS":
            print(f"\n{response.get('message')}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_message(self, args):
        """Retrieve a message by ID"""
        if len(args) < 1:
            print("Usage: %message <message_id>")
            return

        try:
            msg_id = int(args[0])
        except ValueError:
            print("Error: Message ID must be a number")
            return

        response = self.send_command("MESSAGE", msg_id=msg_id)

        if response.get("status") == "SUCCESS":
            msg = response.get("message")
            print(f"\n{'='*60}")
            print(f"Message ID: {msg['msg_id']}")
            print(f"Sender: {msg['sender']}")
            print(f"Date: {msg['post_date']}")
            print(f"Subject: {msg['subject']}")
            print(f"{'-'*60}")
            print(f"{msg['content']}")
            print(f"{'='*60}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_groups(self, args):
        """Retrieve list of all available groups"""
        response = self.send_command("GROUPS")

        if response.get("status") == "SUCCESS":
            groups = response.get("groups", [])
            print(f"\nAvailable groups ({len(groups)} total):")
            print(f"{'ID':<15} {'Name':<30} {'Members':<10}")
            print(f"{'-'*55}")
            for group in groups:
                print(f"{group['group_id']:<15} {group['name']:<30} {group['member_count']:<10}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_groupjoin(self, args):
        """Join a specific group"""
        if len(args) < 1:
            print("Usage: %groupjoin <group_id>")
            return

        group_id = args[0]
        response = self.send_command("GROUPJOIN", group_id=group_id)

        if response.get("status") == "SUCCESS":
            print(f"\n{response.get('message')}")
            print("\nUsers in this group:")
            for user in response.get("users", []):
                print(f"  - {user}")

            recent_messages = response.get("recent_messages", [])
            if recent_messages:
                print("\nRecent messages:")
                for msg in recent_messages:
                    print(f"  {msg}")
            else:
                print("\nNo recent messages.")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_grouppost(self, args):
        """Post a message to a specific group"""
        if len(args) < 3:
            print("Usage: %grouppost <group_id> <subject> <message content>")
            return

        group_id = args[0]
        subject = args[1]
        content = " ".join(args[2:])

        response = self.send_command("GROUPPOST", group_id=group_id, subject=subject, content=content)

        if response.get("status") == "SUCCESS":
            print(f"\nMessage posted successfully to group '{group_id}' (ID: {response.get('msg_id')})")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_groupusers(self, args):
        """Retrieve list of users in a specific group"""
        if len(args) < 1:
            print("Usage: %groupusers <group_id>")
            return

        group_id = args[0]
        response = self.send_command("GROUPUSERS", group_id=group_id)

        if response.get("status") == "SUCCESS":
            users = response.get("users", [])
            print(f"\nUsers in group '{group_id}' ({len(users)} total):")
            for user in users:
                print(f"  - {user}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_groupleave(self, args):
        """Leave a specific group"""
        if len(args) < 1:
            print("Usage: %groupleave <group_id>")
            return

        group_id = args[0]
        response = self.send_command("GROUPLEAVE", group_id=group_id)

        if response.get("status") == "SUCCESS":
            print(f"\n{response.get('message')}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_groupmessage(self, args):
        """Retrieve a message from a specific group by ID"""
        if len(args) < 2:
            print("Usage: %groupmessage <group_id> <message_id>")
            return

        group_id = args[0]
        try:
            msg_id = int(args[1])
        except ValueError:
            print("Error: Message ID must be a number")
            return

        response = self.send_command("GROUPMESSAGE", group_id=group_id, msg_id=msg_id)

        if response.get("status") == "SUCCESS":
            msg = response.get("message")
            print(f"\n{'='*60}")
            print(f"Message ID: {msg['msg_id']}")
            print(f"Group: {msg['group_id']}")
            print(f"Sender: {msg['sender']}")
            print(f"Date: {msg['post_date']}")
            print(f"Subject: {msg['subject']}")
            print(f"{'-'*60}")
            print(f"{msg['content']}")
            print(f"{'='*60}")
        else:
            print(f"\nError: {response.get('message')}")

    def cmd_help(self, args):
        """Display help information"""
        print("\n" + "="*60)
        print("BULLETIN BOARD SYSTEM - AVAILABLE COMMANDS")
        print("="*60)
        print("\nConnection Commands:")
        print("  %connect <host> <port>    - Connect to a bulletin board server")
        print("  %exit                     - Disconnect and exit the client")
        print("\nPart 1 - Public Message Board Commands:")
        print("  %join                     - Join the public message board")
        print("  %post <subject> <content> - Post a message to the public board")
        print("  %users                    - List all users in the public group")
        print("  %leave                    - Leave the public group")
        print("  %message <id>             - Retrieve a message by ID")
        print("\nPart 2 - Private Groups Commands:")
        print("  %groups                   - List all available groups")
        print("  %groupjoin <group_id>     - Join a specific group")
        print("  %grouppost <group_id> <subject> <content>")
        print("                            - Post a message to a group")
        print("  %groupusers <group_id>    - List users in a specific group")
        print("  %groupleave <group_id>    - Leave a specific group")
        print("  %groupmessage <group_id> <id>")
        print("                            - Retrieve a message from a group")
        print("\nOther Commands:")
        print("  help                      - Display this help message")
        print("="*60 + "\n")

    def cmd_exit(self, args):
        """Exit the client"""
        print("\nDisconnecting from server...")
        self.running = False
        self.connected = False
        if self.socket:
            self.socket.close()
        print("Goodbye!")
        sys.exit(0)

    def run_interactive(self):
        """Run the client in interactive mode"""
        print("="*60)
        print("BULLETIN BOARD SYSTEM - CLIENT")
        print("="*60)
        print("\nWelcome! Type 'help' for a list of commands.")
        print("Use %connect <host> <port> to connect to a server.\n")

        while self.running:
            try:
                user_input = input(f"{self.username if self.username else 'guest'}> ").strip()

                if not user_input:
                    continue

                # Parse the command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # Handle commands
                if command == "help":
                    self.cmd_help(args)
                elif command == "%connect":
                    if len(args) < 2:
                        print("Usage: %connect <host> <port>")
                        continue
                    host = args[0]
                    try:
                        port = int(args[1])
                    except ValueError:
                        print("Error: Port must be a number")
                        continue

                    # Prompt for username
                    username = input("Enter your username: ").strip()
                    if not username:
                        print("Error: Username cannot be empty")
                        continue

                    self.connect(host, port, username)

                elif command == "%join":
                    self.cmd_join(args)
                elif command == "%post":
                    self.cmd_post(args)
                elif command == "%users":
                    self.cmd_users(args)
                elif command == "%leave":
                    self.cmd_leave(args)
                elif command == "%message":
                    self.cmd_message(args)
                elif command == "%groups":
                    self.cmd_groups(args)
                elif command == "%groupjoin":
                    self.cmd_groupjoin(args)
                elif command == "%grouppost":
                    self.cmd_grouppost(args)
                elif command == "%groupusers":
                    self.cmd_groupusers(args)
                elif command == "%groupleave":
                    self.cmd_groupleave(args)
                elif command == "%groupmessage":
                    self.cmd_groupmessage(args)
                elif command == "%exit":
                    self.cmd_exit(args)
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\nUse %exit to disconnect and quit.")
            except EOFError:
                self.cmd_exit([])
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Main entry point for the client"""
    client = BulletinBoardClient()

    # If command line arguments provided, auto-connect
    if len(sys.argv) >= 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        username = sys.argv[3]

        if client.connect(host, port, username):
            client.run_interactive()
    else:
        # Run in interactive mode
        client.run_interactive()


if __name__ == "__main__":
    main()
