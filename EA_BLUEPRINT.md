# EA Development Blueprint
**How to build large-scale MQL5 EAs with AI assistance**

*Based on successful patterns from NetRunner project*

---

## 1. PROJECT STRUCTURE

### File Organization
```
project/
├── EA-V{VERSION}.mq5        # Main EA file with version in name
├── VERSIONING.md            # Version tracking standards
├── EA_BLUEPRINT.md          # This document
├── helper_functions.mql5    # Optional: Extracted helper functions
└── README.md                # Optional: Project overview
```

### Version Tracking
- **Filename Pattern**: `EA-V{MAJOR}{MINOR}{PATCH}.mq5`
  - Example: `NetRunner-V154.mq5` = Version 1.54
- **#define VERSION** at top of file for dynamic display
- **#property version** in header
- **VERSIONING.md** tracks all releases with features

**Why it works:**
- AI can quickly identify current version
- Git history shows clear progression
- No confusion about which file is active

---

## 2. CODE ORGANIZATION

### File Structure (Top to Bottom)
```mql5
//+------------------------------------------------------------------+
//| HEADER (Copyright, Properties, Description)
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| DEFINES
//+------------------------------------------------------------------+
#define VERSION "1.54"
#define MAX_RETRIES 3
// etc.

//+------------------------------------------------------------------+
//| INCLUDES
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| ENUMERATIONS
//+------------------------------------------------------------------+
enum ENUM_TRADE_DIRECTION { ... };

//+------------------------------------------------------------------+
//| INPUT PARAMETERS (Grouped in Sections)
//+------------------------------------------------------------------+
// See Section 3 for details

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES
//+------------------------------------------------------------------+
// Organized by category with comments

//+------------------------------------------------------------------+
//| INITIALIZATION & DEINITIALIZATION
//+------------------------------------------------------------------+
int OnInit() { }
void OnDeinit(const int reason) { }

//+------------------------------------------------------------------+
//| MAIN FUNCTIONS (OnTick, OnChartEvent)
//+------------------------------------------------------------------+
void OnTick() { }
void OnChartEvent(...) { }

//+------------------------------------------------------------------+
//| HELPER FUNCTIONS (Alphabetically or by Category)
//+------------------------------------------------------------------+
// One clear purpose per function
// Descriptive names: IsSpreadAcceptable(), CanOpenNewEA()
```

**Why it works:**
- AI can grep and find anything instantly
- Logical flow from config → initialization → runtime
- Easy to navigate even at 2000+ lines

---

## 3. INPUT PARAMETER ORGANIZATION

### Workflow-Based Grouping
**Anti-Pattern:** Group by type (all bools together, all ints together)
**Best Practice:** Group by user workflow

**NetRunner Example:**
```mql5
//═══════════════════════════════════════════════════════════════════
//  GENERAL SETTINGS
//═══════════════════════════════════════════════════════════════════
sinput string Sep1 = "════════ GENERAL ════════";
input bool InpEnableAutoEntry = true;              // Auto Entry (MA Crossover)
input bool InpEnableTrendSignals = false;          // Auto Entry (Trend Following)
input bool InpEnableAwayMode = false;              // Away Mode
input int InpMagicNumber = 12345;                  // Magic Number

//═══════════════════════════════════════════════════════════════════
//  GRID SYSTEM
//═══════════════════════════════════════════════════════════════════
sinput string Sep2 = "════════ GRID SYSTEM ════════";
input int InpInitialDistance = 1000;               // Initial Grid Distance
```

### Section Design
1. **GENERAL**: Core settings (modes, magic, lot, TP)
2. **STRATEGY**: Core strategy parameters
3. **ENTRY METHOD 1**: First entry logic (e.g., MA Crossover)
4. **ENTRY METHOD 2**: Second entry logic (e.g., Trend Detection)
5. **MANAGEMENT**: Position/Grid management
6. **FILTERS**: All filters grouped (Time, News, Spread)
7. **VISUALIZATION**: Display settings

