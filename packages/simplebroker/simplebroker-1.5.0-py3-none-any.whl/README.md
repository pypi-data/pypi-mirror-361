# SimpleBroker

*A lightweight message queue backed by SQLite. No setup required, just works.*

```bash
$ pipx install simplebroker
$ broker write tasks "ship it 🚀"
$ broker read tasks
ship it 🚀
```

SimpleBroker gives you a zero-configuration message queue that runs anywhere Python runs. It's designed to be simple enough to understand in an afternoon, yet powerful enough for real work.

## Features

- **Zero configuration** - No servers, daemons, or complex setup
- **SQLite-backed** - Rock-solid reliability with true ACID guarantees  
- **Concurrent safe** - Multiple processes can read/write simultaneously
- **Simple CLI** - Intuitive commands that work with pipes and scripts
- **Portable** - Each directory gets its own isolated `.broker.db`
- **Fast** - 1000+ messages/second throughput
- **Lightweight** - ~1500 lines of code, no external dependencies
- **Real-time** - Built-in watcher for event-driven workflows

## Installation

```bash
# Use pipx for global installation (recommended)
pipx install simplebroker

# Or install with uv to use as a library
uv add simplebroker

# Or with pip
pip install simplebroker
```

The CLI is available as both `broker` and `simplebroker`.

**Requirements:**
- Python 3.8+
- SQLite 3.35+ (released March 2021) - required for `DELETE...RETURNING` support

## Quick Start

```bash
# Create a queue and write a message
$ broker write myqueue "Hello, World!"

# Read the message (removes it)
$ broker read myqueue
Hello, World!

# Write from stdin
$ echo "another message" | broker write myqueue -

# Read all messages at once
$ broker read myqueue --all

# Peek without removing
$ broker peek myqueue

# List all queues
$ broker list
myqueue: 3

# Broadcast to all queues
$ broker broadcast "System maintenance at 5pm"

# Clean up when done
$ broker --cleanup
```

## Command Reference

### Global Options

- `-d, --dir PATH` - Use PATH instead of current directory
- `-f, --file NAME` - Database filename or absolute path (default: `.broker.db`)
  - If an absolute path is provided, the directory is extracted automatically
  - Cannot be used with `-d` if the directories don't match
- `-q, --quiet` - Suppress non-error output (intended reads excepted)
- `--cleanup` - Delete the database file and exit
- `--vacuum` - Remove claimed messages and exit
- `--version` - Show version information
- `--help` - Show help message

### Commands

| Command | Description |
|---------|-------------|
| `write <queue> <message>` | Add a message to the queue |
| `write <queue> -` | Add message from stdin |
| `read <queue> [--all] [--json] [-t\|--timestamps] [--since <ts>]` | Remove and return message(s) |
| `peek <queue> [--all] [--json] [-t\|--timestamps] [--since <ts>]` | Return message(s) without removing |
| `list [--stats]` | Show queues with unclaimed messages (use `--stats` to include claimed) |
| `delete <queue>` | Delete all messages in queue |
| `delete --all` | Delete all queues |
| `broadcast <message>` | Send message to all existing queues |
| `watch <queue> [--peek] [--json] [-t] [--since <ts>] [--quiet]` | Watch queue for new messages |
| `watch <queue> --move <dest> [--json] [-t] [--quiet]` | Watch for messages, moving all messages to `<dest>` queue |

#### Read/Peek Options

- `--all` - Read/peek all messages in the queue
- `--json` - Output in line-delimited JSON (ndjson) format for safe handling of special characters
- `-t, --timestamps` - Include timestamps in output
  - Regular format: `<timestamp>\t<message>` (tab-separated)
  - JSON format: `{"message": "...", "timestamp": <timestamp>}`
