# Code Flow Comparison: With vs Without Starlette

## Request Body Reading Flow

### With Starlette (Before PR #45)
```python
1. Client sends request with body
2. ASGI server calls ConnecpyASGIApp.__call__()
3. ConnecpyASGIApp._handle_post_request():
   a. request = Request(scope, receive)  # Create Starlette Request object
   b. req_body = await request.body()    # Starlette reads entire body into memory
      └─> Starlette internally:
          - Checks if body already cached
          - If not, loops through receive() messages
          - Accumulates chunks in a list
          - Joins chunks into single bytes object
          - Caches result
   c. Check size limit AFTER body is fully loaded
   d. If too large, raise exception (but memory already consumed!)
```

### Without Starlette (After PR #45)
```python
1. Client sends request with body
2. ASGI server calls ConnecpyASGIApp.__call__()
3. ConnecpyASGIApp._handle_post_request():
   a. req_body = await self._read_body(receive)  # Direct implementation
      └─> ConnecPy internally:
          - Loops through receive() messages
          - Accumulates chunks with += operator
          - Returns complete body
   b. Check size limit AFTER body is fully loaded
   c. If too large, raise exception (but memory already consumed!)
```

## The CRITICAL Issue: Both Approaches Have The Same Vulnerability!

### The Problem
Both implementations read the ENTIRE body into memory BEFORE checking the size limit:

```python
# Both versions essentially do this:
body = read_entire_body_into_memory()  # ← VULNERABILITY HERE
if len(body) > limit:                   # ← Too late! Memory already used
    raise Exception("Too large")
```

### What SHOULD Be Done (in both cases)
```python
# Secure implementation (neither version does this):
total_size = 0
chunks = []
while reading:
    chunk = await receive_chunk()
    total_size += len(chunk)
    if total_size > limit:              # ← Check BEFORE accumulating
        raise Exception("Too large")
    chunks.append(chunk)
body = b"".join(chunks)
```

## Performance Comparison

### Memory Allocation Pattern

**Starlette approach:**
```python
chunks = []             # List allocation
chunks.append(chunk1)   # List grows
chunks.append(chunk2)   # List grows more
...
body = b"".join(chunks) # Final allocation + copy
```

**PR #45 approach:**
```python
body = b""              # Initial empty bytes
body += chunk1          # Reallocation + copy
body += chunk2          # Reallocation + copy
...
```

**Performance Impact**: NEGLIGIBLE for typical request sizes
- Starlette: More efficient for many small chunks (list growth is amortized)
- PR #45: Simpler, more direct approach
- Both: Vulnerable to large requests consuming memory

## Error Handling Comparison

### Starlette Errors
```python
# If client disconnects:
raise ClientDisconnect()  # Generic Starlette exception

# If stream already consumed:
raise RuntimeError("Stream consumed")
```

### PR #45 Errors
```python
# If client disconnects:
raise ConnecpyServerException(
    code=errors.Errors.Canceled,
    message="Client disconnected before request completion"
)

# If unexpected message type:
raise ConnecpyServerException(
    code=errors.Errors.Unknown,
    message="Unexpected message type"
)
```

**Advantage**: PR #45 provides Connect Protocol-specific error codes that clients can properly interpret.

## Conclusion

The removal of Starlette is a **non-event** from a security perspective. The code does exactly the same thing, with the same vulnerabilities, just without an unnecessary dependency.