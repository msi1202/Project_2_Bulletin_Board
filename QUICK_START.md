# Quick Start Guide

## 5-Minute Setup

### Step 1: Start the Server
```bash
python server.py
```
or
```bash
make server
```

### Step 2: Start a Client (in a new terminal)
```bash
python client.py
```

### Step 3: Connect to Server
```
guest> %connect localhost 8888
Enter your username: alice
```

### Step 4: Join Public Group
```
alice> %join
```

### Step 5: Post a Message
```
alice> %post "My First Message" "Hello everyone!"
```

### Step 6: Try Multiple Groups (Part 2)
```
alice> %groups
alice> %groupjoin tech
alice> %grouppost tech "Python Question" "What's your favorite Python feature?"
```

## Testing with Multiple Clients

### Terminal 1 (Server)
```bash
python server.py
```

### Terminal 2 (Client 1)
```bash
python client.py localhost 8888 alice
alice> %join
alice> %post "Hello" "This is Alice"
```

### Terminal 3 (Client 2)
```bash
python client.py localhost 8888 bob
bob> %join
bob> %users
bob> %message 1
bob> %post "Re: Hello" "Hi Alice!"
```

### Terminal 4 (Client 3)
```bash
python client.py localhost 8888 charlie
charlie> %groups
charlie> %groupjoin tech
charlie> %grouppost tech "Welcome" "Hello tech group!"
```

## Command Cheat Sheet

### Essential Commands
- `%connect <host> <port>` - Connect to server
- `%join` - Join public board
- `%post <subject> <message>` - Post message
- `%users` - List users
- `%message <id>` - Read message
- `%groups` - List all groups
- `%groupjoin <id>` - Join a group
- `%exit` - Quit

### Example Flow
```
%connect localhost 8888      # Connect
%join                        # Join public
%users                       # See who's here
%post "Test" "Hello!"        # Post message
%groups                      # See available groups
%groupjoin tech              # Join tech group
%grouppost tech "Hi" "Hello tech!"  # Post to tech
%groupusers tech             # See tech members
%exit                        # Quit
```

## Automated Test

Run the test script to see automated demo:
```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run test
python test_demo.py
```

## Tips

1. **Run server first** - Always start server before clients
2. **Multiple terminals** - Open separate terminals for each client
3. **Port conflicts** - If port 8888 is busy, use: `python server.py 9000`
4. **Help command** - Type `help` anytime in the client
5. **Notifications** - You'll see real-time updates when others join/post

## Troubleshooting

**Problem:** "Connection refused"
- **Solution:** Make sure server is running first

**Problem:** "Username already exists"
- **Solution:** Choose a different username

**Problem:** "Not a member of this group"
- **Solution:** Join the group first with `%join` or `%groupjoin <id>`

**Problem:** Port already in use
- **Solution:** Use a different port: `python server.py 9000`