- `--since <timestamp>` - Return only messages with timestamp > the given value
  - Accepts multiple formats:
    - Native 64-bit timestamp as returned by `--timestamps` (e.g., `1837025672140161024`)
    - ISO 8601 date/datetime (e.g., `2024-01-15`, `2024-01-15T14:30:00Z`)
      - Date-only strings (`YYYY-MM-DD`) are interpreted as the beginning of that day in UTC (00:00:00Z)
      - Naive datetime strings (without timezone) are assumed to be in UTC
    - Unix timestamp in seconds (e.g., `1705329000` or from `date +%s`)
    - Unix timestamp in milliseconds (e.g., `1705329000000`)
  - **Explicit unit suffixes** (strongly recommended for scripts):
    - `1705329000s` - Unix seconds
    - `1705329000000ms` - Unix milliseconds  
    - `1705329000000000000ns` - Unix nanoseconds
    - `1837025672140161024hyb` - Native hybrid timestamp
    - **Best practice**: While automatic detection is convenient for interactive use, we strongly recommend using explicit unit suffixes in scripts and applications to ensure predictable behavior and future-proof your code
  - **Automatic disambiguation**: Integer timestamps without suffixes are interpreted based on magnitude:
    - Values < 2^44 are treated as Unix timestamps (seconds, milliseconds, or nanoseconds)
    - Values ≥ 2^44 are treated as native hybrid timestamps
    - This heuristic works reliably until the year ~2527
  - Native format: high 44 bits are milliseconds since Unix epoch, low 20 bits are a counter
  - Note: time.time() returns seconds, so the native format is `int(time.time() * 1000) << 20`
  - Most effective when used with `--all` to process all new messages since a checkpoint
  - Without `--all`, it finds the oldest message in the queue that is newer than `<timestamp>` and returns only that single message

### Exit Codes

- `0` - Success
- `1` - General error
- `2` - Queue is empty

## Examples

### Basic Queue Operations

```bash
# Create a work queue
$ broker write work "process customer 123"
$ broker write work "process customer 456"

# Worker processes tasks
$ while msg=$(broker read work 2>/dev/null); do
    echo "Processing: $msg"
    # do work...
done
```

### Using Multiple Queues

```bash
# Different queues for different purposes
$ broker write emails "send welcome to user@example.com"
$ broker write logs "2023-12-01 system started"
$ broker write metrics "cpu_usage:0.75"

$ broker list
emails: 1
logs: 1
metrics: 1
```

### Fan-out Pattern

```bash
# Send to all queues at once
$ broker broadcast "shutdown signal"

# Each worker reads from its own queue
$ broker read worker1  # -> "shutdown signal"
$ broker read worker2  # -> "shutdown signal"
```

**Note on broadcast behavior**: The `broadcast` command sends a message to all *existing* queues at the moment of execution. There's a small race window - if a new queue is created after the broadcast starts but before it completes, that queue won't receive the message. This is by design to keep the operation simple and atomic.

## Integration with Unix Tools

```bash
# Store command output
$ df -h | broker write monitoring -
$ broker peek monitoring

# Process files through a queue
$ find . -name "*.log" | while read f; do
    broker write logfiles "$f"
done

# Parallel processing with xargs
$ broker read logfiles --all | xargs -P 4 -I {} process_log {}

# Use absolute paths for databases in specific locations
$ broker -f /var/lib/myapp/queue.db write tasks "backup database"
$ broker -f /var/lib/myapp/queue.db read tasks
```

### Safe Handling with JSON Output

Messages containing newlines, quotes, or other special characters can break shell pipelines. The `--json` flag provides a safe way to handle any message content:

```bash
# Problem: Messages with newlines break shell processing
$ broker write alerts "ERROR: Database connection failed\nRetrying in 5 seconds..."
$ broker read alerts | wc -l
2  # Wrong! This is one message, not two

# Solution: Use --json for safe handling
$ broker write alerts "ERROR: Database connection failed\nRetrying in 5 seconds..."
$ broker read alerts --json
{"message": "ERROR: Database connection failed\nRetrying in 5 seconds..."}

# Parse JSON safely in scripts
$ broker read alerts --json | jq -r '.message'
ERROR: Database connection failed
Retrying in 5 seconds...

# Multiple messages with --all --json (outputs ndjson)
$ broker write safe "Line 1\nLine 2"
$ broker write safe 'Message with "quotes"'
$ broker write safe "Tab\there"
$ broker read safe --all --json
{"message": "Line 1\nLine 2"}
{"message": "Message with \"quotes\""}
{"message": "Tab\there"}

# Parse each line with jq
$ broker read safe --all --json | jq -r '.message'
Line 1
Line 2
Message with "quotes"
Tab	here
```

