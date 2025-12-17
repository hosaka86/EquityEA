//+------------------------------------------------------------------+
//|                                            EquityMonitor-V105.mq5 |
//|                                       Developed for YouTube Tutorial |
//|                                                                      |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      ""
#property version   "1.05"
#property description "Equity Monitor EA - Advanced Drawdown Tracking"
#property description "Version: 1.05 | Reduced log spam by throttling routine messages"
#property description ""
#property description "Features:"
#property description "- Real-time equity & drawdown monitoring"
#property description "- Configurable peak tracking (equity or balance based)"
#property description "- Trading statistics (Win Rate, Total Trades, P/L)"
#property description "- Auto-save to file with import capability"
#property description "- Professional dashboard display"

//+------------------------------------------------------------------+
//| DEFINES                                                           |
//+------------------------------------------------------------------+
#define VERSION "1.05"
#define DASHBOARD_PREFIX "EM_"  // Prefix for all dashboard objects

//+------------------------------------------------------------------+
//| INCLUDES                                                          |
//+------------------------------------------------------------------+
// No additional includes needed for basic functionality

//+------------------------------------------------------------------+
//| ENUMERATIONS                                                      |
//+------------------------------------------------------------------+
enum ENUM_CORNER_POSITION
{
   CORNER_TOP_LEFT = 0,      // Top Left
   CORNER_TOP_RIGHT = 1,     // Top Right
   CORNER_BOTTOM_LEFT = 2,   // Bottom Left
   CORNER_BOTTOM_RIGHT = 3   // Bottom Right
};

/**
 * Drawdown Calculation Modes:
 *
 * DRAWDOWN_EQUITY (Equity-based):
 *   - Peak tracking includes floating P/L from open positions
 *   - Drawdown reflects unrealized profits/losses
 *   - More responsive to market movements
 *   - Example: If you have +$500 floating profit, peak can be updated
 *
 * DRAWDOWN_BALANCE (Balance-based):
 *   - Peak tracking based only on closed trades (account balance)
 *   - Drawdown ignores open positions
 *   - More conservative measurement
 *   - Example: Peak only updates when trades are closed with profit
 */
