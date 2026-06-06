# JA1 Court Manager - Implementation Test Plan

## What Was Implemented

### 1. **Overlap Penalty System** ✅
- `computeOverlapPenalty(candidateIds)` function tracks:
  - `maxCommon`: Maximum players shared with any historical match
  - `pairCountSum`: Total pair co-occurrences across history
  - `score`: Combined weighted score (higher = worse overlap)
- Constants configured: `MAX_ALLOWED_OVERLAP=1`, `PENALTY_WEIGHT=10`, `STRICT_ATTEMPTS=30`
- Integrated into `autoMatchmake()`, `createManualMatch()`, and `chooseClosestWinrateGroup()`

### 2. **Fair Queue Mode** ✅
- Toggle button added (FairQ) in nav bar
- `shuffleWaitingQueueFair()` function selects players using:
  - `queuedAt` timestamp (longest waiters first)
  - `checkInEpoch` (fairness by session time)
  - Idle session tracking
- `chooseLowestOverlapWindow()` ranks candidates by penalty score
- Persisted to localStorage with seed order preservation

### 3. **Staged-First Flow** ✅
- `autoMatchmake()` and `createManualMatch()` now:
  1. Select 4 players from queue
  2. Mark them as 'Staged'
  3. Push match to `upNextDeck` (not directly to court)
  4. Remove from `waitingQueue`
- Players can edit/shuffle/replace staged matches before court placement
- Court placement requires explicit "Send to court" + "Confirm"

### 4. **Auto-Placement Guard (Fix)** ✅
- Added `autoFillFromDeck` flag (default: `false`) to disable automatic filling
- `processPipeline()` now guarded: only auto-fills if flag is `true`
- Toggle button "Manual" ↔ "Auto-Fill ON" in nav bar
- When **Manual** (default): 
  - Matches stay in Up Next Deck
  - Requires user to click "Send to court" + select court + click "Confirm"
- When **Auto-Fill ON**:
  - Matches auto-placed to available courts (original behavior)
- Flag persisted to localStorage

### 5. **Enhanced Match Creation UI** ✅
- Up Next Deck renders all staged matches with:
  - **Send to court** → Opens court dropdown + Confirm/Cancel buttons
  - **Shuffle** → Randomly reassign lineup (maintains 4 from available pool)
  - **Replace** → Swap one player with fairest next from queue
  - **Edit** → Inline player swaps with auto-pick helper
- Court selection dropdown shows available courts before placement

## Test Scenarios

### Test 1: Auto Match → Stays in Deck (Manual Mode)
**Steps:**
1. Ensure **Manual** toggle is active (default)
2. Add 4+ players to queue
3. Click **Auto Match**
4. **Expected:** Match appears in "Up Next Deck" (not on court)
5. Click **Send to court** on the staged match
6. Select a court from dropdown → Click **Confirm**
7. **Expected:** Match moves to court, players status → 'Playing'

### Test 2: Overlap Penalty Avoidance
**Steps:**
1. Create a match: Players A, B, C, D on Court 1
2. Complete the match (or resolve it)
3. Add 8+ players to queue (including A, B, C, D)
4. Click **Auto Match**
5. **Expected:** Selected players should prefer fresh combinations
6. Manual creation with high-overlap shows confirmation dialog

### Test 3: Fair Queue Mode
**Steps:**
1. Toggle **FairQ** ON
2. Add players with varied wait times
3. Click **Auto Match** multiple times
4. **Expected:** Players rotate fairly (longest waiters prioritized)
5. Disabled repeat pairs when possible

### Test 4: Manual Select with Edit
**Steps:**
1. Click **Manual Select**
2. Pick 4 players (or with high penalty)
3. If penalty high → Confirm dialog appears
4. After creation, click **Edit** on staged match
5. Swap a player → **Apply**
6. **Expected:** 
   - Swapped-out player returns to queue
   - New player marked 'Staged'
   - Match updates

### Test 5: Auto-Fill Toggle
**Steps:**
1. Create staged match (Manual mode active)
2. Toggle **Auto-Fill ON**
3. Have an available court
4. **Expected:** Match auto-places within ~1s
5. Toggle back to **Manual**
6. **Expected:** New matches stay in deck until explicit Send + Confirm

## Validation Checklist
- [ ] Auto Match creates match in Up Next Deck (Manual mode)
- [ ] Staged matches don't auto-place to courts by default
- [ ] "Send to court" button shows court dropdown UI
- [ ] Confirm places match on court; Cancel returns to deck
- [ ] Overlap penalty prevents repeat lineups (when avoidance enabled)
- [ ] Fair Queue mode rotates players fairly
- [ ] Edit mode allows inline player swaps
- [ ] Shuffle/Replace buttons work without auto-placement
- [ ] Auto-Fill toggle switches behavior (Manual ↔ Auto)
- [ ] All settings persist across page reload
- [ ] Player statuses update correctly (Queued → Staged → Playing)
- [ ] localStorage has `pq_autoFillFromDeck` entry

## Key Implementation Files
- **index.html**: Single-file app containing:
  - Overlap penalty: lines 443–476
  - Fair Queue: lines 392–425, 1160–1200
  - Auto Match: lines 1050–1120
  - Manual Select: lines 1486–1523
  - Send to Court: lines 545–575
  - Auto-Fill guard: line 1170–1178
  - UI toggles: lines 340–370

## Persistence Layer
All settings saved to localStorage:
- `pq_autoFillFromDeck` (new flag for manual/auto toggle)
- `pq_fairQueueMode` (fair queue toggle state)
- `pq_gameTimeMode` (game time mode state)
- `pq_upNextDeck` (staged matches)
- `pq_waitingQueue` (queue of available players)
- `pq_courts` (court state with current matches)
- `pq_players` (player stats and status)
