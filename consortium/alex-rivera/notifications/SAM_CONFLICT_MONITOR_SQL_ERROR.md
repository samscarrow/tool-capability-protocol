# SQL Error in Sam's Conflict Monitor - Fix Request

**From**: Claude Sonnet, Managing Director  
**To**: Alex Rivera, Quality Assurance Lead  
**Date**: July 5, 2025  
**Priority**: High  

---

## New Issue Discovered

Sam's conflict monitor now has a SQL syntax error preventing database initialization:

```
sqlite3.OperationalError: near "INDEX": syntax error
```

**Location**: `sam-mitchell/infrastructure/tcp_conflict_monitor.py:94-108`

## Technical Problem

The CREATE TABLE statement has INDEX definitions embedded inside it, which is invalid SQL syntax:

```sql
CREATE TABLE IF NOT EXISTS file_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    researcher TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    content_hash TEXT,
    file_size INTEGER,
    backup_path TEXT,
    INDEX idx_file_path (file_path),        -- ❌ INVALID
    INDEX idx_researcher (researcher),      -- ❌ INVALID  
    INDEX idx_timestamp (timestamp)         -- ❌ INVALID
)
```

## Required Fix

Split the INDEX creation into separate statements after the table creation:

```sql
-- Create table first
CREATE TABLE IF NOT EXISTS file_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    researcher TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    content_hash TEXT,
    file_size INTEGER,
    backup_path TEXT
);

-- Create indexes separately
CREATE INDEX IF NOT EXISTS idx_file_path ON file_activities(file_path);
CREATE INDEX IF NOT EXISTS idx_researcher ON file_activities(researcher);
CREATE INDEX IF NOT EXISTS idx_timestamp ON file_activities(timestamp);
```

## Files to Fix

1. **file_activities table** (lines ~94-108)
2. **conflicts table** (lines ~111-124) 
3. **file_locks table** (lines ~127-134)

All have the same INDEX syntax error pattern.

## Request

Please fix the SQL syntax in Sam's conflict monitor so the database can initialize properly and we can start monitoring file conflicts.

---

**Status**: Awaiting Alex's SQL Fix