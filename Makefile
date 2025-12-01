# Makefile for CS4065 Project 2 - Bulletin Board System
# Python-based project - no compilation needed, but provides convenience commands

.PHONY: all server client clean help test chmod

# Default target
all: help

# Display help information
help:
	@echo "============================================================"
	@echo "CS4065 Project 2 - Bulletin Board System"
	@echo "============================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make server       - Start the bulletin board server"
	@echo "  make server PORT=<port> - Start server on custom port"
	@echo "  make client       - Start a client in interactive mode"
	@echo "  make client-connect HOST=<host> PORT=<port> USER=<username>"
	@echo "                    - Start client with auto-connect"
	@echo "  make test         - Run basic tests"
	@echo "  make chmod        - Make Python scripts executable"
	@echo "  make clean        - Clean up temporary files"
	@echo "  make help         - Display this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make server"
	@echo "  make server PORT=9000"
	@echo "  make client"
	@echo "  make client-connect HOST=localhost PORT=8888 USER=alice"
	@echo ""
	@echo "Manual execution:"
	@echo "  python3 server.py [port]"
	@echo "  python3 client.py [host port username]"
	@echo ""
	@echo "============================================================"

# Default port for server
PORT ?= 8888

# Start the server
server:
	@echo "Starting Bulletin Board Server on port $(PORT)..."
	@python3 server.py $(PORT)

# Start the client in interactive mode
client:
	@echo "Starting Bulletin Board Client..."
	@python3 client.py

# Start the client with auto-connect
# Usage: make client-connect HOST=localhost PORT=8888 USER=alice
client-connect:
ifndef HOST
	$(error HOST is not set. Usage: make client-connect HOST=<host> PORT=<port> USER=<username>)
endif
ifndef PORT
	$(error PORT is not set. Usage: make client-connect HOST=<host> PORT=<port> USER=<username>)
endif
ifndef USER
	$(error USER is not set. Usage: make client-connect HOST=<host> PORT=<port> USER=<username>)
endif
	@echo "Connecting to $(HOST):$(PORT) as $(USER)..."
	@python3 client.py $(HOST) $(PORT) $(USER)

# Make scripts executable
chmod:
	@echo "Making Python scripts executable..."
	@chmod +x server.py
	@chmod +x client.py
	@echo "Done! You can now run ./server.py and ./client.py"

# Basic tests
test:
	@echo "Running basic tests..."
	@echo "Checking Python version..."
	@python3 --version
	@echo ""
	@echo "Checking if server.py exists..."
	@test -f server.py && echo "✓ server.py found" || echo "✗ server.py not found"
	@echo "Checking if client.py exists..."
	@test -f client.py && echo "✓ client.py found" || echo "✗ client.py not found"
	@echo ""
	@echo "Checking Python syntax..."
	@python3 -m py_compile server.py && echo "✓ server.py syntax OK" || echo "✗ server.py syntax error"
	@python3 -m py_compile client.py && echo "✓ client.py syntax OK" || echo "✗ client.py syntax error"
	@echo ""
	@echo "All basic tests passed!"

# Clean temporary files
clean:
	@echo "Cleaning up temporary files..."
	@rm -f *.pyc
	@rm -rf __pycache__
	@rm -f .DS_Store
	@echo "Done!"

# Run server in background (for testing)
server-bg:
	@echo "Starting server in background on port $(PORT)..."
	@python3 server.py $(PORT) &
	@echo "Server started! PID: $$!"

# Stop background server
server-stop:
	@echo "Stopping background server..."
	@pkill -f "python3 server.py" || echo "No server process found"
	@echo "Done!"