enum ENUM_DRAWDOWN_MODE
{
   DRAWDOWN_EQUITY = 0,      // Equity-based (includes floating P/L)
   DRAWDOWN_BALANCE = 1      // Balance-based (closed trades only)
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS                                                  |
//+------------------------------------------------------------------+

//═══════════════════════════════════════════════════════════════════
//  GENERAL SETTINGS
//═══════════════════════════════════════════════════════════════════
sinput string Sep1 = "════════ GENERAL ════════";
input int InpMagicNumber = 0;                      // Magic Number (0 = All Trades)
input string InpTradeComment = "EquityMonitor";    // EA Comment
input ENUM_DRAWDOWN_MODE InpDrawdownMode = DRAWDOWN_EQUITY;  // Drawdown Calculation Mode

//═══════════════════════════════════════════════════════════════════
//  DISPLAY SETTINGS
//═══════════════════════════════════════════════════════════════════
sinput string Sep2 = "════════ DISPLAY ════════";
input bool InpShowDashboard = true;                // Show Dashboard
input ENUM_CORNER_POSITION InpCornerPosition = CORNER_TOP_LEFT;  // Dashboard Position
input int InpXOffset = 10;                         // X Offset (Pixels)
input int InpYOffset = 20;                         // Y Offset (Pixels)
input int InpFontSize = 9;                         // Font Size
input color InpColorBackground = C'25,25,25';      // Background Color
input color InpColorText = clrWhite;               // Text Color
input color InpColorProfit = clrLimeGreen;         // Profit Color
input color InpColorLoss = clrRed;                 // Loss Color

//═══════════════════════════════════════════════════════════════════
//  FILE MANAGEMENT
//═══════════════════════════════════════════════════════════════════
sinput string Sep3 = "════════ FILE MANAGEMENT ════════";
input bool InpEnableAutoSave = true;               // Enable Auto-Save
input int InpAutoSaveInterval = 60;                // Auto-Save Interval (Minutes)
input string InpFileName = "EquityMonitor_Stats.csv";  // Stats Filename

//═══════════════════════════════════════════════════════════════════
//  KILLSWITCH PROTECTION
//═══════════════════════════════════════════════════════════════════
sinput string Sep4 = "════════ KILLSWITCH ════════";
input double InpMaxDrawdownThreshold = 0.0;        // Max Drawdown Threshold % (0 = Disabled)
input bool InpAggressiveCloseMode = false;         // Aggressive Mode (Continuously Close Positions)
input bool InpKillswitchAlert = true;              // Show Alert When Triggered

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - Equity Tracking                               |
//+------------------------------------------------------------------+
double g_PeakEquity = 0.0;              // Highest equity ever reached
double g_MaxDrawdown = 0.0;             // Maximum drawdown in account currency
double g_MaxDrawdownPercent = 0.0;      // Maximum drawdown in percentage

double g_CurrentEquity = 0.0;           // Current account equity
double g_CurrentBalance = 0.0;          // Current account balance
double g_CurrentDrawdown = 0.0;         // Current drawdown in currency
double g_CurrentDrawdownPercent = 0.0;  // Current drawdown in percentage
double g_FloatingPL = 0.0;              // Current floating profit/loss

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - Trading Statistics                            |
//+------------------------------------------------------------------+
int g_TotalTrades = 0;                  // Total closed trades
int g_WinningTrades = 0;                // Number of winning trades
int g_LosingTrades = 0;                 // Number of losing trades
double g_TotalProfit = 0.0;             // Total profit from all trades
double g_TotalLoss = 0.0;               // Total loss from all trades
double g_NetProfit = 0.0;               // Net profit/loss (Total Profit - Total Loss)
double g_WinRate = 0.0;                 // Win rate in percentage

double g_DailyPL = 0.0;                 // Profit/Loss for current day
datetime g_LastTradeTime = 0;           // Timestamp of last processed trade
datetime g_CurrentDay = 0;              // Current day being tracked for daily PNL

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - File Management                               |
//+------------------------------------------------------------------+
datetime g_LastSaveTime = 0;            // Timestamp of last save operation
bool g_StatsLoaded = false;             // Flag: Stats loaded from file

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - Dashboard                                     |
//+------------------------------------------------------------------+
bool g_DashboardCreated = false;        // Flag: Dashboard objects created
datetime g_LastUpdateTime = 0;          // Timestamp of last dashboard update

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - Killswitch                                    |
//+------------------------------------------------------------------+
bool g_KillswitchTriggered = false;     // Flag: Killswitch has been activated
datetime g_KillswitchTriggerTime = 0;   // Timestamp when killswitch was triggered
bool g_AlertShown = false;              // Flag: Alert already shown to user

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES - Logging Control                               |
//+------------------------------------------------------------------+
datetime g_LastLogTime = 0;             // Timestamp of last regular log output

//+------------------------------------------------------------------+
//| Expert initialization function                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("═══════════════════════════════════════════════════════════");
   Print("=== ", InpTradeComment, " V", VERSION, " Initialized ===");
   Print("═══════════════════════════════════════════════════════════");

