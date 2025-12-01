#!/usr/bin/env python3
"""
Bulletin Board Server
A multithreaded server implementation for a bulletin board system
supporting public and private group messaging.
"""

import socket
import threading
import json
import time
from datetime import datetime
from typing import Dict, List, Set


class Message:
    """Represents a message posted on the bulletin board"""

    def __init__(self, msg_id: int, sender: str, subject: str, content: str, group_id: str = "public"):
        self.msg_id = msg_id
        self.sender = sender
        self.subject = subject
        self.content = content
        self.post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.group_id = group_id

    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "subject": self.subject,
            "content": self.content,
            "post_date": self.post_date,
            "group_id": self.group_id
        }

    def get_header(self):
        """Get message header for display"""
        return f"[{self.msg_id}] {self.sender} | {self.post_date} | {self.subject}"


class Group:
    """Represents a message board group"""

    def __init__(self, group_id: str, name: str):
        self.group_id = group_id
        self.name = name
        self.members: Set[str] = set()
        self.messages: List[Message] = []
        self.message_counter = 0

    def add_member(self, username: str):
        """Add a member to the group"""
        self.members.add(username)

    def remove_member(self, username: str):
        """Remove a member from the group"""
        self.members.discard(username)

    def add_message(self, sender: str, subject: str, content: str):
        """Add a new message to the group"""
        self.message_counter += 1
        msg = Message(self.message_counter, sender, subject, content, self.group_id)
        self.messages.append(msg)
        return msg

    def get_last_n_messages(self, n: int = 2):
        """Get the last N messages"""
        return self.messages[-n:] if len(self.messages) >= n else self.messages

    def get_message_by_id(self, msg_id: int):
        """Get a message by its ID"""
        for msg in self.messages:
            if msg.msg_id == msg_id:
                return msg
        return None