The JSON output uses line-delimited JSON (ndjson) format:
- Each message is output on its own line as: `{"message": "content"}`
- This format is streaming-friendly and works well with tools like `jq`

This is the recommended approach for handling messages that may contain special characters, as mentioned in the Security Considerations section.

## Timestamps

### Using Timestamps for Message Ordering

The `-t/--timestamps` flag includes message timestamps in the output, useful for debugging and understanding message order:

```bash
# Write some messages
$ broker write events "server started"
$ broker write events "user login"
$ broker write events "file uploaded"

# View with timestamps (non-destructive peek)
$ broker peek events --all --timestamps
1837025672140161024	server started
1837025681658085376	user login
1837025689412308992	file uploaded

# Read with timestamps and JSON for parsing
$ broker read events --all --timestamps --json
{"message": "server started", "timestamp": 1837025672140161024}
{"message": "user login", "timestamp": 1837025681658085376}
{"message": "file uploaded", "timestamp": 1837025689412308992}

# Extract just timestamps with jq
$ broker peek events --all --timestamps --json | jq '.timestamp'
1837025672140161024
1837025681658085376
1837025689412308992
```

Timestamps are 64-bit hybrid values that serve dual purposes as both timestamps and unique message IDs:
- High 44 bits: milliseconds since Unix epoch (equivalent to `int(time.time() * 1000)`)
- Low 20 bits: logical counter for ordering within the same millisecond
- Guaranteed monotonically increasing timestamps even for rapid writes
- Each timestamp is unique within the system and can be used as a message identifier

### Using Timestamps as Message IDs

Since each timestamp is guaranteed to be globally unique (enforced by a database constraint),
you can use them as message identifiers for tracking, deduplication, or correlation:

```bash
# Save message ID for later reference
$ result=$(broker write events "user_signup" | broker read events --timestamps --json)
$ msg_id=$(echo "$result" | jq '.timestamp')
$ echo "Processed signup event: $msg_id"
Processed signup event: 1837025672140161024

# Use timestamp as correlation ID in logs
$ broker write tasks "process_order_123"
$ broker read tasks --timestamps --json | jq -r '"Task ID: \(.timestamp) - \(.message)"'
Task ID: 1837025681658085376 - process_order_123

# Track message processing status
$ broker write jobs "generate_report"
$ job_id=$(broker read jobs --timestamps --json | jq '.timestamp')
$ echo "$job_id:pending" | broker write job_status -
$ # ... after processing ...
$ echo "$job_id:complete" | broker write job_status -

```

The timestamp format provides several advantages over traditional UUIDs:
- **Time-ordered**: Messages naturally sort by creation time
- **Compact**: 64-bit integers vs 128-bit UUIDs
- **Meaningful**: Can extract creation time from the ID
- **No collisions**: Guaranteed unique even with concurrent writers

This makes SimpleBroker timestamps useful for distributed systems that need both
unique identification and temporal ordering, similar to Twitter's Snowflake IDs
or UUID7, with uniqueness guarantees enforced at the database level.

### Checkpoint-based Processing

The `--since` flag enables checkpoint-based consumption patterns, enabling resilient processing:

```bash
# Process initial messages
$ broker write tasks "task 1"
$ broker write tasks "task 2"

# Read first task and save its timestamp
$ result=$(broker read tasks --timestamps)
$ checkpoint=$(echo "$result" | cut -f1)
$ echo "Processed: $(echo "$result" | cut -f2)"

# More tasks arrive while processing
$ broker write tasks "task 3"
$ broker write tasks "task 4"

# Resume from checkpoint - only get new messages
$ broker read tasks --all --since "$checkpoint"
task 2
task 3
task 4

# Alternative: Use human-readable timestamps
$ broker peek tasks --all --since "2024-01-15T14:30:00Z"
task 3
task 4

# Or use Unix timestamp from date command
$ broker peek tasks --all --since "$(date -d '1 hour ago' +%s)"
task 4
```

This pattern is perfect for:
- Resumable batch processing
- Fault-tolerant consumers
- Incremental data pipelines
- Distributed processing with multiple consumers

