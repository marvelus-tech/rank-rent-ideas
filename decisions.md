# Duplicate Message Prevention Rule

## Problem
Duplicate messages waste tokens, time, and user patience.

## Root Causes
1. Telegram delivery retries (network hiccups)
2. OpenClaw event duplication (race conditions on spawn completions)
3. Subagent spawn + yield creating double announcements

## Prevention Rules (Non-Negotiable)

### 1. Idempotency Check
Before sending ANY message:
- Check if the last message in this session (within 60 seconds) has identical content
- If yes → NO_REPLY (silent drop)
- If no → proceed

### 2. Spawn Acknowledgment Pattern
When spawning a subagent:
- **Option A**: Spawn + immediate yield (NO separate acknowledgment message)
- **Option B**: One acknowledgment message, then yield with NO_REPLY
- **NEVER**: Acknowledgment + yield with message (creates duplicate)

### 3. Completion Event Handling
When a subagent completion event arrives:
- Check if we already announced this task's status in the last 2 minutes
- If yes → NO_REPLY
- If no → send the result

### 4. Telegram-Specific
- Never send the same text twice within 60 seconds
- If a message fails to deliver, wait 5s before retry
- Use NO_REPLY for all retry attempts

## Implementation

In practice, this means:
1. Spawn subagent → NO_REPLY (or one brief acknowledgment)
2. Yield → NO_REPLY
3. Wait for completion event
4. Send result ONCE
5. If completion event fires twice → second one gets NO_REPLY

## Verification
After implementing:
- Check conversation history for duplicates
- If found → investigate which rule was violated
- Update this file with the specific case