   // Initialize current account values
   g_CurrentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   g_CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);

   // Try to load previous statistics from file
   if(InpEnableAutoSave)
   {
      LoadStatsFromFile();
   }

   // If no stats loaded, initialize with current value as peak (based on mode)
   if(!g_StatsLoaded)
   {
      if(InpDrawdownMode == DRAWDOWN_EQUITY)
      {
         g_PeakEquity = g_CurrentEquity;
         Print("Starting fresh monitoring (Equity mode). Initial Peak: ", g_PeakEquity);
      }
      else
      {
         g_PeakEquity = g_CurrentBalance;
         Print("Starting fresh monitoring (Balance mode). Initial Peak: ", g_PeakEquity);
      }
   }

   // Calculate initial statistics from history
   CalculateHistoricalStats();

   // Create dashboard if enabled
   if(InpShowDashboard)
   {
      CreateDashboard();
      g_DashboardCreated = true;
   }

   // Set initial save time
   g_LastSaveTime = TimeCurrent();
   g_LastUpdateTime = TimeCurrent();

   Print("Monitoring started. Peak Equity: ", g_PeakEquity);

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("═══════════════════════════════════════════════════════════");
   Print("=== ", InpTradeComment, " Deinitialized ===");
   Print("Reason: ", GetDeinitReasonText(reason));

   // Save final statistics before shutdown
   if(InpEnableAutoSave)
   {
      SaveStatsToFile();
      Print("Final statistics saved to file.");
   }

   // Remove all dashboard objects
   DeleteDashboard();

   Print("═══════════════════════════════════════════════════════════");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Update account values
   UpdateAccountValues();

   // Update equity tracking and drawdown calculations
   UpdateEquityTracking();

   // Monitor killswitch and close positions if threshold exceeded
   MonitorKillswitch();

   // Check for new closed trades and update statistics
   UpdateTradingStatistics();

   // Update dashboard display (throttled to avoid excessive updates)
   if(InpShowDashboard && TimeCurrent() - g_LastUpdateTime >= 1)
   {
      UpdateDashboard();
      g_LastUpdateTime = TimeCurrent();
   }

   // Auto-save statistics if interval elapsed
   if(InpEnableAutoSave && ShouldAutoSave())
   {
      SaveStatsToFile();
      g_LastSaveTime = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| SECTION: ACCOUNT VALUE UPDATES                                   |
//+------------------------------------------------------------------+

/**
 * Updates current account balance, equity, and floating P/L
 * Called on every tick to ensure real-time accuracy
 */
void UpdateAccountValues()
{
   g_CurrentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   g_CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_FloatingPL = g_CurrentEquity - g_CurrentBalance;
}

//+------------------------------------------------------------------+
//| SECTION: EQUITY TRACKING & DRAWDOWN CALCULATION                 |
//+------------------------------------------------------------------+

/**
 * Updates peak equity and calculates current/maximum drawdown
 * Supports both equity-based and balance-based tracking
 */
void UpdateEquityTracking()
{
   // Determine which value to use for peak tracking based on mode
   double currentValue = 0.0;

   if(InpDrawdownMode == DRAWDOWN_EQUITY)
   {
      // Equity mode: includes floating P/L
      currentValue = g_CurrentEquity;
   }
   else
   {
      // Balance mode: closed trades only (no floating P/L)
      currentValue = g_CurrentBalance;
   }

   // Update peak if current value is higher
   if(currentValue > g_PeakEquity)
   {
      g_PeakEquity = currentValue;

      // Only log at save intervals to reduce spam
      if(ShouldAutoSave() || g_LastLogTime == 0)
      {
         string mode = (InpDrawdownMode == DRAWDOWN_EQUITY) ? "Equity" : "Balance";
         Print("New Peak ", mode, " reached: ", g_PeakEquity);
      }
   }

   // Calculate current drawdown from peak
   g_CurrentDrawdown = g_PeakEquity - currentValue;

   // Calculate drawdown percentage
   if(g_PeakEquity > 0)
   {
      g_CurrentDrawdownPercent = (g_CurrentDrawdown / g_PeakEquity) * 100.0;
   }
   else
   {
      g_CurrentDrawdownPercent = 0.0;
   }

   // Update maximum drawdown if current is larger
   if(g_CurrentDrawdown > g_MaxDrawdown)
   {
      g_MaxDrawdown = g_CurrentDrawdown;
      g_MaxDrawdownPercent = g_CurrentDrawdownPercent;

      // Only log at save intervals to reduce spam
      if(ShouldAutoSave() || g_LastLogTime == 0)
      {
         Print("New Maximum Drawdown: ", g_MaxDrawdown, " (", g_MaxDrawdownPercent, "%)");
      }
   }
}

//+------------------------------------------------------------------+
//| SECTION: TRADING STATISTICS                                      |
//+------------------------------------------------------------------+

/**
 * Calculates historical statistics from closed trades
 * Called during initialization to load existing trade history
 */
void CalculateHistoricalStats()
{
   // Reset counters
   g_TotalTrades = 0;
   g_WinningTrades = 0;
   g_LosingTrades = 0;
   g_TotalProfit = 0.0;
   g_TotalLoss = 0.0;
   g_DailyPL = 0.0;

   datetime todayStart = StringToTime(TimeToString(TimeCurrent(), TIME_DATE));
   g_CurrentDay = todayStart;  // Initialize current day tracker

   // Loop through all deals in history
   HistorySelect(0, TimeCurrent());
   int totalDeals = HistoryDealsTotal();

   for(int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0)
      {
         // Filter by magic number if specified (0 = all trades)
         if(InpMagicNumber != 0 && HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
            continue;

         // Only process entry/exit deals (not balance operations)
         ENUM_DEAL_ENTRY dealEntry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
         if(dealEntry == DEAL_ENTRY_OUT)  // Exit deal = closed trade
         {
            // Calculate true profit including swap and commission
            double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
            double swap = HistoryDealGetDouble(ticket, DEAL_SWAP);
            double commission = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
            double netProfit = profit + swap + commission;

            datetime dealTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);

            g_TotalTrades++;

            if(netProfit > 0)
            {
               g_WinningTrades++;
               g_TotalProfit += netProfit;
            }
            else if(netProfit < 0)
            {
               g_LosingTrades++;
               g_TotalLoss += MathAbs(netProfit);
            }

            // Add to daily P/L if trade closed today
            if(dealTime >= todayStart)
            {
               g_DailyPL += netProfit;
            }

            // Update last trade time
            if(dealTime > g_LastTradeTime)
            {
               g_LastTradeTime = dealTime;
            }
         }
      }
   }

   // Calculate derived statistics
   g_NetProfit = g_TotalProfit - g_TotalLoss;
   g_WinRate = (g_TotalTrades > 0) ? (g_WinningTrades / (double)g_TotalTrades * 100.0) : 0.0;

   Print("Historical Stats Loaded: ", g_TotalTrades, " trades, Win Rate: ", DoubleToString(g_WinRate, 2), "%");
}