### Naming Convention
- **Prefix**: `Inp` for all inputs
- **Boolean**: Start with verb (`InpEnable...`, `InpAllow...`)
- **Descriptive**: `InpMaxConcurrentEAs` not `InpLimit`
- **Units in comment**: `// Max Spread (Points)`, `// Block Before (Minutes)`

**Why it works:**
- User thinks in workflow, not data types
- Easy to find related settings
- Clear hierarchy with separators
- grep "input" shows all parameters instantly

---

## 4. FUNCTION DESIGN

### Naming Patterns
```mql5
// Questions (return bool)
bool IsSpreadAcceptable()
bool CanOpenNewEA()
bool HasOpenPositions()
bool IsWithinTradingHours()

// Getters (return value)
double GetRecoveryPercentForCurrentLevel()
int GetActiveGridCount()

// Actions (return void or bool for success)
void OpenFirstPosition(ENUM_ORDER_TYPE direction)
void ManageGridLevels()
bool PerformGridCleanup()

// Checks (return signal/state)
int CheckMACrossover()  // Returns: 1=Buy, -1=Sell, 0=None
int DetectTrend()       // Returns: 1=Bullish, -1=Bearish, 0=Neutral
```

### Single Responsibility Principle
**Bad:**
```mql5
void CheckAndOpenPosition() {
   if(CheckMA()) {
      if(CheckNews()) {
         if(CheckSpread()) {
            if(CheckEALimit()) {
               OpenPosition();
            }
         }
      }
   }
}
```

**Good:**
```mql5
// In OnTick()
int signal = CheckMACrossover();
if(signal != 0) {
   if(!CanOpenNewEA()) return;
   if(!IsWithinTradingHours()) return;
   if(IsNewsEventNear()) return;
   if(!IsSpreadAcceptable()) return;

   ENUM_ORDER_TYPE direction = (signal == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(IsDirectionAllowed(direction)) {
      OpenFirstPosition(direction);
   }
}
```

**Why it works:**
- Each function testable independently
- Easy to add new filters
- Clear logic flow
- AI can modify one piece without breaking others

---

## 5. FEATURE IMPLEMENTATION WORKFLOW

### Step-by-Step Process (User + AI)

#### 1. User: Feature Request
**Good Request Format:**
```
"I want a spread filter that blocks entries when spread > X points.
Should be configurable in FILTERS section.
Check before opening all positions (signals + manual buttons)."
```

**Why it works:**
- Clear goal
- Specific integration points
- Section preference stated

#### 2. AI: Understanding Confirmation
```
"I'll implement:
- Input: InpEnableSpreadFilter + InpMaxSpreadPoints
- Function: IsSpreadAcceptable()
- Integration: 4 entry points (MA, Trend, BUY, SELL buttons)
Correct?"
```

**Why it works:**
- Confirms understanding before coding
- Lists all affected code sections
- Prevents misunderstandings

#### 3. AI: Implementation
- Add inputs to correct section
- Create helper function
- Integrate at all entry points
- Update VERSION if needed

#### 4. User: Testing Feedback
```
"undeclared identifier IsTimeFilterActive"
```

**Why it works:**
- Direct compiler error = quick fix
- No need for AI to compile
- User validates in actual environment

#### 5. AI: Fix + Git Push
- Fix identified issue
- Commit with clear message
- Push to repository

### Iteration Pattern
```
Request → Confirm → Implement → Test → Fix → Push → Repeat
```

---

## 6. GIT WORKFLOW

### Commit Message Format
```
[Action] Brief description

Detailed explanation:
- Feature 1
- Feature 2
- Integration point 3

Use Case:
- How user benefits
- Example usage

Logic:
- Key implementation details
```

**Example:**
```
Add EA limit feature for multi-symbol scanning

Features:
- Added InpEnableEALimit and InpMaxConcurrentEAs inputs
- Implemented CanOpenNewEA() function
- Counts unique Magic Numbers across all positions

Use Case:
- Run EA on multiple symbols for signal scanning
- Limit concurrent active EAs (e.g., max 2 grids at once)

Logic:
- Ignores own MagicNumber when counting
- Checks if we already have positions
```