Note that simplebroker may return 0 (SUCCESS) even if no messages are returned if the
queue exists and has messages, but none match the --since filter.

**Edge case with future timestamps**: If you provide a `--since` timestamp that's in the future,
no messages will match the filter (since all existing messages have past timestamps). The command
will return exit code 0 if the queue exists with messages, or exit code 2 if the queue is empty
or doesn't exist. This behavior is consistent with the filter semantics - the query succeeded but
found no matching messages.


## Real-time Queue Watching

The `watch` command provides three modes for monitoring queues:

1. **Consume** (default): Process and remove messages from the queue
2. **Peek** (`--peek`): Monitor messages without removing them
3. **Move** (`--move DEST`): Drain ALL messages to another queue

```bash
# Start watching a queue (consumes messages)
$ broker watch tasks
# Blocks and prints each message as it arrives

# Watch without consuming (peek mode)
$ broker watch tasks --peek
# Monitors messages without removing them

# Watch with timestamps and JSON output
$ broker watch tasks --json --timestamps
{"message": "task 1", "timestamp": 1837025672140161024}
{"message": "task 2", "timestamp": 1837025681658085376}

# Watch from a specific timestamp (not compatible with --move)
$ broker watch tasks --since "2024-01-15T14:30:00Z"
# Only shows messages newer than the given timestamp

# Suppress the "Watching queue..." startup message
$ broker watch tasks --quiet
# Useful for scripts and automation

# Move ALL messages from one queue to another, echoing each to stdout
$ broker watch source_queue --move destination_queue
# Continuously drains source queue to destination
```

#### Move Mode (`--move`)

The `--move` option provides continuous queue-to-queue message migration. Think of it like `tail -f` for queues - you see everything flowing through, but the messages continue on to their destination:

```bash
# Like: tail -f /var/log/app.log | tee -a /var/log/processed.log
$ broker watch source_queue --move dest_queue
```

Key characteristics:
- **Drains entire queue**: Moves ALL messages from source to destination
- **Atomic operation**: Each message is atomically moved before being displayed
- **No filtering**: Incompatible with `--since` (would leave messages stranded)
- **Complete ownership**: Assumes exclusive control of the source queue

**⚠️ IMPORTANT**: `--move` mode is designed to **drain ALL messages** from the source queue. Unlike `--peek` or consume modes, it cannot be filtered with `--since` because this would leave older messages permanently stranded in the source queue with no way to process them.

**Concurrent Usage**: Multiple move watchers can safely run on the same queues without data loss or duplication. Each message is atomically moved exactly once. However, for best performance with very large queues (>100K messages), consider using a single move watcher to minimize lock contention.

**Important ordering note**: When using `--move` with a destination queue that has multiple producers, the moved messages may interleave with messages from other sources. While messages from the watched queue maintain their relative order, the overall ordering in the destination queue depends on the timing of writes from all producers.

Example use case:
```bash
# Observe a filtered stream while moving all messages
# This will move ALL messages from 'intake' to 'priority_tasks',
# but only print the ones containing "urgent"
$ broker watch intake --move priority_tasks --json | \
  jq 'select(.message | contains("urgent"))'
```

The watcher uses an efficient polling strategy with PRAGMA data_version for low-overhead change detection:
- **Burst mode**: First 100 checks with zero delay for immediate message pickup
- **Smart backoff**: Gradually increases polling interval to 0.1s maximum
- **Low overhead**: Uses SQLite's data_version to detect changes without querying
- **Graceful shutdown**: Handles Ctrl-C (SIGINT) cleanly

Perfect for:
- Real-time log processing
- Event-driven workflows
- Long-running worker processes
- Development and debugging

#### ⚠️ IMPORTANT: Message Loss in Consuming Mode

When using `watch` in consuming mode (the default, without `--peek`), messages are **permanently removed from the queue** as soon as they are read, **before** your handler processes them. This means:

- **If your handler fails**, the message is already gone and cannot be recovered
- **If your process crashes**, any messages read but not yet processed are lost
- **There is no built-in retry mechanism** for failed messages

For critical messages where data loss is unacceptable, use one of these patterns:

