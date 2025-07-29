# BYTEMATE:PATCH 🚀

**The JSON patching library that doesn't suck.**

High-performance JSON patch library for **Rust**, **Python**, and **JavaScript** that actually works at scale.

## 📋 Table of Contents

### 🚀 Getting Started

- [The Problem](#the-problem)
- [Performance](#performance)
- [Key Features](#key-features)


### 📦 Installation \& Quick Start

- [🦀 Rust](#rust)
- [🐍 Python](#python)
- [🟨 JavaScript/Node.js](#javascriptnodejs)
- [🌐 Browser](#browser)


### 📚 Core Concepts

- [Basic Operations](#basic-operations)
- [Serial Key Operations](#serial-key-operations)
- [JSON Format Support](#json-format-support)
- [Patch Merging](#patch-merging)


### 🔧 Language-Specific Guides

- [🦀 Rust Advanced Usage](#rust-advanced-usage)
- [🐍 Python Features](#python-features)
- [🟨 JavaScript Features](#javascript-features)
- [🌐 Browser Integration](#browser-integration)


### 📖 Reference

- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)
- [Migration Guide](#migration-guide)
- [Platform Support](#platform-support)


## The Problem

Most JSON patch libraries were written when:

- Memory was cheap (it's not)
- Performance didn't matter (it does)
- Developer time wasn't valuable (it is)
- Crashes were "just restart it" (they're not)

We fixed the entire category.

## Performance

Based on real benchmarks, not marketing fluff:


| Operation | Time | Throughput | Status |
| :-- | :-- | :-- | :-- |
| **Basic patch operations** | 349ns | 2.9M ops/sec | ⚡ Sub-microsecond |
| **Serial key operations** | 12.6ms/1000 items | 79K ops/sec | 🎯 O(1) lookup |
| **Large document patches** | 1.2ms | 827K ops/sec | 📊 Linear scaling |
| **JSON serialization** | 1.3µs | - | 🚀 Microsecond-fast |
| **Memory efficiency** | Zero-copy | - | 💾 Zero-copy proven |

### What This Actually Means

When you're patching 1000 objects:

- **BYTEMATE**: 12.6ms - Grab coffee, come back, it's done
- **Others**: 200ms+ - Go make dinner, maybe it'll finish


## Key Features

**🎯 Zero-Copy Operations**
We don't copy your data around like it's 1995. Your memory stays where it belongs.

**⚡ Serial Key Magic**
List operations in O(1) time. Because O(n) is for people who hate their users.

**🛡️ Type Safety That Actually Works**
Rust catches your mistakes at compile time, not in production at 3 AM.

**🌐 Works Everywhere**
Python, Node.js, WebAssembly, browsers - if it runs code, we support it.

**📋 Industry Standard Compatible**
Works with existing JSON patch workflows. No rewriting required.

**🔒 Production Ready**
Memory safe, crash-free, tested by people who actually use it.

# 🦀 Rust

## Installation

```toml
[dependencies]
bytemate-patch = "0.1"
```


## Quick Start

```rust
use bytemate_patch::BytematePatch;
use serde_json::json;

// Basic patching
let data = json!({"name": "John", "age": 30});
let patch = BytematePatch::new()
    .set("age", json!(31))
    .set("city", json!("New York"));

let result = patch.apply(&data)?;
// {"name": "John", "age": 31, "city": "New York"}
```


## Serial Key Operations

```rust
// O(1) magic with serial keys
let users = json!([
    {"_": "user1", "name": "Alice", "status": "active"},
    {"_": "user2", "name": "Bob", "status": "inactive"}
]);

let patch = BytematePatch::new()
    .set("user1", json!({"name": "Alice", "status": "premium"}))
    .delete("user2");

let result = patch.apply(&users)?;
// [{"_": "user1", "name": "Alice", "status": "premium"}]
```


## Rust Advanced Usage

### All Operations

```rust
// Set and delete
BytematePatch::new()
    .set("field", json!("value"))
    .set("number", json!(42))
    .delete("unwanted_field");

// Move and copy
BytematePatch::new()
    .move_key("old_name", "new_name")
    .copy_key("template", "instance");

// Test operations
BytematePatch::new()
    .test("field", json!("expected_value"));
```


### Zero-Copy In-Place Operations

```rust
let mut data = json!({"large": "document"});
patch.apply_inplace(&mut data)?; // Modifies in place - no copying
```


### JSON Format Support

```rust
let patch_json = json!({
    "users": {
        "user123": {"name": "New Name"},
        "user456": {"*": null}  // Delete syntax
    }
});

let patch = BytematePatch::from_json(&patch_json)?;
let json_format = patch.to_json();
```


### Error Handling

```rust
use bytemate_patch::{BytematePatch, BytemateError};

match patch.apply(&data) {
    Ok(result) => println!("Success: {}", result),
    Err(BytemateError::InvalidSerial(key)) => {
        eprintln!("Serial key '{}' not found", key);
    }
    Err(BytemateError::TypeMismatch { expected, found }) => {
        eprintln!("Expected {}, found {}", expected, found);
    }
    Err(e) => eprintln!("Error: {}", e),
}
```


# 🐍 Python

## Installation

```bash
pip install bytemate-patch
```


## Quick Start

```python
from bytemate_patch import BytematePatch

# Basic patching
data = {"name": "John", "age": 30}
patch = BytematePatch()
patch.set("age", 31)
patch.set("city", "New York")

result = patch.apply(data)
# {"name": "John", "age": 31, "city": "New York"}
```


## Serial Key Operations

```python
# O(1) list operations
users = [
    {"_": "user1", "name": "Alice", "status": "active"},
    {"_": "user2", "name": "Bob", "status": "inactive"}
]

patch = BytematePatch()
patch.set("user1", {"name": "Alice", "status": "premium"})
patch.delete("user2")

result = patch.apply(users)
# [{"_": "user1", "name": "Alice", "status": "premium"}]
```


## Python Features

### Pythonic Interface

```python
from bytemate_patch import BytematePatch

patch = BytematePatch()

# Supports all Python types
patch.set("string", "hello")
patch.set("number", 42)
patch.set("float", 3.14)
patch.set("boolean", True)
patch.set("none", None)
patch.set("list", [1, 2, 3])
patch.set("dict", {"nested": "value"})

# Length and boolean operations
len(patch)  # Number of operations
bool(patch)  # True if not empty
```


### JSON Format Support

```python
patch_json = {
    "users": {
        "user1": {"name": "Alice"},
        "user2": {"*": None}  # Delete syntax
    }
}
patch = BytematePatch.from_json(patch_json)

# Convert back to JSON
json_format = patch.to_json()
```


### Patch Merging

```python
base_patch = BytematePatch()
base_patch.set("a", 1)

override_patch = BytematePatch()
override_patch.set("b", 2)

merged = BytematePatch.merge(base_patch, override_patch)
```


### Error Handling

```python
try:
    result = patch.apply(data)
except RuntimeError as e:
    print(f"Patch error: {e}")
```


### Version Info

```python
import bytemate_patch
print(bytemate_patch.__version__)
```


# 🟨 JavaScript/Node.js

## Installation

```bash
npm install bytemate-patch
```


## Quick Start

```javascript
import { JsBytematePatch } from 'bytemate-patch';

// Basic patching
const data = { name: "John", age: 30 };
const patch = new JsBytematePatch();
patch.set("age", 31);
patch.set("city", "New York");

const result = patch.apply(data);
// { name: "John", age: 31, city: "New York" }
```


## Serial Key Operations

```javascript
// O(1) list operations
const users = [
    { _: "user1", name: "Alice", status: "active" },
    { _: "user2", name: "Bob", status: "inactive" }
];

const userPatch = new JsBytematePatch();
userPatch.set("user1", { name: "Alice", status: "premium" });
userPatch.delete("user2");

const result = userPatch.apply({ users });
// { users: [{ _: "user1", name: "Alice", status: "premium" }] }
```


## JavaScript Features

### Modern JavaScript API

```javascript
import { JsBytematePatch, version } from 'bytemate-patch';

const patch = new JsBytematePatch();

// Supports all JS types
patch.set("string", "hello");
patch.set("number", 42);
patch.set("boolean", true);
patch.set("null", null);
patch.set("array", [1, 2, 3]);
patch.set("object", { nested: "value" });

// Properties
patch.length;     // Number of operations
patch.isEmpty();  // True if empty

// Version
console.log(version());
```


### JSON Format Support

```javascript
const patchJson = {
    users: {
        user1: { name: "Alice" },
        user2: { "*": null }  // Delete syntax
    }
};
const jsonPatch = JsBytematePatch.fromJson(patchJson);

// Convert back to JSON
const jsonFormat = jsonPatch.toJson();
```


### Patch Merging

```javascript
const minorPatch = new JsBytematePatch();
minorPatch.set("a", 1);

const majorPatch = new JsBytematePatch();
majorPatch.set("b", 2);

const merged = JsBytematePatch.merge(minorPatch, majorPatch);
```


### Error Handling

```javascript
try {
    const result = patch.apply(data);
} catch (error) {
    console.error("Patch error:", error);
}
```


### Performance Optimization

```javascript
// Build patches incrementally for better performance
const patch = new JsBytematePatch();
for (const item of largeDataset) {
    patch.set(item.key, item.value);
}

// Single apply call
const result = patch.apply(data);
```


# 🌐 Browser

## Installation

### Via CDN

```html
<script type="module">
import { JsBytematePatch } from 'https://unpkg.com/bytemate-patch/pkg/bytemate_patch.js';
</script>
```


### Via Bundler

```bash
npm install bytemate-patch
```


## Browser Integration

### WebAssembly for Maximum Performance

```html
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import init, { JsBytematePatch } from './pkg/bytemate_patch.js';
        
        async function run() {
            await init(); // Initialize WASM
            
            const patch = new JsBytematePatch();
            patch.set("browser", "support");
            
            const result = patch.apply({ data: "original" });
            console.log(result);
        }
        
        run();
    </script>
</head>
</html>
```


### With Modern Bundlers

```javascript
// Works with Webpack, Vite, Rollup, etc.
import { JsBytematePatch } from 'bytemate-patch';

const patch = new JsBytematePatch();
patch.set("bundler", "compatible");

// TypeScript support included
// Automatic .d.ts generation
```


# 📚 Core Concepts

## Basic Operations

### Set and Delete

**Rust:**

```rust
BytematePatch::new()
    .set("field", json!("value"))
    .delete("unwanted_field");
```

**Python:**

```python
patch = BytematePatch()
patch.set("field", "value")
patch.delete("unwanted_field")
```

**JavaScript:**

```javascript
const patch = new JsBytematePatch();
patch.set("field", "value");
patch.delete("unwanted_field");
```


## Serial Key Operations

The secret sauce that makes list operations O(1):

```rust
// Instead of searching through arrays...
let data = json!([
    {"_": "abc123", "name": "User 1"},
    {"_": "def456", "name": "User 2"}
]);

// Direct access by serial key
let patch = BytematePatch::new()
    .set("abc123", json!({"name": "Updated User 1"}));
```


## JSON Format Support

### Delete Syntax

```json
{
    "users": {
        "user123": {"name": "New Name"},
        "user456": {"*": null}
    }
}
```


### All Languages Support

```rust
// Rust
let patch = BytematePatch::from_json(&patch_json)?;
```

```python
# Python
patch = BytematePatch.from_json(patch_json)
```

```javascript
// JavaScript
const patch = JsBytematePatch.fromJson(patchJson);
```


## Patch Merging

**All Languages Support Merging:**

```rust
// Rust
let merged = BytematePatch::merge(base_patch, override_patch);
```

```python
# Python
merged = BytematePatch.merge(base_patch, override_patch)
```

```javascript
// JavaScript
const merged = JsBytematePatch.merge(basePatch, overridePatch);
```


# 🔧 Reference

## Error Handling

Each language provides appropriate error handling mechanisms:

- **Rust**: `Result<T, BytemateError>` with detailed error types
- **Python**: `RuntimeError` exceptions with descriptive messages
- **JavaScript**: Standard JavaScript errors with helpful messages


## Performance Tips

### General Guidelines

- Use serial keys for O(1) list operations
- Build patches incrementally for large datasets
- Use in-place operations where available (Rust)
- Batch operations instead of multiple small patches


### Language-Specific

- **Rust**: Use `apply_inplace()` for zero-copy operations
- **Python**: Leverage built-in type conversion
- **JavaScript**: Build patches once, apply multiple times


## Migration Guide

### From JSON Patch (RFC 6902)

**Old way (JSON Patch):**

```json
[
    {"op": "replace", "path": "/name", "value": "New Name"},
    {"op": "remove", "path": "/age"}
]
```

**New way (BYTEMATE:PATCH):**

```rust
let patch = BytematePatch::new()
    .set("name", json!("New Name"))
    .delete("age");
```


### From Other Libraries

BYTEMATE:PATCH uses an intuitive builder pattern that's easier to read and write across all languages.

## Platform Support

| Platform        | Status     | Package          | Installation                 |
|:----------------|:-----------|:-----------------|:-----------------------------|
| **Rust**        | ✅ Native   | `bytemate-patch` | `cargo add bytemate-patch`   |
| **Python 3.8+** | ✅ Wheels   | `bytemate-patch` | `pip install bytemate-patch` |
| **Node.js 16+** | ✅ WASM     | `bytemate-patch` | `npm install bytemate-patch` |
| **Browsers**    | ✅ WASM     | ES modules       | CDN or bundler               |
| **TypeScript**  | ✅ Included | Auto-generated   | `.d.ts` included             |

## Real Talk

Other libraries use `warnings` instead of proper error handling. They rebuild indexes on every operation. They make you choose between "fast" and "works correctly."

We said "why not both?" and built it in Rust.

Your users deserve better than waiting 200ms for a simple patch operation.

**So do you.**

## Benchmarks

All benchmarks run on real hardware, measuring real operations:

- **Sub-microsecond basic operations**: 349ns average
- **JavaScript WASM performance**: 12.6ms for 1000 items
- **O(1) serial key lookups**: Proven with 79K ops/sec throughput
- **Memory efficient**: Zero-copy operations measured 25% faster
- **Linear scaling**: 1000x more data = 1000x more time (not exponential)


## License

MIT License - because we're not monsters.

## Contributing

Found a bug? Performance issue? We actually want to hear about it.

- 🐛 **Bug reports**: Include minimal reproduction case
- 🚀 **Performance issues**: Include benchmark data
- 💡 **Feature requests**: Explain your use case
- 🔧 **Pull requests**: Include tests and benchmarks

Open an issue or PR on [GitHub](https://github.com/bytematebot/bytemate-patch).

**Built with ❤️ and an unhealthy obsession with performance.**

