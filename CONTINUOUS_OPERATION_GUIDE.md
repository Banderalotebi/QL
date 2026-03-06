#!/usr/bin/env python3
"""
🏛️ CONTINUOUS HIVE OPERATION GUIDE
Complete instructions for running the hive 24/7
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║             🏛️  RUNNING THE HIVE CONTINUOUSLY (24/7)                          ║
║                                                                               ║
║  Your hive is now configured to run indefinitely with automatic recovery     ║
║  and monitoring. Choose your preferred method below.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝


═══════════════════════════════════════════════════════════════════════════════
⚡ QUICK START (Recommended for Dev)
═══════════════════════════════════════════════════════════════════════════════

For quick continuous operation in your current environment:

    cd /workspaces/QL
    chmod +x start_hive.sh stop_hive.sh monitor_hive.sh
    ./start_hive.sh 3 300

This starts the hive with:
  • Batch size: 3 surahs per cycle
  • Interval: 300 seconds (5 minutes) between batches
  • Output: Logged to /workspaces/QL/logs/


═══════════════════════════════════════════════════════════════════════════════
📊 METHOD 1: NOHUP (Simplest for Production)
═══════════════════════════════════════════════════════════════════════════════

Start the hive in background with nohup (ignores hangup signals):

    cd /workspaces/QL
    nohup python hive_continuous.py --batch-size 3 --interval 300 \\
        > hive.log 2>&1 &

Monitor in real-time:

    tail -f /workspaces/QL/hive.log

The hive will:
  ✓ Keep running even if terminal closes
  ✓ Auto-recover from errors
  ✓ Save state every 3 batches
  ✓ Log all activity to hive.log

Stop the hive:

    pkill -f "hive_continuous.py"


═══════════════════════════════════════════════════════════════════════════════
📺 METHOD 2: GNU SCREEN (Great for SSH)
═══════════════════════════════════════════════════════════════════════════════

Create a persistent screen session:

    # Create new session
    screen -S hive

    # Inside screen, run:
    cd /workspaces/QL
    python hive_continuous.py --batch-size 3 --interval 300

    # Detach with: Ctrl+A, then D (won't stop the process)

Monitor from another terminal:

    screen -r hive        # Reattach to the session
    screen -ls            # List all sessions

This is excellent for SSH sessions because:
  ✓ Survives SSH disconnection
  ✓ Can reattach anytime
  ✓ Fully interactive


═══════════════════════════════════════════════════════════════════════════════
🖥️  METHOD 3: TMUX (Advanced Session Manager)
═══════════════════════════════════════════════════════════════════════════════

Create a tmux session:

    # Create new session
    tmux new-session -d -s hive -c /workspaces/QL \\
        'python hive_continuous.py --batch-size 3 --interval 300'

Monitor:

    tmux attach -t hive         # Attach to session
    tmux list-sessions          # List sessions
    tmux kill-session -t hive   # Stop hive

Advantages:
  ✓ More powerful than screen
  ✓ Window/pane support
  ✓ Better scripting
  ✓ Modern alternative to screen


═══════════════════════════════════════════════════════════════════════════════
🐳 METHOD 4: DOCKER (Containerized)
═══════════════════════════════════════════════════════════════════════════════

Create a Dockerfile:

    FROM python:3.10-slim
    WORKDIR /app
    COPY /workspaces/QL /app
    RUN pip install -r requirements.txt
    CMD ["python", "hive_continuous.py", "--batch-size", "3", "--interval", "300"]

Build and run:

    docker build -t hive .
    docker run -d --name hive_instance \\
        -v /workspaces/QL/data:/app/data \\
        -v /workspaces/QL/logs:/app/logs \\
        hive

Monitor:

    docker logs -f hive_instance
    docker stop hive_instance


═══════════════════════════════════════════════════════════════════════════════
🔧 METHOD 5: SYSTEMD SERVICE (Linux Production)
═══════════════════════════════════════════════════════════════════════════════

Register as a systemd service:

    sudo cp /workspaces/QL/hive.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable hive          # Start on boot
    sudo systemctl start hive           # Start now

Monitor:

    sudo systemctl status hive
    sudo journalctl -u hive -f          # Stream logs
    sudo systemctl stop hive            # Stop
    sudo systemctl restart hive         # Restart

This provides:
  ✓ Automatic startup on system reboot
  ✓ Process supervision and restart
  ✓ Integrated with system logging
  ✓ Standard service management


═══════════════════════════════════════════════════════════════════════════════
🎯 ADVANCED CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

Customize batch behavior:

    # Run all 29 surahs as single massive batch
    python hive_continuous.py --all-muqattaat --interval 1800  (30 min between cycles)

    # Small batches for frequent iterations
    python hive_continuous.py --batch-size 1 --interval 60  (1 min between)

    # Large batches for efficiency
    python hive_continuous.py --batch-size 10 --interval 600  (10 min between)

Environment variables:

    export OLLAMA_API_KEY="your_key"
    export DATABASE_URL="postgresql://..."
    python hive_continuous.py

The hive will:
  ✓ Use .env for credentials
  ✓ Gracefully degrade if services unavailable
  ✓ Save state periodically
  ✓ Log everything with timestamps


═══════════════════════════════════════════════════════════════════════════════
📈 MONITORING & HEALTH CHECKS
═══════════════════════════════════════════════════════════════════════════════

Python monitoring script:

    from src.agents.hive_council import get_hive_council
    
    hive = get_hive_council()
    status = hive.get_hive_status()
    
    print(f"Thoughts: {status['total_thoughts_logged']}")
    print(f"Supervisions: {status['total_supervisions']}")
    print(f"Memory: {status['shared_memory_size']} bytes")

Shell command:

    tail -20 /workspaces/QL/logs/hive_*.log
    ps aux | grep hive_continuous
    free -h && vmstat

Watch Streamlit dashboard:

    streamlit run /workspaces/QL/frontend/streamlit_dashboard.py


═══════════════════════════════════════════════════════════════════════════════
🛡️  ERROR HANDLING & RECOVERY
═══════════════════════════════════════════════════════════════════════════════

The hive automatically:

  ✓ Retries failed batches up to 3 times
  ✓ Waits 10 seconds between retries
  ✓ Saves state after every 3 batches
  ✓ Logs all errors with timestamps
  ✓ Handles database disconnections gracefully
  ✓ Gracefully shuts down on SIGTERM
  ✓ Continues with mathematical auditing if LLM unavailable

If hive stops unexpectedly:

    1. Check logs:
       tail -100 /workspaces/QL/logs/hive_*.log

    2. Verify database connection:
       python -c "from src.data.neon_db import NeonDB; db=NeonDB(); print(db.is_connected)"

    3. Check for zombie processes:
       ps aux | grep hive_continuous

    4. Restart:
       nohup python hive_continuous.py --batch-size 3 --interval 300 > hive.log 2>&1 &


═══════════════════════════════════════════════════════════════════════════════
💾 PERSISTENT STATE & KNOWLEDGE
═══════════════════════════════════════════════════════════════════════════════

The running hive automatically maintains:

  • /workspaces/QL/data/processed/hive_state.json
    - Recent agent thoughts (last 100)
    - Supervision reports (last 50)
    - Current hive status

  • /workspaces/QL/data/processed/hive_memory.json
    - Verified patterns (learned)
    - Known errors (to avoid)
    - Optimization tips
    - Style guide

  • /workspaces/QL/data/processed/knowledge_graph.json
    - Complete research findings
    - Theory relationships
    - Citation tracking

All files are JSON for easy inspection:

    cat /workspaces/QL/data/processed/hive_state.json | python -m json.tool


═══════════════════════════════════════════════════════════════════════════════
🚀 RECOMMENDED SETUP FOR YOUR LAB
═══════════════════════════════════════════════════════════════════════════════

For SageMaker Studio Lab (your environment):

Step 1: Create execution script

    #!/bin/bash
    cd /workspaces/QL
    python hive_continuous.py --batch-size 3 --interval 300

Step 2: Make it executable

    chmod +x run_hive.sh

Step 3: Run in background

    ./start_hive.sh 3 300

Step 4: Monitor progress

    In Terminal 1: ./monitor_hive.sh
    In Terminal 2: streamlit run frontend/streamlit_dashboard.py

Step 5: Stop when done

    ./stop_hive.sh


═══════════════════════════════════════════════════════════════════════════════
📋 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problem: Hive stops after X batches
Solution: Check logs, verify database connection, restart with same parameters

Problem: High memory usage
Solution: Reduce batch size or increase interval between runs

Problem: Database errors
Solution: Hive continues with mathematical auditing, check DATABASE_URL in .env

Problem: Slow processing
Solution: Reduce batch size (-batch-size 1) or increase interval (--interval 600)

Problem: Can't attach to screen/tmux
Solution: Session may have ended, start a new one

Problem: Lost output
Solution: All logs saved to /workspaces/QL/logs/ - check there


═══════════════════════════════════════════════════════════════════════════════
✨ WHAT "RUNNING WITHOUT STOP" MEANS
═══════════════════════════════════════════════════════════════════════════════

Your hive now:

  ✓ Continuously analyzes Muqattaat sequences
  ✓ Runs in background (doesn't block your terminal)
  ✓ Auto-recovers from errors (up to 3 retries)
  ✓ Saves state regularly (every 3 batches)
  ✓ Learns from experience (shared memory)
  ✓ Can be monitored anytime (logs + dashboard)
  ✓ Can be stopped gracefully (Ctrl+C in tmux/screen)
  ✓ Handles all failures automatically

This is production-ready continuous analysis!


═══════════════════════════════════════════════════════════════════════════════
🎯 QUICK COMMAND REFERENCE
═══════════════════════════════════════════════════════════════════════════════

Start hive (simple):
  nohup python hive_continuous.py --batch-size 3 --interval 300 > hive.log 2>&1 &

Start hive (script):
  ./start_hive.sh 3 300

Stop hive:
  ./stop_hive.sh

Monitor logs:
  ./monitor_hive.sh

Watch dashboard:
  streamlit run frontend/streamlit_dashboard.py

Check process:
  ps aux | grep hive_continuous

Kill if stuck:
  pkill -9 -f hive_continuous

View recent logs:
  tail -50 /workspaces/QL/logs/hive_*.log

Check hive status:
  python -c "from src.agents.hive_council import get_hive_council; hive = get_hive_council(); print(hive.get_hive_status())"


═══════════════════════════════════════════════════════════════════════════════
✅ YOU'RE READY!
═══════════════════════════════════════════════════════════════════════════════

Your hive is configured to run continuously with:
  ✓ Automatic error recovery
  ✓ Periodic state saving
  ✓ Full monitoring
  ✓ Graceful degradation
  ✓ Production-ready logging

Choose your preferred method above and start analyzing!
""")