1. **Peek mode with manual acknowledgment** (recommended):
   ```bash
   # Watch without consuming
   broker watch tasks --peek --json | while IFS= read -r line; do
       message=$(echo "$line" | jq -r '.message')
       timestamp=$(echo "$line" | jq -r '.timestamp')
       
       # Process the message
       if process_task "$message"; then
           # Only remove after successful processing
           broker read tasks --since "$((timestamp - 1))" >/dev/null
       else
           echo "Failed to process, message remains in queue" >&2
       fi
   done
   ```

2. **Use the Python API with error handling**:
   ```python
   from simplebroker import Queue, QueueWatcher
   
   def handle_error(exception, message, timestamp):
       # Log error and keep the message for retry
       error_queue = Queue("failed-tasks")
       error_queue.write(f"{message}|{exception}")
       return True  # Continue watching
   
   watcher = QueueWatcher(
       queue=Queue("tasks"),
       handler=process_task,
       error_handler=handle_error,
       peek=True  # Use peek mode for safety
   )
   ```

3. **Write to an error queue on failure**:
   ```bash
   broker watch tasks --json | while IFS= read -r line; do
       message=$(echo "$line" | jq -r '.message')
       
       if ! process_task "$message"; then
           # Message is gone, but save it for manual recovery
           echo "$message" | broker write failed-tasks -
       fi
   done
   ```

Example worker script using watch:
```bash
#!/bin/bash
# worker.sh - Process tasks in real-time

broker watch tasks --json | while IFS= read -r line; do
    message=$(echo "$line" | jq -r '.message')
    echo "Processing: $message"
    
    # Your processing logic here
    if ! process_task "$message"; then
        echo "Failed to process: $message" >&2
        # Could write to an error queue
        echo "$message" | broker write failed-tasks -
    fi
done
```

### Robust Worker with Checkpointing

Here's a complete example of a resilient worker that processes messages in batches and can resume from where it left off after failures:

```bash
#!/bin/bash
# resilient-worker.sh - Process messages with checkpoint recovery

QUEUE="events"
CHECKPOINT_FILE="/var/lib/myapp/checkpoint"
BATCH_SIZE=100

# Load last checkpoint (default to 0 if first run)
if [ -f "$CHECKPOINT_FILE" ]; then
    last_checkpoint=$(cat "$CHECKPOINT_FILE")
else
    last_checkpoint=0
fi

echo "Starting from checkpoint: $last_checkpoint"

# Main processing loop
while true; do
    # Check if there are messages newer than our checkpoint
    if ! broker peek "$QUEUE" --json --timestamps --since "$last_checkpoint" >/dev/null 2>&1; then
        echo "No new messages, sleeping..."
        sleep 5
        continue
    fi
    
    echo "Processing new messages..."
    
    # Process messages one at a time to avoid data loss
    processed=0
    while [ $processed -lt $BATCH_SIZE ]; do
        # Read exactly one message newer than checkpoint
        message_data=$(broker read "$QUEUE" --json --timestamps --since "$last_checkpoint" 2>/dev/null)
        
        # Check if we got a message
        if [ -z "$message_data" ]; then
            echo "No more messages to process"
            break
        fi
        
        # Extract message and timestamp
        message=$(echo "$message_data" | jq -r '.message')
        timestamp=$(echo "$message_data" | jq -r '.timestamp')
        
        # Process the message (your business logic here)
        echo "Processing: $message"
        if ! process_event "$message"; then
            echo "Error processing message, will retry on next run"
            echo "Checkpoint remains at last successful message: $last_checkpoint"
            # Exit without updating checkpoint - failed message will be reprocessed
            exit 1
        fi
        
        # Atomically update checkpoint ONLY after successful processing
        echo "$timestamp" > "$CHECKPOINT_FILE.tmp"
        mv "$CHECKPOINT_FILE.tmp" "$CHECKPOINT_FILE"
        
        # Update our local variable for next iteration
        last_checkpoint="$timestamp"
        processed=$((processed + 1))
    done
    
    if [ $processed -eq 0 ]; then
        echo "No messages processed, sleeping..."
        sleep 5
    else
        echo "Batch complete, processed $processed messages, checkpoint at: $last_checkpoint"
    fi
done
```

