---
name: deslop-architecture-composition-over-inheritance
description: Deslop principle — Composition Over Inheritance: Has-a over is-a; black-box composition.
---

# Composition Over Inheritance

> "Favor object composition over class inheritance."
> — Gang of Four, *Design Patterns*

Build complex behavior by combining objects ("has-a") rather than extending classes ("is-a"). Inheritance is white-box — the subclass sees and depends on parent internals, so changes cascade unpredictably and combinations breed a class explosion (`FileLoggerWithEncryptionAndCompression`). Composition is black-box — components interact through interfaces, stay loosely coupled, and can be mixed and swapped at runtime.

```python
# ❌ Wrong - Class explosion via inheritance
class FileLogger: ...
class FileLoggerWithEncryption(FileLogger): ...
class FileLoggerWithCompression(FileLogger): ...
# Combinatorial explosion!

# ✅ Correct - Composition
class Logger:
    def __init__(self, writer: Writer, filters: list[Filter]):
        self.writer = writer
        self.filters = filters

logger = Logger(FileWriter(), [EncryptionFilter(), CompressionFilter()])
```
