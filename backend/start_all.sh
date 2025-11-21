#!/bin/bash

# Start all A2A agent services
# This script starts each agent as an independent service

echo "🚀 Starting A2A Web Builder - Distributed Architecture"
echo "=================================================="

# Kill any existing processes on these ports
echo "Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:8003 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start agent services in background
echo ""
echo "Current directory: $(pwd)"
echo "Starting Analyst Agent (port 8001)..."
(cd agents/analyst-service && echo "Analyst dir: $(pwd)" && ../../.venv/bin/python main.py > ../../logs/analyst.log 2>&1) &
ANALYST_PID=$!

echo "Starting Developer Agent (port 8002)..."
(cd agents/developer-service && echo "Developer dir: $(pwd)" && ../../.venv/bin/python main.py > ../../logs/developer.log 2>&1) &
DEVELOPER_PID=$!

echo "Starting Tester Agent (port 8003)..."
(cd agents/tester-service && echo "Tester dir: $(pwd)" && ../../.venv/bin/python main.py > ../../logs/tester.log 2>&1) &
TESTER_PID=$!

# Wait for agents to start
echo ""
echo "Waiting for agents to initialize..."
sleep 3

# Check if agents are running
echo ""
echo "Checking agent health..."
curl -s http://localhost:8001/health > /dev/null && echo "✓ Analyst agent is healthy" || echo "✗ Analyst agent failed to start"
curl -s http://localhost:8002/health > /dev/null && echo "✓ Developer agent is healthy" || echo "✗ Developer agent failed to start"
curl -s http://localhost:8003/health > /dev/null && echo "✓ Tester agent is healthy" || echo "✗ Tester agent failed to start"

# Start main orchestrator
echo ""
echo "Starting Main Orchestrator (port 8000)..."
.venv/bin/python main.py

# Cleanup on exit
trap "kill $ANALYST_PID $DEVELOPER_PID $TESTER_PID 2>/dev/null" EXIT