Key features of this pattern:
- **No data loss from pipe buffering**: Reads messages one at a time instead of using dangerous pipe patterns
- **Atomic checkpoint updates**: Uses temp file + rename for crash safety
- **Per-message checkpointing**: Updates checkpoint after each successful message (no data loss)
- **Batch processing**: Processes up to BATCH_SIZE messages at a time for efficiency
- **Failure recovery**: On error, exits without updating checkpoint so failed message is retried
- **Efficient polling**: Only queries for new messages (timestamp > checkpoint)
- **Progress tracking**: Checkpoint file persists exact progress across restarts

### Remote Queue via SSH

```bash
# Write to remote queue
$ echo "remote task" | ssh server "cd /app && broker write tasks -"

# Read from remote queue  
$ ssh server "cd /app && broker read tasks"
```

## Python Library Usage

While SimpleBroker is designed for CLI use, it also provides a Python API for more advanced use cases:

### Custom Error Handling with QueueWatcher

The `QueueWatcher` class allows you to watch a queue programmatically with custom error handling:

```python
from simplebroker import Queue, QueueWatcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_message(message: str, timestamp: int) -> None:
    """Process a single message from the queue.
    
    Args:
        message: The message content
        timestamp: The unique message ID (hybrid timestamp)
    """
    # The timestamp serves as a unique message identifier
    print(f"Processing message ID {timestamp}: {message}")
    
    # Your message processing logic here
    if "error" in message.lower():
        raise ValueError(f"Message contains error keyword: {message}")
    print(f"Processed: {message}")

def handle_error(exception: Exception, message: str, timestamp: int) -> bool | None:
    """
    Custom error handler called when process_message raises an exception.
    
    Args:
        exception: The exception that was raised
        message: The message that caused the error
        timestamp: The message timestamp
        
    Returns:
        - False: Stop watching the queue
        - True or None: Continue watching the queue
    """
    logger.error(f"Error processing message: {exception}")
    logger.error(f"Failed message: {message} (timestamp: {timestamp})")
    
    # Example: Stop watching on critical errors
    if isinstance(exception, KeyboardInterrupt):
        return False  # Stop watching
    
    # Example: Log error and continue for recoverable errors
    if isinstance(exception, ValueError):
        # Could write to an error queue for later processing
        error_queue = Queue("errors")
        error_queue.write(f"Failed at {timestamp}: {message} - {exception}")
        return True  # Continue watching
    
    # Default: Continue watching for unknown errors
    return True

# Create queue and watcher
queue = Queue("tasks")
watcher = QueueWatcher(
    queue=queue,
    handler=process_message,
    error_handler=handle_error,  # Optional: handles errors from process_message
    peek=False  # False = consume messages, True = just observe
)

# Start watching (blocks until stopped)
try:
    watcher.watch()
except KeyboardInterrupt:
    print("Watcher stopped by user")
```

The error handler is called whenever the main message handler raises an exception. This allows you to:
- Log errors with full context (exception, message, and timestamp)
- Decide whether to continue watching or stop based on the error type
- Move failed messages to an error queue for later investigation
- Implement custom retry logic or alerting

Without an error handler, exceptions from the message handler will bubble up and stop the watcher.

## Design Philosophy

SimpleBroker follows the Unix philosophy: do one thing well. It's not trying to replace RabbitMQ or Redis - it's for when you need a queue without the complexity.

**What SimpleBroker is:**
- A simple, reliable message queue
- Perfect for scripts, cron jobs, and small services
- Easy to understand and debug
- Portable between environments

**What SimpleBroker is not:**
- A distributed message broker
- A pub/sub system
- A replacement for production message queues
- Suitable for high-frequency trading

## Technical Details

### Storage