/**
 * Updates trading statistics with new closed trades
 * Called on every tick to detect newly closed positions
 */
void UpdateTradingStatistics()
{
   datetime todayStart = StringToTime(TimeToString(TimeCurrent(), TIME_DATE));

   // Check if a new day has started
   if(todayStart != g_CurrentDay)
   {
      Print("New day detected. Resetting daily P/L. Previous: ", g_DailyPL);
      g_DailyPL = 0.0;
      g_CurrentDay = todayStart;
   }

   // Select history and check for new deals
   HistorySelect(g_LastTradeTime, TimeCurrent());
   int totalDeals = HistoryDealsTotal();

   bool newTradeFound = false;

   for(int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0)
      {
         datetime dealTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);

         // Only process deals newer than last processed trade
         if(dealTime <= g_LastTradeTime)
            continue;

         // Filter by magic number if specified
         if(InpMagicNumber != 0 && HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
            continue;

         // Only process exit deals
         ENUM_DEAL_ENTRY dealEntry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
         if(dealEntry == DEAL_ENTRY_OUT)
         {
            // Calculate true profit including swap and commission
            double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
            double swap = HistoryDealGetDouble(ticket, DEAL_SWAP);
            double commission = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
            double netProfit = profit + swap + commission;

            g_TotalTrades++;
            newTradeFound = true;

            if(netProfit > 0)
            {
               g_WinningTrades++;
               g_TotalProfit += netProfit;
            }
            else if(netProfit < 0)
            {
               g_LosingTrades++;
               g_TotalLoss += MathAbs(netProfit);
            }

            // Add to daily P/L if trade closed today
            if(dealTime >= todayStart)
            {
               g_DailyPL += netProfit;
            }

            // Update last trade time
            if(dealTime > g_LastTradeTime)
            {
               g_LastTradeTime = dealTime;
            }
         }
      }
   }

   // Recalculate derived statistics if new trade found
   if(newTradeFound)
   {
      g_NetProfit = g_TotalProfit - g_TotalLoss;
      g_WinRate = (g_TotalTrades > 0) ? (g_WinningTrades / (double)g_TotalTrades * 100.0) : 0.0;

      // Only log at save intervals to reduce spam
      if(ShouldAutoSave() || g_LastLogTime == 0)
      {
         Print("New trade detected. Total: ", g_TotalTrades, ", Win Rate: ", DoubleToString(g_WinRate, 2), "%");
      }
   }
}

//+------------------------------------------------------------------+
//| SECTION: KILLSWITCH PROTECTION                                   |
//+------------------------------------------------------------------+

/**
 * Monitors drawdown and triggers killswitch if threshold is exceeded
 * Supports two modes: Standard (close once) and Aggressive (continuous close)
 */
