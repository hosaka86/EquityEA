# Equity Monitor EA - Version History

## Version Tracking
This document tracks all releases and features of the Equity Monitor EA.

---

## Version History

### **v1.00** - Initial Release (Current)
**Release Date:** 2025-12-15

**Core Features:**
- Real-time equity and drawdown monitoring
- Equity-based peak tracking (includes floating P/L)
- Maximum drawdown tracking (absolute & percentage)
- Professional dashboard display on chart

**Trading Statistics:**
- Total trades counter (winning/losing breakdown)
- Win rate calculation (%)
- Net profit/loss tracking
- Daily P/L monitoring (auto-resets at day change)

**File Management:**
- Auto-save functionality (configurable interval)
- CSV export format for statistics
- Auto-load previous stats on restart
- Continuous monitoring across EA restarts

**Dashboard Features:**
- Configurable position (4 corners)
- Customizable colors (background, text, profit, loss)
- Adjustable font size
- Real-time updates (1-second refresh rate)
- Clean, professional layout

**Input Parameters:**
- 14 configurable inputs organized in 3 sections:
  - GENERAL: Magic Number, Comment
  - DISPLAY: Position, Colors, Font
  - FILE MANAGEMENT: Auto-save settings, Filename

**Technical Highlights:**
- Fully documented code (English) for YouTube tutorial
- Follows EA_BLUEPRINT.md standards
- Single-file architecture (~800 lines)
- Clean function naming (Is/Get/Update patterns)
- Section-based code organization

---

## Upcoming Features (Future Versions)

### Potential v1.01+
- Manual export button on dashboard
- Risk/Reward ratio tracking
- Average trade duration
- Best/Worst trade display
- Multiple timeframe analysis
- Email/Push notifications on new max DD
- Graphical equity curve display

---

## File Naming Convention
- **Pattern**: `EquityMonitor-V{MAJOR}{MINOR}{PATCH}.mq5`
- **Example**: `EquityMonitor-V100.mq5` = Version 1.00

---

## Changelog Format
Each version update should document:
1. **Features Added** - New functionality
2. **Features Modified** - Changes to existing features
3. **Bug Fixes** - Corrections and fixes
4. **Breaking Changes** - Compatibility notes

---

*Last Updated: 2025-12-15*
