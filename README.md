# CS4065 Project 2 - Bulletin Board System

**Students:** Joshua Jerin, Satya Indukuri, Mohamed Sameer Imam

## Project Overview

This project implements a fully functional bulletin board system using pure socket programming in Python. The system consists of a multithreaded server and a client application that allows users to connect, join groups, post messages, and interact with other users in real-time.

The implementation includes:
- **Part 1:** A public message board where all users belong to a single group
- **Part 2:** Multiple private message boards where users can join different groups

## Features

### Part 1 - Public Message Board
- Connect to a dedicated server on a non-system port
- Register with a unique username (no authentication required)
- Join the public message board
- View the last 2 messages posted by earlier users
- See a list of all users in the group
- Post messages visible to all users in the group
- Retrieve full message content by message ID
- Receive real-time notifications when users join or leave
- Receive notifications when new messages are posted
- Leave the group gracefully

### Part 2 - Multiple Private Groups
- List available private groups (5 groups: Technology, Sports, Music, Books, Movies)
- Join multiple groups simultaneously
- Post messages to specific groups
- View users only in groups you belong to
- View messages only from groups you've joined
- Leave specific groups independently
- All Part 1 features extended to work with multiple groups

## Technical Implementation

### Protocol Design
The client-server communication uses a JSON-based protocol over TCP sockets:
- All messages are JSON-encoded for easy parsing and extensibility
- Request format: `{"command": "COMMAND_NAME", "param1": "value1", ...}`
- Response format: `{"status": "SUCCESS/ERROR", "message": "...", ...}`

### Server Implementation
- Uses pure Python sockets (no third-party networking libraries)
- Multithreaded architecture with one thread per client connection
- Maintains persistent TCP connections until client disconnects
- Thread-safe operations using locks for shared data structures
- Real-time notification system for group events
- Supports up to 5 concurrent clients per group

### Client Implementation
- Interactive command-line interface
- Asynchronous notification receiving in a separate thread
- User-friendly command syntax with % prefix
- Comprehensive error handling and feedback

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

No installation is required. Simply ensure Python 3 is installed on your system:

```bash
python --version
```

## Compilation

Since Python is an interpreted language, no compilation is necessary. However, you can make the scripts executable:

```bash
chmod +x server.py
chmod +x client.py
```

## Usage

### Starting the Server

To start the server on the default port (8888):

```bash
python server.py
```

To start the server on a custom port:

```bash
python server.py <port_number>
```

Example:
```bash
python server.py 9000
```

The server will display:
```
[SERVER] Bulletin Board Server started on localhost:8888
[SERVER] Waiting for connections...
```

### Starting the Client

#### Interactive Mode (Recommended)

```bash
python client.py
```

Then use the `%connect` command to connect:
```
guest> %connect localhost 8888
Enter your username: alice
```

#### Direct Connection Mode

You can also connect directly by providing arguments:

```bash
python client.py <host> <port> <username>
```

Example:
```bash
python client.py localhost 8888 alice
```

### Available Commands

#### Connection Commands
- `%connect <host> <port>` - Connect to a bulletin board server
- `%exit` - Disconnect and exit the client

#### Part 1 - Public Message Board Commands
- `%join` - Join the public message board
- `%post <subject> <content>` - Post a message to the public board
- `%users` - List all users in the public group
- `%leave` - Leave the public group
- `%message <id>` - Retrieve a message by ID

#### Part 2 - Private Groups Commands
- `%groups` - List all available groups
- `%groupjoin <group_id>` - Join a specific group
- `%grouppost <group_id> <subject> <content>` - Post a message to a group
- `%groupusers <group_id>` - List users in a specific group
- `%groupleave <group_id>` - Leave a specific group
- `%groupmessage <group_id> <id>` - Retrieve a message from a group

#### Other Commands
- `help` - Display help message with all commands

## Example Usage Scenarios

### Scenario 1: Public Message Board (Part 1)

**Client 1 (Alice):**
```bash
alice> %connect localhost 8888
alice> %join
alice> %post "Hello World" "This is my first message!"
alice> %users
```

**Client 2 (Bob):**
```bash
bob> %connect localhost 8888
bob> %join
[NOTIFICATION] alice has joined the group
bob> %message 1
bob> %post "Re: Hello" "Hi Alice, nice to meet you!"
```

**Client 1 (Alice):**
```
[NOTIFICATION] bob has joined the group
[NOTIFICATION] New message posted: [2] bob | 2025-12-01 14:30:15 | Re: Hello
alice> %message 2
alice> %leave
```

### Scenario 2: Multiple Private Groups (Part 2)

**Client 1 (Alice):**
```bash
alice> %connect localhost 8888
alice> %groups
alice> %groupjoin tech
alice> %grouppost tech "Python vs Java" "What's your favorite language?"
alice> %groupjoin music
alice> %grouppost music "Favorite Band" "Who do you listen to?"
```

**Client 2 (Bob):**
```bash
bob> %connect localhost 8888
bob> %groupjoin tech
[NOTIFICATION] alice has joined the group
bob> %groupusers tech
bob> %groupmessage tech 1
bob> %grouppost tech "Re: Python vs Java" "I prefer Python for its simplicity!"
```

**Client 1 (Alice):**
```
[NOTIFICATION] bob has joined the group
[NOTIFICATION] New message posted: [2] bob | 2025-12-01 14:35:20 | Re: Python vs Java
alice> %groupmessage tech 2
```

## Message Format

Messages are displayed in the following format:
```
[Message ID] Sender | Post Date | Subject
```

Example:
```
[1] alice | 2025-12-01 14:25:10 | Hello World
[2] bob | 2025-12-01 14:30:15 | Re: Hello
```

