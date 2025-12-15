# Equity Monitor EA

**Advanced Equity & Drawdown Tracking for MetaTrader 5**

Version 1.00 | Developed for YouTube Tutorial

---

## Overview

Equity Monitor EA is a professional monitoring tool designed to accurately track your account's equity, drawdown, and trading statistics in real-time. Unlike external tracking services (like FXBlue) which may not capture drawdown accurately, this EA monitors every tick directly in your MT5 terminal.

### Why Use This EA?

- **Accurate Drawdown Tracking**: Measures from highest equity point (not just balance)
- **Real-time Updates**: Dashboard updates every second
- **Persistent Statistics**: Auto-saves and reloads stats across restarts
- **No External Dependencies**: Everything runs locally in MT5
- **Educational Code**: Fully documented in English for learning purposes

---

## Features

### ✅ Equity & Drawdown Monitoring
- Peak equity tracking (highest equity ever reached)
- Current drawdown (absolute & percentage)
- Maximum historical drawdown
- Real-time floating P/L display

### ✅ Trading Statistics
- Total trades count with W/L breakdown
- Win rate percentage
- Net profit/loss tracking
- Daily P/L (automatically resets each day)

### ✅ Professional Dashboard
- Clean, modern UI displayed on chart
- Configurable position (4 corners available)
- Color-coded values (green = profit, red = loss)
- Customizable appearance (colors, fonts, sizes)

### ✅ Data Persistence
- Auto-save to CSV file (configurable interval)
- Automatic loading of previous statistics on restart
- No data loss between EA restarts or terminal restarts
- Manual save on EA shutdown

---

## Installation

1. **Copy the EA file:**
   ```
   EquityMonitor-V100.mq5 → MQL5/Experts/
   ```

2. **Compile in MetaEditor:**
   - Open MetaEditor (F4 in MT5)
   - Open `EquityMonitor-V100.mq5`
   - Click "Compile" (F7)
   - Verify no errors

3. **Attach to Chart:**
   - Drag EA from Navigator onto any chart
   - Configure inputs as desired
   - Click "OK"

---

## Configuration

### General Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Magic Number | 0 | Filter trades by magic (0 = all trades) |
| EA Comment | EquityMonitor | EA identifier |

### Display Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Show Dashboard | true | Enable/disable dashboard |
| Dashboard Position | Top Left | Corner position (4 options) |
| X Offset | 10 | Horizontal offset in pixels |
| Y Offset | 20 | Vertical offset in pixels |
| Font Size | 9 | Text font size |
| Background Color | Dark Gray | Dashboard background |
| Text Color | White | Default text color |
| Profit Color | Lime Green | Color for positive values |
| Loss Color | Red | Color for negative values |

### File Management
| Parameter | Default | Description |
|-----------|---------|-------------|
| Enable Auto-Save | true | Automatic statistics saving |
| Auto-Save Interval | 60 | Save interval in minutes |
| Filename | EquityMonitor_Stats.csv | Stats file name |

---

## How It Works

### Equity-Based Drawdown Calculation

```
Peak Equity = Highest equity ever reached (Balance + Floating P/L)
Current Drawdown = Peak Equity - Current Equity
Drawdown % = (Current Drawdown / Peak Equity) * 100
```

**Example:**
- Peak Equity: $10,000
- Current Equity: $9,200
- Current Drawdown: $800 (8.0%)

### Statistics Tracking

The EA monitors all closed trades (deals) and calculates:
- **Win Rate**: (Winning Trades / Total Trades) * 100
- **Net Profit**: Total Profit - Total Loss
- **Daily P/L**: Sum of all trade profits/losses since midnight

### File Format

CSV file structure:
```csv
Timestamp, PeakEquity, MaxDrawdown, MaxDrawdown%, TotalTrades, ...
2025-12-15 10:30, 10000.00, 800.00, 8.00, 45, ...
```

---

## Usage Tips