### Rules
- ❌ **NO** Claude Code advertisement/attribution
- ✅ **YES** Clear, descriptive messages
- ✅ **YES** Mention affected functions/files if complex
- ✅ **YES** Push after every complete feature

**Why it works:**
- Git history becomes documentation
- Easy to understand what changed
- Rollback is straightforward if needed

---

## 7. AI-FRIENDLY CODE PATTERNS

### Use grep-friendly naming
```mql5
// Good: AI can find all filters easily
bool IsSpreadAcceptable()
bool IsWithinTradingHours()
bool IsNewsEventNear()
bool CanOpenNewEA()

// Bad: Inconsistent naming
bool CheckSpread()
bool TimeOK()
bool NewsFilter()
bool EALimitCheck()
```

### Comment Integration Points
```mql5
void OnTick() {
   // ... grid management code ...

   //--- Prüfe auf MA Crossover Signal (nur wenn kein Grid aktiv)
   int signal = CheckMACrossover();

   if(signal != 0) {
      // Prüfe Filter (EA Limit, Time, News, Spread)
      if(!CanOpenNewEA()) {
         Print("EA Limit erreicht!");
      }
      // ... more filters ...
   }
}
```

**Why it works:**
- AI can grep for "Prüfe Filter" to find all entry points
- Clear sectioning with comments
- Easy to add new checks in logical place

### Use Enums for Multi-State
```mql5
enum ENUM_TRADE_DIRECTION {
   TRADE_BUY_ONLY,
   TRADE_SELL_ONLY,
   TRADE_BOTH
};

// Not: bool InpAllowLongs + bool InpAllowShorts
// AI can reason about single state better than two bools
```

---

## 8. SCALING TO LARGE CODEBASES

### When to Split Files
**Keep in one file if:**
- Total < 3000 lines
- All functions related to same strategy
- Fast grep/search works fine

**Split into multiple files if:**
- > 3000 lines
- Clear subsystems (Indicators, Risk Management, UI)
- Reusable across multiple EAs

**NetRunner Status:**
- ~2000 lines
- Single file works perfectly
- Clear section structure sufficient

### Managing Complexity
```mql5
//+------------------------------------------------------------------+
//| SECTION: GRID MANAGEMENT
//+------------------------------------------------------------------+

void ManageGridLevels() { }
void PerformGridCleanup() { }
double GetRecoveryPercentForCurrentLevel() { }

//+------------------------------------------------------------------+
//| SECTION: SIGNAL DETECTION
//+------------------------------------------------------------------+

int CheckMACrossover() { }
int DetectTrend() { }
```

**Why it works:**
- AI can read section headers
- Functions grouped by purpose
- Easy to navigate with grep "SECTION:"

---

## 9. COMMON PATTERNS & SOLUTIONS

### Pattern: Multi-Entry System
```mql5
// Don't duplicate filter checks
// Use central filtering before entry

if(signal != 0) {
   if(IsDirectionAllowed(direction)) {
      // Check ALL filters once
      if(!CanOpenNewEA()) return;
      if(!IsWithinTradingHours()) return;
      if(IsNewsEventNear()) return;
      if(!IsSpreadAcceptable()) return;

      OpenFirstPosition(direction);
   }
}
```

### Pattern: Tiered Configuration
```mql5
// Allow user to configure ranges
input double InpR1RecoveryPercent = 100.0;  // R1 Recovery %
input int InpR1LastLevel = 3;               // R1 Last Level
input double InpR2RecoveryPercent = 80.0;   // R2 Recovery %
input int InpR2LastLevel = 8;               // R2 Last Level

double GetRecoveryPercentForCurrentLevel() {
   int level = GetCurrentLevel();
   if(level <= InpR1LastLevel) return InpR1RecoveryPercent;
   if(level <= InpR2LastLevel) return InpR2RecoveryPercent;
   // ...
}
```

