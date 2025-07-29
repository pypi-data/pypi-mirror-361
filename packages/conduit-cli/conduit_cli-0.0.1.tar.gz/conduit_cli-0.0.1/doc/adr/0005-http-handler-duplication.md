# 5. HTTP Handler Duplication

Date: 2025-06-03

## Status

Accepted

## Context

During implementation of HTTP artifact support, we created two separate HTTP handler implementations:

1. **HttpSourceHandler** (`src/conduit/handlers/source/http.py`)
   - Uses synchronous `requests` library
   - Follows the existing source/destination handler pattern
   - Integrated with HandlerFactory and GenerateService
   - Works with the current synchronous generate command

2. **HttpFetchHandler** (`src/conduit/handlers/fetch/http.py`)
   - Uses asynchronous `aiohttp` library
   - Follows the new Command/Query Handler pattern (CQRS)
   - Supports concurrent downloads via `FetchHandlerFactory.fetch()`
   - Better architectural pattern with dependency injection

This duplication violates the DRY principle but serves different architectural needs.

## Decision

We will **keep both implementations temporarily** and migrate incrementally to the fetch handler pattern.

### Rationale

1. **Different abstraction levels**: Source handlers are utilities, fetch handlers are proper command handlers
2. **Working system**: The generate command works today with source handlers
3. **Risk management**: Refactoring GenerateService to async is a significant change
4. **Clear migration path**: New features use fetch handlers, old features migrate gradually

## Consequences

### Positive
- Existing functionality remains stable
- New features get async benefits immediately
- Clear architectural direction (toward CQRS pattern)
- Incremental migration reduces risk

### Negative
- Temporary code duplication
- Two HTTP client dependencies (requests + aiohttp)
- Potential for confusion about which to use

### Migration Plan

1. **Phase 1** (Current): Both handlers coexist
   - Generate uses HttpSourceHandler
   - Pack/Unpack use HttpFetchHandler

2. **Phase 2** (Post-MVP): Migrate GenerateService
   - Refactor to support async operations
   - Replace source handlers with fetch handlers
   
3. **Phase 3** (Cleanup): Remove source handlers
   - Delete HttpSourceHandler
   - Remove requests dependency
   - Update all documentation

## Technical Debt Tracking

This decision creates technical debt that must be addressed:
- **Debt**: Duplicate HTTP download implementations
- **Impact**: Medium (code duplication, maintenance burden)
- **Resolution**: Migrate to fetch handlers exclusively
- **Timeline**: Post-MVP refactoring sprint