Messages are stored in a SQLite database with Write-Ahead Logging (WAL) enabled for better concurrency. Each message is stored with:

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Ensures strict FIFO ordering
    queue TEXT NOT NULL,
    body TEXT NOT NULL,
    ts INTEGER NOT NULL UNIQUE             -- Unique hybrid timestamp serves as message ID
)
```

The `id` column guarantees global FIFO ordering across all processes. However, this is
an internal implementation detail not exposed to users. Instead, the `ts` column serves
as the public message identifier. With its UNIQUE constraint and hybrid timestamp algorithm
(combining physical time and a logical counter), timestamps are guaranteed to be globally
unique across all processes and can be used as message IDs, similar to how UUID7 provides
both unique identification and time-ordering in a single value.

### Concurrency

SQLite's built-in locking handles concurrent access. Multiple processes can safely read and write simultaneously. Messages are delivered **exactly once** by default using atomic `DELETE...RETURNING` operations.

**Delivery Guarantees**
- **Default behavior**: All reads (single and bulk) provide exactly-once delivery with immediate commits
- **Performance optimization**: For bulk reads (`--all`), you can trade safety for speed by setting `BROKER_READ_COMMIT_INTERVAL` to a number greater than 1 to batch messages. If a consumer crashes mid-batch, uncommitted messages remain in the queue and will be redelivered to the next consumer (at-least-once delivery).

**FIFO Ordering Guarantee:**
- **True FIFO ordering across all processes**: Messages are always read in the exact order they were written to the database, regardless of which process wrote them
- **Guaranteed by SQLite's autoincrement**: Each message receives a globally unique, monotonically increasing ID
- **No ordering ambiguity**: Even when multiple processes write simultaneously, SQLite ensures strict serialization

### Message Lifecycle and Claim Optimization

SimpleBroker uses a two-phase message lifecycle for performance optimization that's transparent to users:

1. **Claim Phase**: When messages are read, they're marked as "claimed" instead of being immediately deleted. This allows for extremely fast read operations (~3x faster) by avoiding expensive DELETE operations in the critical path.

2. **Vacuum Phase**: Claimed messages are periodically cleaned up by an automatic background process or manually via the `broker --vacuum` command. This ensures the database doesn't grow unbounded while keeping read operations fast.

This optimization is completely transparent - messages are still delivered exactly once, and from the user's perspective, a read message is gone. The cleanup happens automatically based on configurable thresholds.

**Note on `list` command**: By default, `broker list` only shows queues with unclaimed messages. To see all queues including those with only claimed messages awaiting vacuum, use `broker list --stats`. This also displays claim statistics for each queue.

### Performance

- **Throughput**: 1000+ messages/second on typical hardware
- **Latency**: <10ms for write, <10ms for read
- **Scalability**: Tested with 100k+ messages per queue
- **Read optimization**: ~3x faster reads due to the claim-based message lifecycle optimization

**Note on CLI vs Library Usage**: For CLI-only use, startup cost predominates the overall performance. If you need to process 1000+ messages per second, use the library interface directly to avoid the overhead of repeated process creation.

### Security

- Queue names are validated (alphanumeric + underscore + hyphen + period only, can't start with hyphen or period)
- Message size limited to 10MB
- Database files created with 0600 permissions
- SQL injection prevented via parameterized queries

**Security Considerations:**
- **Message bodies are not validated** - they can contain any text including newlines, control characters, and shell metacharacters
- **Shell injection risks** - When piping output to shell commands, malicious message content could execute unintended commands
- **Special characters** - Messages containing newlines or other special characters can break shell pipelines that expect single-line output
- **Recommended practice** - Always sanitize or validate message content before using it in shell commands or other security-sensitive contexts

### Tuning Watcher Performance

The `watch` command's polling behavior can be tuned via environment variables:

- `SIMPLEBROKER_INITIAL_CHECKS` - Number of checks with zero delay (default: 100)
  - Controls the "burst mode" duration for immediate message pickup
  - Higher values are better for high-throughput scenarios
- `SIMPLEBROKER_MAX_INTERVAL` - Maximum polling interval in seconds (default: 0.1)
  - Controls the backoff ceiling when no messages are available
  - Lower values reduce latency but increase CPU usage

Example:
```bash
# High-throughput configuration
export SIMPLEBROKER_INITIAL_CHECKS=1000  # Longer burst mode
export SIMPLEBROKER_MAX_INTERVAL=0.05    # Faster polling

# Low-latency configuration  
export SIMPLEBROKER_INITIAL_CHECKS=500   # Extended burst
export SIMPLEBROKER_MAX_INTERVAL=0.01    # Very responsive