### Pattern: Feature Flags
```mql5
// Always allow disabling features
input bool InpEnableAutoEntry = true;
input bool InpEnableTrendSignals = false;
input bool InpEnableAwayMode = false;
input bool InpEnableGridCleanup = true;
input bool InpEnableEALimit = false;

// Check flags at function start
bool CanOpenNewEA() {
   if(!InpEnableEALimit) return true;  // Feature disabled
   // ... actual logic ...
}
```

**Why it works:**
- User can enable/disable features individually
- Easy testing (turn off one feature)
- Backward compatible (default = disabled)

---

## 10. DEBUGGING & TESTING WORKFLOW

### User Responsibilities
1. **Compile in MT5** (AI cannot compile)
2. **Report exact errors** with line numbers
3. **Test on Strategy Tester or Live**
4. **Provide clear feedback**

### AI Responsibilities
1. **Never attempt to compile**
2. **Use grep to verify function names**
3. **Read code before editing**
4. **Ask before major refactoring**

### Error Reporting Format
**Good:**
```
undeclared identifier    NetRunner-V154.mq5    385    13
')' - expression expected    NetRunner-V154.mq5    385    32
```

**Also Good:**
```
"EA Limit feature works but I want it to also check
for Away Mode positions. Currently it ignores them."
```

**Why it works:**
- AI can locate exact line
- Clear description of behavior vs. expectation
- Quick iteration possible

---

## 11. PROJECT DOCUMENTATION

### Essential Files
1. **VERSIONING.md** - Track releases
2. **EA_BLUEPRINT.md** - This document (optional for small projects)
3. **README.md** - Optional, user-facing description

### Version History Format
```markdown
## Version History
- **v1.54** - Spread Filter + Improved Input Grouping (Current)
- **v1.53** - Tiered Recovery System (R1-R4)
- **v1.52** - Trend Display Always Active + Input Grouping
- **v1.51** - Version Tracking in Filename
- **v1.50** - Away Mode (Manual Position Adoption)
```

**Why it works:**
- Quick overview of feature evolution
- AI can understand project history
- User knows what version they're running

---

## 12. COMMUNICATION PATTERNS

### User → AI: Request Patterns

**Pattern 1: Feature Request**
```
"Add a [FEATURE] that [DOES X] when [CONDITION].
Should be configurable in [SECTION].
Integrate at [LOCATIONS]."
```

**Pattern 2: Bug Report**
```
"Getting error [ERROR MESSAGE] at line [X].
Expected: [BEHAVIOR A]
Actual: [BEHAVIOR B]"
```

**Pattern 3: Enhancement**
```
"The [FEATURE] works but I want it to also [DO Y].
Currently it [DOES X]."
```

### AI → User: Response Patterns

**Pattern 1: Confirmation**
```
"I'll implement:
- Input: [NAMES]
- Function: [NAME]
- Integration: [LOCATIONS]
Correct?"
```

**Pattern 2: Clarification**
```
"Should the [FEATURE] also apply to [CASE X]?
Or only for [CASE Y]?"
```

**Pattern 3: Completion**
```
"✅ [FEATURE] implemented!
- [DETAIL 1]
- [DETAIL 2]
Soll ich pushen?"
```

**Why it works:**
- Clear, structured communication
- No ambiguity
- Fast iteration

---

## 13. DO'S AND DON'TS

### DO ✅
- Use descriptive function names (`IsSpreadAcceptable` not `CheckSpread`)
- Group inputs by user workflow, not data type
- Add comments at integration points
- Keep functions small and single-purpose
- Use feature flags for optional features
- Version in filename + VERSION define
- Push to git after every complete feature
- Report exact compiler errors with line numbers

### DON'T ❌
- Don't compile code as AI (user does this)
- Don't create files "just in case" (only when needed)
- Don't duplicate filter logic across entry points
- Don't use magic numbers (use defines/inputs)
- Don't add Claude Code attribution to commits
- Don't refactor without asking first
- Don't assume variable/function names (grep first)
- Don't create docs unless explicitly requested

---

## 14. SUCCESS METRICS