void MonitorKillswitch()
{
   // Skip if killswitch is disabled (threshold = 0)
   if(InpMaxDrawdownThreshold <= 0.0)
      return;

   // Check if drawdown threshold is exceeded
   if(g_CurrentDrawdownPercent >= InpMaxDrawdownThreshold)
   {
      // Trigger killswitch if not already triggered
      if(!g_KillswitchTriggered)
      {
         g_KillswitchTriggered = true;
         g_KillswitchTriggerTime = TimeCurrent();

         Print("═══════════════════════════════════════════════════════════");
         Print("!!! KILLSWITCH TRIGGERED !!!");
         Print("Max Drawdown Threshold Exceeded: ", DoubleToString(g_CurrentDrawdownPercent, 2), "% >= ",
               DoubleToString(InpMaxDrawdownThreshold, 2), "%");
         Print("═══════════════════════════════════════════════════════════");

         // Show alert to user (once)
         if(InpKillswitchAlert && !g_AlertShown)
         {
            string alertMsg = "KILLSWITCH TRIGGERED!\n\n" +
                            "Drawdown: " + DoubleToString(g_CurrentDrawdownPercent, 2) + "%\n" +
                            "Threshold: " + DoubleToString(InpMaxDrawdownThreshold, 2) + "%\n\n" +
                            "Closing all positions...";
            Alert(alertMsg);
            g_AlertShown = true;
         }

         // Close all positions (Standard Mode)
         CloseAllPositions();
      }

      // Aggressive Mode: Keep closing any positions that appear
      if(InpAggressiveCloseMode && g_KillswitchTriggered)
      {
         CloseAllPositions();
      }
   }
}

/**
 * Closes all open positions on the account
 * Works with any magic number (closes positions from all EAs)
 * @return Number of positions closed
 */
int CloseAllPositions()
{
   int totalPositions = PositionsTotal();
   int closedCount = 0;
   int failedCount = 0;

   if(totalPositions == 0)
      return 0;

   Print("Attempting to close ", totalPositions, " position(s)...");

   // Iterate backwards to avoid index shifting issues
   for(int i = totalPositions - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;

      // CRITICAL: Select position by ticket to ensure data is current
      if(!PositionSelectByTicket(ticket))
      {
         Print("WARNING: Position #", ticket, " no longer exists (may already be closed)");
         continue;
      }

      string symbol = PositionGetString(POSITION_SYMBOL);
      ulong magic = PositionGetInteger(POSITION_MAGIC);
      double volume = PositionGetDouble(POSITION_VOLUME);
      ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);

      // Check if trading is allowed on this symbol
      if(!SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE))
      {
         Print("WARNING: Trading disabled on ", symbol, " - cannot close position #", ticket);
         failedCount++;
         continue;
      }

      // Prepare close request
      MqlTradeRequest request;
      MqlTradeResult result;
      ZeroMemory(request);
      ZeroMemory(result);

      request.action = TRADE_ACTION_DEAL;
      request.position = ticket;
      request.symbol = symbol;
      request.volume = volume;
      request.deviation = 50;  // Increased deviation for volatile markets
      request.magic = magic;
      request.comment = "Killswitch Close";
      request.type_filling = ORDER_FILLING_FOK;  // Fill or Kill

      // Determine close direction and price
      if(posType == POSITION_TYPE_BUY)
      {
         request.type = ORDER_TYPE_SELL;
         request.price = SymbolInfoDouble(symbol, SYMBOL_BID);
      }
      else
      {
         request.type = ORDER_TYPE_BUY;
         request.price = SymbolInfoDouble(symbol, SYMBOL_ASK);
      }

      // Attempt to close position with retry logic
      bool closed = false;
      for(int attempt = 1; attempt <= 3; attempt++)
      {
         ResetLastError();

         if(OrderSend(request, result))
         {
            if(result.retcode == TRADE_RETCODE_DONE || result.retcode == TRADE_RETCODE_PLACED)
            {
               closedCount++;
               Print("Killswitch closed position #", ticket, " (", symbol, ", ", volume, " lot)");
               closed = true;
               break;
            }
         }

         // Handle specific error codes
         if(result.retcode == TRADE_RETCODE_REJECT)
         {
            Print("WARNING: Broker rejected close request for #", ticket, " (attempt ", attempt, "/3)");
         }
         else if(result.retcode == TRADE_RETCODE_INVALID_PRICE)
         {
            Print("WARNING: Invalid price for #", ticket, " - refreshing (attempt ", attempt, "/3)");
            // Refresh price
            request.price = (posType == POSITION_TYPE_BUY) ?
                           SymbolInfoDouble(symbol, SYMBOL_BID) :
                           SymbolInfoDouble(symbol, SYMBOL_ASK);
         }
         else if(result.retcode == TRADE_RETCODE_MARKET_CLOSED)
         {
            Print("ERROR: Market closed for ", symbol, " - cannot close position #", ticket);
            failedCount++;
            break;
         }
         else
         {
            Print("WARNING: Close failed for #", ticket, " - Retcode: ", result.retcode,
                  ", Error: ", GetLastError(), " (attempt ", attempt, "/3)");
         }

         // Wait before retry
         if(attempt < 3)
            Sleep(100);
      }

      if(!closed)
      {
         failedCount++;
         Print("ERROR: Failed to close position #", ticket, " after 3 attempts - Final retcode: ", result.retcode);
      }
   }

   // Summary
   Print("Killswitch Summary: ", closedCount, " closed, ", failedCount, " failed");

   return closedCount;
}