Full message display:
```
============================================================
Message ID: 1
Sender: alice
Date: 2025-12-01 14:25:10
Subject: Hello World
------------------------------------------------------------
This is my first message!
============================================================
```

## Available Groups (Part 2)

The system provides 5 private groups:

| Group ID | Name                    | Description              |
|----------|-------------------------|--------------------------|
| tech     | Technology Discussion   | Tech and programming     |
| sports   | Sports Talk             | Sports discussions       |
| music    | Music Lovers            | Music recommendations    |
| books    | Book Club               | Book discussions         |
| movies   | Movie Reviews           | Movie talk and reviews   |

## Architecture

### Server Architecture

```
BulletinBoardServer
├── Socket Listener (Main Thread)
│   └── Accepts incoming connections
├── Client Handler Threads (One per client)
│   ├── Receives and processes commands
│   └── Sends responses
├── Notification System
│   └── Broadcasts events to group members
└── Data Structures
    ├── Groups (with messages and members)
    ├── Connected clients
    └── Client-group mappings
```

### Client Architecture

```
BulletinBoardClient
├── Main Thread (Interactive Loop)
│   ├── Reads user input
│   ├── Parses commands
│   └── Sends requests to server
└── Listener Thread
    └── Receives notifications asynchronously
```

### Protocol Messages

**Example Request:**
```json
{
  "command": "POST",
  "subject": "Hello World",
  "content": "This is my first message!"
}
```

**Example Response:**
```json
{
  "status": "SUCCESS",
  "message": "Message posted successfully",
  "msg_id": 1
}
```

**Example Notification:**
```json
{
  "type": "NOTIFICATION",
  "message": "alice has joined the group"
}
```

## Threading and Concurrency

### Server-Side Threading
- **Main Thread:** Accepts new client connections
- **Client Handler Threads:** One thread per connected client for processing commands
- **Notification Threads:** Short-lived threads for sending notifications to avoid blocking
- **Thread Safety:** All shared data structures are protected by locks

### Client-Side Threading
- **Main Thread:** Handles user input and command processing
- **Listener Thread:** Continuously listens for server notifications
- Both threads access the socket safely

## Error Handling

The implementation includes comprehensive error handling for:
- Connection failures
- Invalid commands
- Non-existent users or groups
- Message ID not found
- Attempting to join already-joined groups
- Attempting to leave non-joined groups
- Socket errors and disconnections
- JSON parsing errors
- Threading exceptions

## Testing

### Automated Test

Run the test script to see automated demo:
```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run test
python test_demo.py
```

### Testing Part 1 (Public Message Board)

1. Start the server:
   ```bash
   python server.py
   ```

2. Open 3 terminal windows and start 3 clients:
   ```bash
   # Terminal 1
   python client.py localhost 8888 alice

   # Terminal 2
   python client.py localhost 8888 bob

   # Terminal 3
   python client.py localhost 8888 charlie
   ```

3. Test the following scenarios:
   - All clients join the public board
   - Verify each client sees the other users
   - Post messages from different clients
   - Verify all clients receive notifications
   - Retrieve message content by ID
   - Have one client leave and verify others are notified

### Testing Part 2 (Multiple Private Groups)

1. Start the server (same as above)

2. Start multiple clients and test:
   - List available groups
   - Join different groups from different clients
   - Post messages to specific groups
   - Verify users in one group cannot see messages from other groups
   - Join multiple groups from the same client
   - Post to different groups and verify isolation
   - Leave groups and verify notifications

### Testing Concurrent Access

1. Start server
2. Connect 5+ clients simultaneously
3. Have all clients join the same group
4. Post messages rapidly from multiple clients
5. Verify message ordering and delivery
6. Test disconnecting clients while others are active

## Troubleshooting

**Problem:** "Connection refused"
- **Solution:** Make sure server is running first

**Problem:** "Username already exists"
- **Solution:** Choose a different username

**Problem:** "Not a member of this group"
- **Solution:** Join the group first with `%join` or `%groupjoin <id>`

**Problem:** Port already in use
- **Solution:** Use a different port: `python server.py 9000`

## Major Issues and Solutions

### Issue 1: Notification Delivery During Command Processing
**Problem:** Initial implementation used blocking sends, causing delays when broadcasting notifications to many clients.

**Solution:** Implemented asynchronous notification sending using separate short-lived threads for each notification. This prevents the server from blocking while sending notifications to slow clients.

### Issue 2: Race Conditions in Shared Data
**Problem:** Multiple threads accessing the same data structures (groups, clients, messages) could cause race conditions.

**Solution:** Implemented thread-safe access using Python's `threading.Lock` to protect all critical sections where shared data is accessed or modified.

### Issue 3: Socket Receive Buffer Management
**Problem:** Large messages or rapid successive messages could cause receive buffer issues.

**Solution:** Used a 4096-byte buffer size which is sufficient for JSON-encoded messages. The protocol keeps messages reasonably sized by separating message headers from content.

### Issue 4: Client Disconnection Detection
**Problem:** Server didn't immediately detect when clients disconnected unexpectedly.

**Solution:** Implemented proper exception handling in the receive loop. When a socket receive returns empty data or raises an exception, the client is properly cleaned up and removed from all groups.

### Issue 5: Message Display Synchronization
**Problem:** Asynchronous notifications interrupted user input in the client.

**Solution:** Added prompt re-display after notifications using `flush=True` and repositioning the cursor. This provides a better user experience when notifications arrive during typing.

## File Structure

```
project2/
├── server.py          # Server implementation
├── client.py          # Client implementation
├── README.md          # This file
└── Makefile           # Build automation (optional)
```

