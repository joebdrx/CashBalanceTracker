# Excel Formula Solution for Daily Cash Balance Tracking

This document provides Excel formulas to track your daily cash balance with 10% position sizing.

## Required Columns in Your Excel Sheet

You'll need these columns in your trading data:

| Column | Name | Description |
|--------|------|-------------|
| A | Date | Every calendar day from first trade to last exit |
| B | EntrySignal | 1 if there's a trade entry on this date, 0 otherwise |
| C | ExitSignal | 1 if there's a trade exit on this date, 0 otherwise |
| D | EntryPrice | Entry price for trades starting this date |
| E | ExitPrice | Exit price for trades ending this date |
| F | CashBalance | Running cash balance (calculated) |
| G | NewPositionCost | Cost of new positions entered today |
| H | ExitProceeds | Proceeds from positions exited today |
| I | ActivePositions | Number of active positions |

## Step-by-Step Excel Setup

### 1. Prepare Your Data

First, create a daily calendar from your first trade entry to your last trade exit:

```excel
A2: =DATE(2017,1,11)  // Your first trade date
A3: =A2+1             // Copy this down for all days
```

### 2. Mark Entry and Exit Signals

Use VLOOKUP or INDEX/MATCH to mark when trades happen:

```excel
B2: =IF(COUNTIFS(TradeData[EntryDate],A2)>0,1,0)
C2: =IF(COUNTIFS(TradeData[ExitDate],A2)>0,1,0)
```

### 3. Get Trade Prices

```excel
D2: =IF(B2=1,INDEX(TradeData[EntryPrice],MATCH(A2,TradeData[EntryDate],0)),"")
E2: =IF(C2=1,INDEX(TradeData[ExitPrice],MATCH(A2,TradeData[ExitDate],0)),"")
```

### 4. Calculate New Position Costs (10% allocation)

```excel
G2: =IF(B2=1,INT((F1*0.1)/D2)*D2,0)
```

This formula:
- Checks if there's an entry signal (B2=1)
- Takes 10% of previous day's cash balance (F1*0.1)
- Divides by entry price to get shares: (F1*0.1)/D2
- Uses INT() to round down to whole shares
- Multiplies back by entry price to get actual cost

### 5. Calculate Exit Proceeds

For this, you need to track how many shares you bought for each position. Create a helper table or use arrays.

**Simple approach (assumes one position per day):**
```excel
H2: =IF(C2=1,INT((F_EntryDay*0.1)/D_EntryDay)*E2,0)
```

**Advanced approach (multiple positions):**
Create a separate tracking table for active positions.

### 6. Calculate Daily Cash Balance

```excel
F1: 1000000  // Starting cash
F2: =F1-G2+H2
```

Copy this formula down for all days.

### 7. Track Active Positions

```excel
I2: =I1+B2-C2
```

## Complete Formula Example for Row 2

Assuming row 1 has headers and initial values:

```excel
A2: =A1+1                                           // Next day
B2: =IF(COUNTIFS(EntryDates,A2)>0,1,0)            // Entry signal
C2: =IF(COUNTIFS(ExitDates,A2)>0,1,0)             // Exit signal  
D2: =IF(B2=1,INDEX(EntryPrices,MATCH(A2,EntryDates,0)),"") // Entry price
E2: =IF(C2=1,INDEX(ExitPrices,MATCH(A2,ExitDates,0)),"")   // Exit price
F2: =F1-G2+H2                                      // Cash balance
G2: =IF(B2=1,INT((F1*0.1)/D2)*D2,0)               // New position cost
H2: =IF(C2=1,[POSITION_EXIT_CALCULATION],0)        // Exit proceeds
I2: =I1+B2-C2                                      // Active positions
```

## Advanced Position Tracking

For accurate exit proceeds tracking, you need a helper table that tracks each position:

### Position Tracking Table (separate sheet or area)

| Position_ID | Entry_Date | Entry_Price | Shares | Exit_Date | Status |
|-------------|------------|-------------|--------|-----------|--------- |
| 1 | 2017-01-11 | 98.96 | 1010 | 2017-03-14 | Open |

### Formulas for Position Tracking

**When a new position opens:**
```excel
=IF(B2=1,ROW()-1,NA())                     // Position ID
=IF(B2=1,A2,NA())                          // Entry Date  
=IF(B2=1,D2,NA())                          // Entry Price
=IF(B2=1,INT((F1*0.1)/D2),NA())           // Shares
=IF(B2=1,"","")                            // Exit Date (blank initially)
=IF(B2=1,"Open","")                        // Status
```

**Calculate exit proceeds:**
```excel
H2: =IF(C2=1,SUMPRODUCT((PositionTable[Status]="Open")*
             (PositionTable[Exit_Date]=A2)*
             (PositionTable[Shares]*E2)),0)
```

## Simplified One-Formula Approach

If you want a single formula for cash balance that handles everything:

```excel
F2: =F1 
    - IF(B2=1,INT((F1*0.1)/D2)*D2,0)              // Subtract new position cost
    + IF(C2=1,SUMIF(PreviousEntries,A2-DAYS_TO_EXIT,
                   INT((CashAtEntry*0.1)/EntryPrice)*E2),0)  // Add exit proceeds
```

Note: This requires additional helper columns to track positions over time.

## Tips for Implementation

1. **Start Simple**: Begin with the basic cash balance formula and add complexity gradually
2. **Use Named Ranges**: Name your data ranges (EntryDates, ExitDates, etc.) for clearer formulas  
3. **Validate Results**: Cross-check your Excel results with a few manual calculations
4. **Handle Edge Cases**: Add error checking for division by zero, missing data, etc.
5. **Use Array Formulas**: For Excel 365, consider using dynamic arrays for easier maintenance

## Example Setup for Your Data

Based on your sample data, here's how to set up the formulas:

```excel
// Assuming your trade data is in columns M:S
F2: =F1-G2+H2                              // Cash balance
G2: =IF(COUNTIFS($M:$M,A2)>0,              // If entry today
        INT((F1*0.1)/INDEX($N:$N,MATCH(A2,$M:$M,0)))*
        INDEX($N:$N,MATCH(A2,$M:$M,0)),0)   // 10% position cost
H2: [Complex formula for exit proceeds based on your data structure]
```

This Excel approach will give you the same daily cash tracking as the Python script, but requires more setup for handling multiple positions and tracking shares over time.
