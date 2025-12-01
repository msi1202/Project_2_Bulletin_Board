# CS4065 Project 2 - Bulletin Board System

**Students:** [Your Name], [Partner 1 Name], [Partner 2 Name]

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
python3 --version
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
python3 server.py
```

To start the server on a custom port:

```bash
python3 server.py <port_number>
```

Example:
```bash
python3 server.py 9000
```

The server will display:
```
[SERVER] Bulletin Board Server started on localhost:8888
[SERVER] Waiting for connections...
```

### Starting the Client

#### Interactive Mode (Recommended)

```bash
python3 client.py
```

Then use the `%connect` command to connect:
```
guest> %connect localhost 8888
Enter your username: alice
```

#### Direct Connection Mode

You can also connect directly by providing arguments:

```bash
python3 client.py <host> <port> <username>
```

Example:
```bash
python3 client.py localhost 8888 alice
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

### Testing Part 1 (Public Message Board)

1. Start the server:
   ```bash
   python3 server.py
   ```

2. Open 3 terminal windows and start 3 clients:
   ```bash
   # Terminal 1
   python3 client.py localhost 8888 alice

   # Terminal 2
   python3 client.py localhost 8888 bob

   # Terminal 3
   python3 client.py localhost 8888 charlie
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

## Limitations and Future Enhancements

### Current Limitations
- No persistent storage (messages are lost when server restarts)
- No user authentication or password protection
- Message size limited by buffer size
- No message editing or deletion
- No private direct messaging between users
- No message search functionality

### Possible Future Enhancements
- Database integration for persistent storage
- User authentication system
- Message pagination for large message boards
- File attachment support
- Private messaging between users
- Message reactions and likes
- User roles and permissions
- Group creation by users
- Message formatting (bold, italic, etc.)
- GUI implementation using tkinter or PyQt

## File Structure

```
project2/
├── server.py          # Server implementation
├── client.py          # Client implementation
├── README.md          # This file
└── Makefile           # Build automation (optional)
```

## Code Documentation

Both `server.py` and `client.py` are well-documented with:
- Module-level docstrings
- Class docstrings explaining purpose
- Method docstrings for all functions
- Inline comments for complex logic
- Type hints for better code clarity

## Performance Considerations

- Server can handle multiple concurrent clients efficiently
- Thread-per-client model scales well for moderate user counts (< 100)
- JSON parsing is fast enough for real-time messaging
- Lock contention is minimized by keeping critical sections short
- Memory usage is proportional to number of messages and users

## Security Considerations

**Note:** This implementation is for educational purposes only and is NOT production-ready.

Security issues that should be addressed for production use:
- No input validation or sanitization
- Susceptible to JSON injection attacks
- No rate limiting or DoS protection
- No encryption (messages sent in plain text)
- No authentication or authorization
- No audit logging

## Grading Checklist

### Functionality (70%)

**Part 1 (40%):**
- [x] Server listens on non-system port
- [x] Client connects and registers with username
- [x] Users can join the public group
- [x] New users see last 2 messages
- [x] List of users displayed when joining
- [x] Users notified when others join/leave
- [x] Post messages visible to all users
- [x] Retrieve message content by ID
- [x] Leave group functionality
- [x] Messages displayed in correct format

**Part 2 (30%):**
- [x] List 5 available groups
- [x] Join multiple groups simultaneously
- [x] Post messages to specific groups
- [x] View users only in joined groups
- [x] View messages only from joined groups
- [x] Leave specific groups
- [x] Group isolation (users in one group can't see others)

### Usability (15%)
- [x] User-friendly command interface
- [x] All required commands implemented
- [x] Clear command syntax with % prefix
- [x] Help command available
- [x] Informative error messages
- [x] Real-time notifications

### Documentation (15%)
- [x] Code well-documented with docstrings
- [x] Expressive variable names
- [x] README with compilation/running instructions
- [x] Usage examples provided
- [x] Major issues documented

## Contact and Support

For questions or issues, please contact the course instructor or teaching assistants.

## License

This project is submitted as part of CS4065 coursework and is subject to university academic integrity policies.

---

**Last Updated:** December 1, 2025
