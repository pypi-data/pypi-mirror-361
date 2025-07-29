# Code Review: PR #48 - Rework Client Timeouts to Work Closer to Connect

## Summary of Changes

This PR modifies the timeout behavior in connecpy's client implementations to better align with the Connect RPC specification and other Connect implementations. The key changes are:

1. **Timeout Unit Change**: Changed from seconds to milliseconds to match Connect's timeout specification
2. **Parameter Naming**: Renamed `timeout` to `timeout_ms` for clarity
3. **Default Behavior**: Changed from a default 5-second timeout to no read timeout (matching connect-go's behavior)
4. **Timeout Semantics**: For async clients, applies timeout to the entire operation using `asyncio.wait_for`
5. **Connection Timeout**: Added a 30-second connect timeout by default when no timeout is specified

## Code Quality Assessment

### Strengths

1. **Specification Compliance**: The changes align connecpy with the Connect protocol specification and other implementations (connect-go, connect-es), improving cross-language consistency.

2. **Clear Intent**: The parameter rename from `timeout` to `timeout_ms` makes the unit explicit, reducing potential confusion.

3. **Comprehensive Testing**: Added extensive test coverage for timeout scenarios, including:
   - Client-level timeouts
   - Per-call timeouts
   - Timeout header verification
   - Both sync and async client timeout tests

4. **Backward Compatibility Consideration**: The PR maintains the ability to set timeouts while changing the default behavior.

5. **Proper Error Handling**: Consistent error messages ("Request timed out") and appropriate error codes (DeadlineExceeded).

### Areas of Concern

1. **Breaking Change**: This is a breaking API change that will require users to update their code:
   - Parameter name change from `timeout` to `timeout_ms`
   - Unit change from seconds to milliseconds
   - Default behavior change (from 5s to no timeout)

2. **Sync vs Async Timeout Implementation Discrepancy**:
   - Async implementation uses `asyncio.wait_for` for true operation-level timeout
   - Sync implementation falls back to httpx's read timeout, which is "more forgiving" as noted in the docstring
   - This inconsistency could lead to different behaviors between sync and async clients

3. **Documentation**: The PR lacks updates to documentation explaining:
   - The rationale for no default timeout
   - Migration guide for existing users
   - The difference in timeout behavior between sync and async clients

4. **Test Server Cleanup**: The timeout test uses a sleeping server but doesn't properly shut it down:
   ```python
   finally:
       # Don't wait for sleeping server to shutdown cleanly for this
       # test, we don't care anyways.
       pass
   ```
   This could potentially leave resources hanging.

## Potential Issues

1. **Resource Leaks**: The incomplete server shutdown in tests could lead to resource leaks during test runs.

2. **User Surprise**: Users upgrading might be surprised by:
   - Their code breaking due to parameter rename
   - Requests that previously timed out after 5s now running indefinitely

3. **Platform Differences**: The comment about sync timeout being "difficult in synchronous Python code to do cross-platform" suggests potential platform-specific behaviors.

## Suggestions for Improvements

1. **Migration Documentation**: Add a migration guide or update the changelog to help users transition:
   ```python
   # Before
   client = ConnecpyClient(url, timeout=5)
   
   # After
   client = ConnecpyClient(url, timeout_ms=5000)
   ```

2. **Deprecation Path**: Consider a deprecation path:
   ```python
   def __init__(self, address: str, timeout_ms: Optional[int] = None, timeout: Optional[float] = None, ...):
       if timeout is not None:
           warnings.warn("'timeout' is deprecated, use 'timeout_ms' instead", DeprecationWarning)
           timeout_ms = int(timeout * 1000)
   ```

3. **Test Cleanup**: Properly clean up the test server:
   ```python
   finally:
       httpd.shutdown()
       thread.join(timeout=1)
   ```

4. **Sync Timeout Improvement**: Document the limitation more clearly or investigate using `signal.alarm()` on Unix systems for better timeout control.

5. **Constants**: Consider adding timeout-related constants:
   ```python
   DEFAULT_CONNECT_TIMEOUT_S = 30.0
   NO_TIMEOUT = None
   ```

## Overall Recommendation

**Approve with reservations** - This PR makes important improvements to align connecpy with the Connect specification, which is valuable for cross-language consistency. However, the breaking changes need careful consideration:

1. The PR should include migration documentation
2. Consider adding a deprecation period for the old parameter name
3. The sync vs async timeout implementation difference should be clearly documented
4. Test cleanup should be improved

The maintainers should weigh the benefits of specification compliance against the disruption to existing users. If this project is still in early stages (pre-1.0), the breaking change might be acceptable. Otherwise, a more gradual migration path would be advisable.

## Additional Notes

- The PR author (Anuraag Agrawal) has provided clear rationale for the changes
- All CI checks are passing
- The code quality is generally good with proper type hints and error handling
- The test coverage is comprehensive and well-structured