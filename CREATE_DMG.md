# Creating a DMG for Distribution

To create a professional DMG file for distribution:

## Option 1: Using Disk Utility (GUI)
1. Open Disk Utility
2. File → New Image → Image from Folder
3. Select the CashBalanceTracker.app
4. Choose compressed format
5. Save as CashBalanceTracker.dmg

## Option 2: Using Terminal
```bash
hdiutil create -volname "Cash Balance Tracker" -srcfolder CashBalanceTracker.app -ov -format UDZO CashBalanceTracker.dmg
```

## Option 3: Professional DMG with background
1. Create a folder with:
   - CashBalanceTracker.app
   - Applications folder shortcut
   - Background image
2. Use create-dmg tool or DMG Canvas

The resulting DMG file can be distributed to users who can:
1. Double-click to mount
2. Drag app to Applications
3. Eject and delete DMG