### For Accurate Tracking:
1. **Start with clean account**: Attach EA at account opening for full history
2. **Keep EA running**: Continuous monitoring ensures no data gaps
3. **Don't delete stats file**: File preserves historical peak equity
4. **Use Magic Number**: Filter specific EA trades if running multiple systems

### For YouTube Videos:
- Code is fully documented in English
- Clear function names (IsXxx, GetXxx, UpdateXxx patterns)
- Section comments for easy navigation
- Examples of dashboard creation, file I/O, statistics calculation

### For Live Trading:
- Low resource usage (updates once per second)
- No trading operations (monitoring only)
- Works on any symbol/timeframe
- Compatible with other EAs running simultaneously

---

## Dashboard Sections

### Current Status
- **Balance**: Account balance (realized P/L only)
- **Equity**: Account equity (balance + floating P/L)
- **Floating P/L**: Current unrealized profit/loss

### Drawdown Analysis
- **Peak Equity**: Highest equity value reached
- **Current DD**: Active drawdown from peak
- **Max DD**: Largest historical drawdown

### Trading Statistics
- **Total Trades**: Count with W/L breakdown
- **Win Rate**: Winning percentage
- **Net Profit**: Total realized profit/loss
- **Daily P/L**: Today's profit/loss

---

## Code Structure

Following the **EA_BLUEPRINT.md** standards:

```
HEADER (Copyright, Properties, Description)
├── DEFINES (VERSION, DASHBOARD_PREFIX)
├── INCLUDES
├── ENUMERATIONS (Corner positions)
├── INPUT PARAMETERS (3 sections)
├── GLOBAL VARIABLES (Organized by category)
├── INITIALIZATION & DEINITIALIZATION
├── MAIN FUNCTIONS (OnTick)
└── HELPER FUNCTIONS (Organized by section)
    ├── Account Value Updates
    ├── Equity Tracking & Drawdown
    ├── Trading Statistics
    ├── File Management
    ├── Dashboard Visualization
    └── Utility Functions
```

---

## Troubleshooting

### Dashboard Not Visible
- Check "Show Dashboard" input is enabled
- Verify X/Y offsets don't push dashboard off-screen
- Try different corner position

### Stats Not Saving
- Check "Enable Auto-Save" is enabled
- Verify file permissions (MT5 sandbox)
- Look in `MQL5/Files/` directory
- Check Experts log for error messages

### Wrong Trade Count
- Verify Magic Number setting (0 = all trades)
- Check that history is fully loaded
- Ensure deals (not just positions) are counted

---

## YouTube Tutorial Topics

This EA demonstrates:
1. **Object-Oriented Dashboard Creation**: Label objects, positioning, updates
2. **File I/O in MQL5**: CSV reading/writing, data persistence
3. **History Analysis**: Deal iteration, profit calculation
4. **Real-time Monitoring**: Tick-by-tick updates, throttling
5. **Input Organization**: Workflow-based grouping
6. **Code Documentation**: Professional commenting style
7. **Global Variable Management**: State tracking, initialization

---

## Version History

See [VERSIONING.md](VERSIONING.md) for detailed changelog.

**Current Version: 1.00**
- Initial release with core monitoring features
- Dashboard visualization
- Auto-save/load functionality
- Full statistics tracking

---

## License

This EA is provided as educational material for YouTube tutorial purposes.

Feel free to:
- ✅ Use in personal trading
- ✅ Modify and customize
- ✅ Learn from the code
- ✅ Share with attribution

---

## Support

For questions, issues, or suggestions:
- Check code comments for implementation details
- Review EA_BLUEPRINT.md for architecture patterns
- Consult MQL5 documentation for API reference

---

## Credits

Developed following the **EA Development Blueprint** methodology.

**Code Quality Standards:**
- Single Responsibility Principle
- Descriptive function naming
- Workflow-based input organization
- Comprehensive English documentation

---

*Happy Trading & Happy Learning! 📊*
