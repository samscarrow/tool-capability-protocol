# Migration Guide: Commands Dict to List Format

**Version**: 1.0.0  
**Author**: Dr. Alex Rivera  
**Date**: July 4, 2025  
**Deprecation Timeline**: Dict format will be removed in TCP v2.0.0  

## Overview

The TCP `CapabilityDescriptor.commands` field is transitioning from accepting Dict format to List format only. This guide helps you migrate your code.

## Why This Change?

1. **Consistency**: The type annotation has always been `List[CommandDescriptor]`
2. **Performance**: List operations are more predictable
3. **Clarity**: Order of commands is explicit
4. **Standards**: Aligns with industry best practices

## Current Behavior (v1.x)

Both formats are supported, but Dict format triggers a deprecation warning:

```python
# List format (recommended) ✅
descriptor = CapabilityDescriptor(
    name="mytool",
    version="1.0.0",
    commands=[
        CommandDescriptor(name="search", description="Search files"),
        CommandDescriptor(name="count", description="Count matches")
    ]
)

# Dict format (deprecated) ⚠️
descriptor = CapabilityDescriptor(
    name="mytool",
    version="1.0.0",
    commands={
        "search": CommandDescriptor(name="search", description="Search files"),
        "count": CommandDescriptor(name="count", description="Count matches")
    }
)
# DeprecationWarning: Dict format for commands is deprecated and will be removed in v2.0.0
```

## Migration Steps

### 1. For Direct Usage

**Before (Dict):**
```python
commands = {
    "cmd1": CommandDescriptor(name="cmd1", ...),
    "cmd2": CommandDescriptor(name="cmd2", ...),
}
descriptor = CapabilityDescriptor(commands=commands)
```

**After (List):**
```python
commands = [
    CommandDescriptor(name="cmd1", ...),
    CommandDescriptor(name="cmd2", ...),
]
descriptor = CapabilityDescriptor(commands=commands)
```

### 2. For Dynamic Command Building

**Before (Dict):**
```python
commands = {}
for cmd_name, cmd_info in command_data.items():
    commands[cmd_name] = CommandDescriptor(
        name=cmd_name,
        description=cmd_info['description']
    )
```

**After (List):**
```python
commands = []
for cmd_name, cmd_info in command_data.items():
    commands.append(CommandDescriptor(
        name=cmd_name,
        description=cmd_info['description']
    ))
```

### 3. For Schema Generation

**Before (Dict):**
```python
schema = {
    "commands": {}
}
for cmd in capabilities.commands:
    schema["commands"][cmd.name] = {...}
```

**After (List):**
```python
schema = {
    "commands": []
}
for cmd in capabilities.commands:
    schema["commands"].append({
        "name": cmd.name,
        ...
    })
```

### 4. For Command Lookup

If you were relying on Dict for O(1) lookup, use the built-in method:

```python
# Instead of: command = descriptor.commands["search"]
command = descriptor.get_command("search")
```

## Testing Your Migration

Run this test to verify your migration:

```python
import warnings

# This should not produce warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    descriptor = CapabilityDescriptor(
        name="test",
        version="1.0.0",
        commands=[...]  # Your migrated commands
    )
    
    if len(w) > 0:
        print("⚠️ Migration incomplete - still using Dict format")
    else:
        print("✅ Migration successful - using List format")
```

## Suppressing Warnings (Temporary)

If you need time to migrate:

```python
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    # Your Dict-using code here
```

**Note**: This is temporary! Plan your migration before v2.0.0.

## Timeline

- **v1.x.x** (current): Both formats supported, Dict shows deprecation warning
- **v2.0.0** (future): Only List format supported, Dict will raise TypeError

## Need Help?

Contact the TCP Research Consortium:
- Quality Issues: Dr. Alex Rivera
- Performance Concerns: Dr. Yuki Tanaka
- Architecture Questions: Marcus Chen

## Benefits After Migration

1. **No warnings** in your logs
2. **Future-proof** code
3. **Slightly better performance** (no conversion overhead)
4. **Clearer code** with explicit command ordering

---

Remember: Good code evolves. This migration makes TCP better for everyone!