//+------------------------------------------------------------------+
//| SECTION: FILE MANAGEMENT                                         |
//+------------------------------------------------------------------+

/**
 * Checks if auto-save interval has elapsed
 * @return true if save should occur, false otherwise
 */
bool ShouldAutoSave()
{
   int intervalSeconds = InpAutoSaveInterval * 60;
   return (TimeCurrent() - g_LastSaveTime >= intervalSeconds);
}

/**
 * Saves current statistics to CSV file
 * File format: timestamp, peak_equity, max_dd, max_dd_pct, total_trades, win_rate, net_profit
 */
void SaveStatsToFile()
{
   int fileHandle = FileOpen(InpFileName, FILE_WRITE|FILE_CSV|FILE_ANSI);

   if(fileHandle == INVALID_HANDLE)
   {
      Print("ERROR: Failed to open file for writing: ", InpFileName);
      return;
   }

   // Write header
   FileWrite(fileHandle, "Timestamp", "PeakEquity", "MaxDrawdown", "MaxDrawdown%",
             "TotalTrades", "WinningTrades", "LosingTrades", "WinRate%",
             "TotalProfit", "TotalLoss", "NetProfit", "LastTradeTime");

   // Write current statistics
   FileWrite(fileHandle,
             TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES),
             DoubleToString(g_PeakEquity, 2),
             DoubleToString(g_MaxDrawdown, 2),
             DoubleToString(g_MaxDrawdownPercent, 2),
             IntegerToString(g_TotalTrades),
             IntegerToString(g_WinningTrades),
             IntegerToString(g_LosingTrades),
             DoubleToString(g_WinRate, 2),
             DoubleToString(g_TotalProfit, 2),
             DoubleToString(g_TotalLoss, 2),
             DoubleToString(g_NetProfit, 2),
             TimeToString(g_LastTradeTime, TIME_DATE|TIME_MINUTES)
            );

   FileClose(fileHandle);
   Print("Statistics saved to: ", InpFileName);

   // Update log timestamp to sync with save intervals
   g_LastLogTime = TimeCurrent();
}

/**
 * Loads previous statistics from CSV file
 * Restores peak equity and max drawdown for continuous monitoring
 */
void LoadStatsFromFile()
{
   if(!FileIsExist(InpFileName))
   {
      Print("No previous stats file found. Starting fresh.");
      return;
   }

   int fileHandle = FileOpen(InpFileName, FILE_READ|FILE_CSV|FILE_ANSI);

   if(fileHandle == INVALID_HANDLE)
   {
      Print("ERROR: Failed to open file for reading: ", InpFileName);
      return;
   }

   // Skip header line
   string temp = FileReadString(fileHandle);

   // Read last line (most recent stats)
   // Note: In CSV mode, FileReadString reads until delimiter
   if(!FileIsEnding(fileHandle))
   {
      string timestamp = FileReadString(fileHandle);
      g_PeakEquity = StringToDouble(FileReadString(fileHandle));
      g_MaxDrawdown = StringToDouble(FileReadString(fileHandle));
      g_MaxDrawdownPercent = StringToDouble(FileReadString(fileHandle));
      g_TotalTrades = (int)StringToInteger(FileReadString(fileHandle));
      g_WinningTrades = (int)StringToInteger(FileReadString(fileHandle));
      g_LosingTrades = (int)StringToInteger(FileReadString(fileHandle));
      g_WinRate = StringToDouble(FileReadString(fileHandle));
      g_TotalProfit = StringToDouble(FileReadString(fileHandle));
      g_TotalLoss = StringToDouble(FileReadString(fileHandle));
      g_NetProfit = StringToDouble(FileReadString(fileHandle));
      string lastTradeTimeStr = FileReadString(fileHandle);
      g_LastTradeTime = StringToTime(lastTradeTimeStr);

      g_StatsLoaded = true;
      Print("Previous stats loaded from file:");
      Print("  Peak Equity: ", g_PeakEquity);
      Print("  Max Drawdown: ", g_MaxDrawdown, " (", g_MaxDrawdownPercent, "%)");
      Print("  Total Trades: ", g_TotalTrades);
   }

   FileClose(fileHandle);
}