class BulletinBoardServer:
    """Main bulletin board server class"""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[str, socket.socket] = {}  # username -> socket
        self.client_groups: Dict[str, Set[str]] = {}  # username -> set of group_ids
        self.groups: Dict[str, Group] = {}
        self.lock = threading.Lock()
        self.running = False

        # Initialize groups
        self._initialize_groups()

    def _initialize_groups(self):
        """Initialize the default groups"""
        # Public group for Part 1
        self.groups["public"] = Group("public", "Public Message Board")

        # Private groups for Part 2
        self.groups["tech"] = Group("tech", "Technology Discussion")
        self.groups["sports"] = Group("sports", "Sports Talk")
        self.groups["music"] = Group("music", "Music Lovers")
        self.groups["books"] = Group("books", "Book Club")
        self.groups["movies"] = Group("movies", "Movie Reviews")

    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True

        print(f"[SERVER] Bulletin Board Server started on {self.host}:{self.port}")
        print(f"[SERVER] Waiting for connections...")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[SERVER] New connection from {address}")

                # Start a new thread for this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Error accepting connection: {e}")

    def handle_client(self, client_socket: socket.socket, address):
        """Handle communication with a connected client"""
        username = None

        try:
            # Receive username from client
            data = client_socket.recv(4096).decode('utf-8')
            request = json.loads(data)

            if request.get("command") == "REGISTER":
                username = request.get("username")

                with self.lock:
                    if username in self.clients:
                        # Username already exists
                        response = {
                            "status": "ERROR",
                            "message": "Username already exists. Please choose another."
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        client_socket.close()
                        return

                    # Register the client
                    self.clients[username] = client_socket
                    self.client_groups[username] = set()

                # Send success response
                response = {
                    "status": "SUCCESS",
                    "message": f"Welcome to the Bulletin Board, {username}!"
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
                print(f"[SERVER] {username} registered successfully")

            # Main command loop
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                command = request.get("command")

                # Process the command
                response = self.process_command(username, command, request)

                # Send response back to client
                client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"[SERVER] Error handling client {username}: {e}")

        finally:
            # Clean up when client disconnects
            if username:
                self.disconnect_client(username)

    def process_command(self, username: str, command: str, request: dict):
        """Process a command from the client"""

        if command == "JOIN":
            return self.handle_join(username)

        elif command == "POST":
            subject = request.get("subject", "")
            content = request.get("content", "")
            return self.handle_post(username, "public", subject, content)

        elif command == "USERS":
            return self.handle_users(username, "public")

        elif command == "LEAVE":
            return self.handle_leave(username, "public")

        elif command == "MESSAGE":
            msg_id = request.get("msg_id")
            return self.handle_get_message(username, "public", msg_id)

        elif command == "GROUPS":
            return self.handle_list_groups()

        elif command == "GROUPJOIN":
            group_id = request.get("group_id")
            return self.handle_group_join(username, group_id)

        elif command == "GROUPPOST":
            group_id = request.get("group_id")
            subject = request.get("subject", "")
            content = request.get("content", "")
            return self.handle_post(username, group_id, subject, content)

        elif command == "GROUPUSERS":
            group_id = request.get("group_id")
            return self.handle_users(username, group_id)

        elif command == "GROUPLEAVE":
            group_id = request.get("group_id")
            return self.handle_leave(username, group_id)

        elif command == "GROUPMESSAGE":
            group_id = request.get("group_id")
            msg_id = request.get("msg_id")
            return self.handle_get_message(username, group_id, msg_id)

        else:
            return {"status": "ERROR", "message": "Unknown command"}

    def handle_join(self, username: str):
        """Handle user joining the public group"""
        with self.lock:
            group = self.groups["public"]
            group.add_member(username)
            self.client_groups[username].add("public")

            # Get list of users
            users = list(group.members)

            # Get last 2 messages
            recent_messages = group.get_last_n_messages(2)
            messages_headers = [msg.get_header() for msg in recent_messages]

            # Notify other users
            self.broadcast_notification(
                "public",
                f"{username} has joined the group",
                exclude=username
            )

            return {
                "status": "SUCCESS",
                "message": "Joined public message board",
                "users": users,
                "recent_messages": messages_headers
            }

    def handle_group_join(self, username: str, group_id: str):
        """Handle user joining a private group"""
        with self.lock:
            if group_id not in self.groups:
                return {"status": "ERROR", "message": "Group does not exist"}

            if group_id in self.client_groups[username]:
                return {"status": "ERROR", "message": "Already a member of this group"}

            group = self.groups[group_id]
            group.add_member(username)
            self.client_groups[username].add(group_id)

            # Get list of users
            users = list(group.members)

            # Get last 2 messages
            recent_messages = group.get_last_n_messages(2)
            messages_headers = [msg.get_header() for msg in recent_messages]

            # Notify other users in the group
            self.broadcast_notification(
                group_id,
                f"{username} has joined the group",
                exclude=username
            )

            return {
                "status": "SUCCESS",
                "message": f"Joined group: {group.name}",
                "users": users,
                "recent_messages": messages_headers
            }

    def handle_post(self, username: str, group_id: str, subject: str, content: str):
        """Handle posting a message"""
        with self.lock:
            if group_id not in self.groups:
                return {"status": "ERROR", "message": "Group does not exist"}

            if group_id not in self.client_groups[username]:
                return {"status": "ERROR", "message": "You are not a member of this group"}

            group = self.groups[group_id]
            msg = group.add_message(username, subject, content)

            # Broadcast the new message to all group members
            self.broadcast_notification(
                group_id,
                f"New message posted: {msg.get_header()}",
                exclude=username
            )

            return {
                "status": "SUCCESS",
                "message": "Message posted successfully",
                "msg_id": msg.msg_id
            }

    def handle_users(self, username: str, group_id: str):
        """Handle retrieving list of users in a group"""
        with self.lock:
            if group_id not in self.groups:
                return {"status": "ERROR", "message": "Group does not exist"}

            if group_id not in self.client_groups[username]:
                return {"status": "ERROR", "message": "You are not a member of this group"}

            group = self.groups[group_id]
            users = list(group.members)

            return {
                "status": "SUCCESS",
                "users": users
            }

    def handle_leave(self, username: str, group_id: str):
        """Handle user leaving a group"""
        with self.lock:
            if group_id not in self.groups:
                return {"status": "ERROR", "message": "Group does not exist"}

            if group_id not in self.client_groups[username]:
                return {"status": "ERROR", "message": "You are not a member of this group"}

            group = self.groups[group_id]
            group.remove_member(username)
            self.client_groups[username].discard(group_id)

            # Notify other users
            self.broadcast_notification(
                group_id,
                f"{username} has left the group",
                exclude=username
            )

            return {
                "status": "SUCCESS",
                "message": f"Left group: {group.name}"
            }

    def handle_get_message(self, username: str, group_id: str, msg_id: int):
        """Handle retrieving a message by ID"""
        with self.lock:
            if group_id not in self.groups:
                return {"status": "ERROR", "message": "Group does not exist"}

            if group_id not in self.client_groups[username]:
                return {"status": "ERROR", "message": "You are not a member of this group"}

            group = self.groups[group_id]
            msg = group.get_message_by_id(msg_id)

            if msg is None:
                return {"status": "ERROR", "message": "Message not found"}

            return {
                "status": "SUCCESS",
                "message": msg.to_dict()
            }

    def handle_list_groups(self):
        """Handle listing all available groups"""
        groups_list = []
        for group_id, group in self.groups.items():
            if group_id != "public":  # Exclude public group from the list
                groups_list.append({
                    "group_id": group_id,
                    "name": group.name,
                    "member_count": len(group.members)
                })

        return {
            "status": "SUCCESS",
            "groups": groups_list
        }

    def broadcast_notification(self, group_id: str, message: str, exclude: str = None):
        """Broadcast a notification to all members of a group"""
        if group_id not in self.groups:
            return

        group = self.groups[group_id]
        notification = {
            "type": "NOTIFICATION",
            "message": message
        }

        for member in group.members:
            if member != exclude and member in self.clients:
                try:
                    client_socket = self.clients[member]
                    # Send notification asynchronously
                    threading.Thread(
                        target=self._send_notification,
                        args=(client_socket, notification)
                    ).start()
                except Exception as e:
                    print(f"[SERVER] Error sending notification to {member}: {e}")

    def _send_notification(self, client_socket: socket.socket, notification: dict):
        """Send a notification to a client (helper method)"""
        try:
            client_socket.send(json.dumps(notification).encode('utf-8'))
        except Exception as e:
            print(f"[SERVER] Error sending notification: {e}")

    def disconnect_client(self, username: str):
        """Handle client disconnection"""
        with self.lock:
            if username in self.clients:
                # Remove from all groups
                if username in self.client_groups:
                    for group_id in list(self.client_groups[username]):
                        group = self.groups.get(group_id)
                        if group:
                            group.remove_member(username)
                            # Notify other users
                            self.broadcast_notification(
                                group_id,
                                f"{username} has disconnected",
                                exclude=username
                            )

                    del self.client_groups[username]

                # Close socket and remove from clients
                try:
                    self.clients[username].close()
                except:
                    pass
                del self.clients[username]

                print(f"[SERVER] {username} disconnected")

    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def main():
    """Main entry point for the server"""
    import sys

    # Default values
    host = "localhost"
    port = 8888

    # Parse command line arguments
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    # Create and start the server
    server = BulletinBoardServer(host, port)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        server.stop()


if __name__ == "__main__":
    main()