# Power-saving configuration
export SIMPLEBROKER_INITIAL_CHECKS=50    # Short burst
export SIMPLEBROKER_MAX_INTERVAL=0.5     # Longer sleep
```

### Environment Variables

SimpleBroker can be configured via environment variables:

- `BROKER_BUSY_TIMEOUT` - SQLite busy timeout in milliseconds (default: 5000)
- `BROKER_CACHE_MB` - SQLite page cache size in megabytes (default: 10)
  - Larger cache improves performance for repeated queries and large scans
  - Recommended: 10-50 MB for typical workloads, 100+ MB for heavy use
- `BROKER_SYNC_MODE` - SQLite synchronous mode: FULL, NORMAL, or OFF (default: FULL)
  - `FULL`: Maximum durability, safe against power loss (default)
  - `NORMAL`: ~25% faster writes, safe against app crashes, small risk on power loss
  - `OFF`: Fastest but unsafe - only for testing or non-critical data
- `BROKER_READ_COMMIT_INTERVAL` - Number of messages to read before committing in `--all` mode (default: 1)
  - Default of 1 provides exactly-once delivery guarantee (~10,000 messages/second)
  - Increase for better performance with at-least-once delivery guarantee
  - With values > 1, messages are only deleted after being successfully delivered
  - Trade-off: larger batches hold database locks longer, reducing concurrency
- `BROKER_AUTO_VACUUM` - Enable automatic vacuum of claimed messages (default: true)
  - When enabled, vacuum runs automatically when thresholds are exceeded
  - Set to `false` to disable automatic cleanup and run `broker vacuum` manually
- `BROKER_VACUUM_THRESHOLD` - Number of claimed messages before auto-vacuum triggers (default: 10000)
  - Higher values reduce vacuum frequency but use more disk space
  - Lower values keep the database smaller but run vacuum more often
- `BROKER_VACUUM_BATCH_SIZE` - Number of messages to delete per vacuum batch (default: 1000)
  - Larger batches are more efficient but hold locks longer
  - Smaller batches are more responsive but less efficient
- `BROKER_VACUUM_LOCK_TIMEOUT` - Seconds before a vacuum lock is considered stale (default: 300)
  - Prevents orphaned lock files from blocking vacuum operations
  - Lock files older than this are automatically removed

## Development

SimpleBroker uses [`uv`](https://github.com/astral-sh/uv) for package management and [`ruff`](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Clone the repository
git clone git@github.com:VanL/simplebroker.git
cd simplebroker

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies including dev extras
uv sync --all-extras

# Run tests (fast tests only, in parallel)
uv run pytest

# Run all tests including slow ones (with 1000+ subprocess spawns)
uv run pytest -m ""

# Run tests with coverage
uv run pytest --cov=simplebroker --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_smoke.py

# Run tests in a single process (useful for debugging)
uv run pytest -n 0

# Lint and format code
uv run ruff check simplebroker tests  # Check for issues
uv run ruff check --fix simplebroker tests  # Fix auto-fixable issues
uv run ruff format simplebroker tests  # Format code

# Type check
uv run mypy simplebroker
```

### Development Workflow

1. **Before committing**:
   ```bash
   uv run ruff check --fix simplebroker tests
   uv run ruff format simplebroker tests
   uv run mypy simplebroker
   uv run pytest
   ```

2. **Building packages**:
   ```bash
   uv build  # Creates wheel and sdist in dist/
   ```

3. **Installing locally for testing**:
   ```bash
   uv pip install dist/simplebroker-*.whl
   ```

## Contributing

Contributions are welcome! Please:

1. Keep it simple - the entire codebase should stay understandable in an afternoon
2. Maintain backward compatibility
3. Add tests for new features
4. Update documentation
5. Run `uv run ruff` and `uv run pytest` before submitting PRs

### Setting up for development

```bash
# Fork and clone the repo
git clone git@github.com:VanL/simplebroker.git
cd simplebroker

# Install development environment
uv sync --all-extras

# Create a branch for your changes
git checkout -b my-feature

# Make your changes, then validate
uv run ruff check --fix simplebroker tests
uv run ruff format simplebroker tests
uv run pytest

# Push and create a pull request
git push origin my-feature
```

## License

MIT © 2025 Van Lindberg

## Acknowledgments

Built with Python, SQLite, and the Unix philosophy. 