//+------------------------------------------------------------------+
//| SECTION: DASHBOARD VISUALIZATION                                 |
//+------------------------------------------------------------------+

/**
 * Creates all dashboard objects on the chart
 */
void CreateDashboard()
{
   // Background panel
   CreateLabel(DASHBOARD_PREFIX + "BG", "", InpXOffset, InpYOffset, InpCornerPosition,
               InpFontSize + 2, InpColorBackground, "Consolas");

   // Title
   CreateLabel(DASHBOARD_PREFIX + "Title", "═══ EQUITY MONITOR V" + VERSION + " ═══",
               InpXOffset + 5, InpYOffset + 5, InpCornerPosition, InpFontSize + 1, clrGold, "Arial Black");

   int yPos = InpYOffset + 25;
   int lineHeight = InpFontSize + 8;

   // Section: Current Status
   CreateLabel(DASHBOARD_PREFIX + "SecCurrent", "─── Current Status ───",
               InpXOffset + 5, yPos, InpCornerPosition, InpFontSize, clrSilver, "Arial");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "Balance", "Balance:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "BalanceVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "Equity", "Equity:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "EquityVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "Floating", "Floating P/L:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "FloatingVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight + 5;

   // Section: Drawdown
   string ddMode = (InpDrawdownMode == DRAWDOWN_EQUITY) ? "Equity" : "Balance";
   CreateLabel(DASHBOARD_PREFIX + "SecDD", "─── Drawdown Analysis (" + ddMode + " Mode) ───",
               InpXOffset + 5, yPos, InpCornerPosition, InpFontSize, clrSilver, "Arial");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "Peak", "Peak " + ddMode + ":",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "PeakVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, clrLimeGreen, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "CurrDD", "Current DD:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "CurrDDVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "MaxDD", "Max DD:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "MaxDDVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, clrRed, "Consolas");
   yPos += lineHeight + 5;

   // Section: Trading Stats
   CreateLabel(DASHBOARD_PREFIX + "SecStats", "─── Trading Statistics ───",
               InpXOffset + 5, yPos, InpCornerPosition, InpFontSize, clrSilver, "Arial");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "TotalTrades", "Total Trades:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "TotalTradesVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "WinRate", "Win Rate:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "WinRateVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "NetProfit", "Net Profit:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "NetProfitVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight;

   CreateLabel(DASHBOARD_PREFIX + "DailyPL", "Daily P/L:",
               InpXOffset + 10, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   CreateLabel(DASHBOARD_PREFIX + "DailyPLVal", "",
               InpXOffset + 150, yPos, InpCornerPosition, InpFontSize, InpColorText, "Consolas");
   yPos += lineHeight + 5;

   // Footer
   CreateLabel(DASHBOARD_PREFIX + "Footer", "Auto-save: " + (InpEnableAutoSave ? "ON" : "OFF"),
               InpXOffset + 5, yPos, InpCornerPosition, InpFontSize - 1, clrDimGray, "Arial");

   Print("Dashboard created successfully.");
}

/**
 * Updates all dashboard values with current statistics
 */
void UpdateDashboard()
{
   if(!g_DashboardCreated) return;

   string currency = AccountInfoString(ACCOUNT_CURRENCY);

   // Current Status
   UpdateLabelText(DASHBOARD_PREFIX + "BalanceVal", DoubleToString(g_CurrentBalance, 2) + " " + currency);
   UpdateLabelText(DASHBOARD_PREFIX + "EquityVal", DoubleToString(g_CurrentEquity, 2) + " " + currency);

   // Floating P/L with color
   color floatingColor = (g_FloatingPL >= 0) ? InpColorProfit : InpColorLoss;
   UpdateLabelText(DASHBOARD_PREFIX + "FloatingVal", DoubleToString(g_FloatingPL, 2) + " " + currency);
   UpdateLabelColor(DASHBOARD_PREFIX + "FloatingVal", floatingColor);

   // Drawdown
   UpdateLabelText(DASHBOARD_PREFIX + "PeakVal", DoubleToString(g_PeakEquity, 2) + " " + currency);
   UpdateLabelText(DASHBOARD_PREFIX + "CurrDDVal",
                   DoubleToString(g_CurrentDrawdown, 2) + " (" + DoubleToString(g_CurrentDrawdownPercent, 2) + "%)");
   UpdateLabelText(DASHBOARD_PREFIX + "MaxDDVal",
                   DoubleToString(g_MaxDrawdown, 2) + " (" + DoubleToString(g_MaxDrawdownPercent, 2) + "%)");

   // Trading Stats
   UpdateLabelText(DASHBOARD_PREFIX + "TotalTradesVal",
                   IntegerToString(g_TotalTrades) + " (W:" + IntegerToString(g_WinningTrades) +
                   " L:" + IntegerToString(g_LosingTrades) + ")");
   UpdateLabelText(DASHBOARD_PREFIX + "WinRateVal", DoubleToString(g_WinRate, 2) + "%");

   // Net Profit with color
   color profitColor = (g_NetProfit >= 0) ? InpColorProfit : InpColorLoss;
   UpdateLabelText(DASHBOARD_PREFIX + "NetProfitVal", DoubleToString(g_NetProfit, 2) + " " + currency);
   UpdateLabelColor(DASHBOARD_PREFIX + "NetProfitVal", profitColor);

   // Daily P/L with color
   color dailyColor = (g_DailyPL >= 0) ? InpColorProfit : InpColorLoss;
   UpdateLabelText(DASHBOARD_PREFIX + "DailyPLVal", DoubleToString(g_DailyPL, 2) + " " + currency);
   UpdateLabelColor(DASHBOARD_PREFIX + "DailyPLVal", dailyColor);

   ChartRedraw();
}

/**
 * Deletes all dashboard objects from chart
 */
void DeleteDashboard()
{
   // Delete all objects with dashboard prefix
   int total = ObjectsTotal(0, 0, -1);

   for(int i = total - 1; i >= 0; i--)
   {
      string objName = ObjectName(0, i, 0, -1);
      if(StringFind(objName, DASHBOARD_PREFIX) == 0)
      {
         ObjectDelete(0, objName);
      }
   }

   ChartRedraw();
   Print("Dashboard deleted.");
}

//+------------------------------------------------------------------+
//| HELPER FUNCTIONS: Object Creation & Manipulation                 |
//+------------------------------------------------------------------+

/**
 * Creates a text label object on the chart
 */
void CreateLabel(string name, string text, int x, int y, ENUM_CORNER_POSITION corner,
                 int fontSize, color clr, string font)
{
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER, corner);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
   ObjectSetString(0, name, OBJPROP_FONT, font);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
}

/**
 * Updates the text of an existing label
 */
void UpdateLabelText(string name, string text)
{
   ObjectSetString(0, name, OBJPROP_TEXT, text);
}

/**
 * Updates the color of an existing label
 */
void UpdateLabelColor(string name, color clr)
{
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
}

//+------------------------------------------------------------------+
//| HELPER FUNCTIONS: Utility                                        |
//+------------------------------------------------------------------+

/**
 * Returns human-readable deinitialization reason
 */
string GetDeinitReasonText(int reason)
{
   switch(reason)
   {
      case REASON_PROGRAM:     return "EA stopped by user";
      case REASON_REMOVE:      return "EA removed from chart";
      case REASON_RECOMPILE:   return "EA recompiled";
      case REASON_CHARTCHANGE: return "Chart symbol/period changed";
      case REASON_CHARTCLOSE:  return "Chart closed";
      case REASON_PARAMETERS:  return "Input parameters changed";
      case REASON_ACCOUNT:     return "Account changed";
      case REASON_TEMPLATE:    return "Template applied";
      case REASON_INITFAILED:  return "Initialization failed";
      case REASON_CLOSE:       return "Terminal closing";
      default:                 return "Unknown reason";
   }
}

//+------------------------------------------------------------------+