**NetRunner Project Results:**
- 65 input parameters, still manageable
- ~2000 lines, single file
- 7 major features implemented iteratively
- Clean git history (10+ meaningful commits)
- Zero merge conflicts
- Code compiles without errors
- Clear feature toggles (test individually)

**What Made It Work:**
1. **Structured inputs** - Easy to find settings
2. **Clear function names** - Grep finds everything
3. **Modular features** - Add without breaking existing
4. **Git discipline** - Every feature committed separately
5. **Version tracking** - Always know what version running
6. **User-AI workflow** - Clear request → confirm → implement → test cycle

---

## 15. TEMPLATE FOR NEW EA

```mql5
//+------------------------------------------------------------------+
//|                                                  YourEA-V100.mq5 |
//|                                          Your Name / Organization |
//|                                               https://yoursite.com |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://yoursite.com"
#property version   "1.00"
#property description "Your EA - Brief description"
#property description "Version: 1.00 | Last Feature: Initial Release"

//+------------------------------------------------------------------+
//| DEFINES                                                           |
//+------------------------------------------------------------------+
#define VERSION "1.00"

//+------------------------------------------------------------------+
//| INCLUDES                                                          |
//+------------------------------------------------------------------+
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| ENUMERATIONS                                                      |
//+------------------------------------------------------------------+
// Your enums here

//+------------------------------------------------------------------+
//| INPUT PARAMETERS                                                  |
//+------------------------------------------------------------------+

//═══════════════════════════════════════════════════════════════════
//  GENERAL SETTINGS
//═══════════════════════════════════════════════════════════════════
sinput string Sep1 = "════════ GENERAL ════════";
input int InpMagicNumber = 12345;                  // Magic Number
input string InpTradeComment = "YourEA";           // Trade Comment
input double InpLotSize = 0.01;                    // Lot Size

//═══════════════════════════════════════════════════════════════════
//  STRATEGY SETTINGS
//═══════════════════════════════════════════════════════════════════
sinput string Sep2 = "════════ STRATEGY ════════";
// Your strategy inputs

//═══════════════════════════════════════════════════════════════════
//  FILTERS
//═══════════════════════════════════════════════════════════════════
sinput string Sep3 = "════════ FILTERS ════════";
// Your filter inputs

//═══════════════════════════════════════════════════════════════════
//  VISUALIZATION
//═══════════════════════════════════════════════════════════════════
sinput string Sep4 = "════════ VISUALIZATION ════════";
// Your UI inputs

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES                                                  |
//+------------------------------------------------------------------+
// Your globals

//+------------------------------------------------------------------+
//| Expert initialization function                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== ", InpTradeComment, " V", VERSION, " Initialized ===");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("=== ", InpTradeComment, " Deinitialized ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Your main logic
}

//+------------------------------------------------------------------+
//| HELPER FUNCTIONS                                                  |
//+------------------------------------------------------------------+

// Your helper functions with clear names
```

---

## 16. CONTINUOUS IMPROVEMENT

### End of Project Review Questions
1. What worked well in the workflow?
2. What slowed us down?
3. Were input groupings intuitive?
4. Were function names clear?
5. Was git history useful?
6. What would you change next time?

### Iteration
- Update this blueprint after each project
- Add new patterns that emerge
- Remove patterns that don't work
- Share learnings across projects

---

## SUMMARY

**Core Principles:**
1. **Structure** - Workflow-based organization
2. **Naming** - Descriptive, grep-friendly
3. **Modularity** - Single-responsibility functions
4. **Communication** - Clear request/confirm/implement cycle
5. **Version Control** - Git discipline, clear commits
6. **Testing** - User compiles, AI fixes based on feedback
7. **Iteration** - Small features, test, push, repeat

**This Blueprint Lives:**
- In your EA project folder
- Updated after each project
- Referenced at start of new projects
- Shared with AI at project start

**Result:**
- Fast development
- Clean codebase
- Easy maintenance
- Happy developer + Happy AI 🚀

---

*Blueprint Version: 1.0*
*Based on: NetRunner V1.54 (2000 lines, 65 inputs, 7 major features)*
*Last Updated: 2025-10-24*
