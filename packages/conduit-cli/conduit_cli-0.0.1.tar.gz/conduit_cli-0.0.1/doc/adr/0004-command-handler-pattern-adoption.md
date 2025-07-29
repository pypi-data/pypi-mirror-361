# 4. Command Handler Pattern Adoption

Date: 2025-01-29

## Status

**ACCEPTED**

## Context

During implementation of the pack command, we identified inconsistencies in how the codebase handles different types of "handlers." The current architecture mixes two distinct patterns:

1. **Utility Handlers**: `FileSourceHandler`, `FileDestinationHandler` - focused utilities for specific operations
2. **Command Processing**: Services directly orchestrating business logic

This mixed approach led to confusion about where pack command logic should reside and how to structure the handler abstraction properly.

## Decision

We will adopt the **Command/Query Handler pattern** (CQRS/MediatR style) for command processing in Conduit, while maintaining existing utility handlers for their specific purposes.

### Command Handler Pattern Structure

```python
# Command object - explicit request structure
@dataclass
class PackCommand:
    lockfile_path: str
    output_path: str
    registry_ref: Optional[str] = None

# Result object - explicit response structure  
@dataclass
class PackResult:
    bundle_path: str
    layers_created: int
    artifacts_bundled: int

# Command Handler - handles specific commands with dependency injection
class PackCommandHandler:
    def __init__(self, 
                 lockfile_service: LockfileService,
                 oci_bundler: OCIBundler):
        self.lockfile_service = lockfile_service
        self.oci_bundler = oci_bundler
    
    def handle(self, command: PackCommand) -> PackResult:
        # Command-specific business logic
        lockfile = self.lockfile_service.load_lockfile(command.lockfile_path)
        bundle_path = self.oci_bundler.create_bundle(lockfile, command.output_path)
        return PackResult(
            bundle_path=bundle_path,
            layers_created=2,
            artifacts_bundled=len(lockfile.artifacts)
        )
```

### Usage Pattern

```python
# Dependency injection (manual or via DI container)
lockfile_service = LockfileService()
oci_bundler = OCIBundler()
pack_handler = PackCommandHandler(lockfile_service, oci_bundler)

# Command execution
command = PackCommand(lockfile_path="app.lock.yaml", output_path="./bundle")
result = pack_handler.handle(command)
```

## Architecture Boundaries

### Command Handlers (New Pattern)
- **Purpose**: Handle specific commands/queries with explicit input/output
- **Location**: `src/conduit/handlers/` (new command handlers)
- **Examples**: `PackCommandHandler`, `UnpackCommandHandler`, `VerifyCommandHandler`
- **Characteristics**:
  - Single `handle(command) -> result` method
  - Dependency injection in constructor
  - Explicit command and result objects
  - Business logic orchestration

### Utility Handlers (Existing Pattern)
- **Purpose**: Focused utilities for specific operations by URI scheme
- **Location**: `src/conduit/handlers/source/`, `src/conduit/handlers/destination/`
- **Examples**: `FileSourceHandler`, `FileDestinationHandler`, `OCISourceHandler`
- **Characteristics**:
  - Scheme-specific operations (`calculate_metadata`, `validate_target`)
  - Created via `HandlerFactory`
  - Used by services for specific tasks

### Services (Existing Pattern)
- **Purpose**: Coordinate business logic using utility handlers
- **Location**: `src/conduit/services/`
- **Examples**: `GenerateService`, `ApplyService`
- **Characteristics**:
  - Single public method (e.g., `generate_lockfile`, `apply_lockfile`)
  - Use utility handlers via `HandlerFactory`
  - May be injected into command handlers

## Testing Strategy

### Command Handler Testing
```python
def test_pack_command_handler_creates_valid_bundle():
    # Setup command
    command = PackCommand(lockfile_path="test.lock.yaml", output_path="./bundle")
    
    # Inject dependencies (real objects, no mocking)
    pack_handler = PackCommandHandler(lockfile_service, oci_bundler)
    
    # Execute command
    result = pack_handler.handle(command)
    
    # Verify result
    assert isinstance(result, PackResult)
    assert result.bundle_path == command.output_path
    _assert_oci_compliance(Path(result.bundle_path))
```

### Benefits for Testing
- **Clear interfaces**: Explicit command/result objects
- **Dependency injection**: Easy to inject test doubles if needed
- **Single responsibility**: Each handler tests one command type
- **Real object testing**: Follows project preference for real objects over mocks

## Implementation Guidelines

### 1. Command Objects
- Use `@dataclass` for command and result objects
- Include all required parameters as fields
- Optional parameters should have default values
- Place in same module as command handler

### 2. Command Handlers
- Single `handle(command) -> result` method
- Constructor injection for dependencies
- Should be instantiable with no arguments (dependencies have defaults)
- Place in `src/conduit/handlers/` with descriptive names

### 3. CLI Integration
```python
# CLI command creates command object and invokes handler
@click.command()
@click.argument('lockfile_path')
@click.option('--output', default='./bundle')
def pack(lockfile_path: str, output: str):
    command = PackCommand(lockfile_path=lockfile_path, output_path=output)
    pack_handler = PackCommandHandler()
    result = pack_handler.handle(command)
    click.echo(f"Bundle created at: {result.bundle_path}")
```

## Migration Strategy

### Phase 1: New Commands (Immediate)
- Implement pack/unpack/verify commands using Command Handler pattern
- Create new handlers in `src/conduit/handlers/`
- Maintain existing utility handlers and services unchanged

### Phase 2: Gradual Migration (Future)
- Consider converting generate/apply commands to Command Handler pattern
- Evaluate benefits vs. migration effort for existing functionality
- Maintain backward compatibility during transition

### Phase 3: Consistency (Future)
- Standardize on Command Handler pattern for all user-facing operations
- Keep utility handlers for internal operations
- Services become implementation details of command handlers

## Consequences

### Positive
- **Clear separation**: Commands, business logic, and utilities have distinct roles
- **Testability**: Easy to test command handlers with dependency injection
- **Consistency**: Standard pattern for all command processing
- **Scalability**: Easy to add new commands following established pattern
- **CLI Integration**: Natural mapping from CLI commands to command handlers

### Negative
- **Additional Complexity**: More objects and abstractions than simple service calls
- **Learning Curve**: Team must understand Command Handler pattern
- **Migration Effort**: Existing commands may need refactoring for consistency

### Neutral
- **Pattern Familiarity**: Command Handler pattern is well-established in .NET/Java ecosystems
- **Testing Approach**: Maintains preference for real objects over mocking
- **Dependency Injection**: Aligns with existing DI practices in the codebase

## Related Patterns

### MediatR (C#/.NET)
- Command/Query Handler pattern with mediator for dispatching
- Explicit request/response objects
- Dependency injection for handlers

### CQRS (Command Query Responsibility Segregation)
- Separate models for read and write operations
- Command handlers for writes, query handlers for reads
- Event sourcing often paired with CQRS

### Django Commands
- Management commands with `handle()` method
- Options and arguments as command properties
- Similar structure to our Command Handler pattern

## References

- [MediatR Documentation](https://github.com/jbogard/MediatR)
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Command Pattern (GoF)](https://en.wikipedia.org/wiki/Command_pattern)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)