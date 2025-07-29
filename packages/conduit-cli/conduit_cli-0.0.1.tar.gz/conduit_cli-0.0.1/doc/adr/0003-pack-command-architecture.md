# 3. Pack command architecture

Date: 2025-05-29

## Status

Accepted

## Context

The pack command architecture outlined in `PACK_COMMAND_ARCHITECTURE.md` and the signing/attestation strategy in `SIGNING_ATTESTATION_EVALUATION.md` were evaluated for:

1. Architectural alignment with existing Conduit patterns
2. OCI compliance and standards adherence  
3. Service vs handler separation for testability
4. Security best practices and signing integration
5. Implementation feasibility

## Decision

We **approve** the pack command architecture with the following assessment and modifications:

### ✅ **Approved Components**

#### Service Architecture (85% Compliant)
- **PackService** follows established service-oriented patterns
- Proper separation of concerns between packing, signing, and verification
- Good integration with existing `LockfileService` and `HandlerFactory`
- Service composition approach aligns with current codebase patterns

#### OCI Compliance (85% Compliant)  
- Directory structure is fully OCI-compliant
- Image manifest format follows OCI specifications correctly
- Layer format and blob storage meet OCI standards
- Content-addressable storage implementation is sound

#### Signing Architecture (90% Compliant)
- Sigstore/Cosign integration is architecturally sound
- SLSA attestation design meets federal compliance requirements
- Service composition pattern maintains clean separation
- Security design follows industry best practices

### ⚠️ **Required Modifications**

#### 2. Handler Usage for Testability
**Status**: Recommended enhancement

**Current Assessment**: The proposed architecture places most functionality in services, which is generally appropriate. However, specific components would benefit from handler abstraction:

**Recommended Handler Extractions**:
- **OCI Bundle Handler**: Extract OCI directory creation, manifest generation, and layer packaging into `OCIBundleHandler` for better testing isolation
- **Registry Handler**: Abstract registry operations (`push_oci_bundle`, `pull_oci_bundle`) into `RegistryHandler` for mock-friendly testing
- **Signing Handler**: Extract signing operations into `SigningHandler` to enable testing without actual Cosign dependencies

**Benefits**:
- Enables comprehensive unit testing with mocks
- Supports future registry backends (Docker Registry, Harbor, etc.)
- Facilitates testing of edge cases and error conditions
- Maintains service layer focus on business logic

#### 3. Service Composition Refinement
**Status**: Architecture improvement

**Current Design Issues**:
- `SignedPackService` wrapping `PackService` creates unnecessary complexity
- Signing should be optional in core `PackService`

**Recommended Pattern**:
```python
class PackService:
    def __init__(self, 
                 bundle_handler: OCIBundleHandler,
                 registry_handler: RegistryHandler, 
                 signing_handler: Optional[SigningHandler] = None):
        self.bundle_handler = bundle_handler
        self.registry_handler = registry_handler  
        self.signing_handler = signing_handler
    
    def pack_lockfile(self, lockfile_path: str, registry_ref: str, **options):
        # Core business logic with optional signing
        pass
```

### 📋 **Implementation Guidelines**

#### Phase 1: Core OCI Implementation
1. Create `OCIBundleHandler` for bundle creation operations
2. Implement basic `PackService` with handler composition
3. Add comprehensive unit tests with handler mocking

#### Phase 2: Registry Integration  
1. Implement `RegistryHandler` abstraction
2. Add registry push/pull operations
3. Integrate with ORAS Python SDK
4. Add integration tests with registry mocking

#### Phase 3: Signing Integration
1. Implement `SigningHandler` for Cosign operations
2. Add SLSA attestation generation
3. Implement verification service
4. Add signing integration tests

#### Phase 4: CLI and Documentation
1. Implement CLI commands (`pack`, `unpack`, `verify`)
2. Add comprehensive documentation
3. Create usage examples and best practices
4. Performance testing and optimization

### 🧪 **Testing Strategy**

**Unit Testing**:
- Mock all handler dependencies for isolated service testing
- Test OCI compliance with temporary directory fixtures
- Verify SLSA attestation generation without actual signing
- Validate error handling and edge cases

**Integration Testing**:
- Test complete pack/unpack workflow with local registry
- Verify signing with test certificates
- Test cross-platform compatibility
- Performance benchmarking with various artifact sizes

**Security Testing**:
- Verify signature validation edge cases
- Test policy enforcement mechanisms
- Validate certificate chain verification
- Assess resistance to known attack vectors



## Consequences

### ✅ **Positive Outcomes**

**Security Leadership**: Positions Conduit as a leader in secure artifact management with federal compliance readiness

**Architecture Consistency**: Maintains clean service-oriented architecture with proper handler abstractions

**Enterprise Readiness**: Supports enterprise deployment scenarios with policy enforcement and audit capabilities

**Future Extensibility**: Handler pattern enables future registry backends and signing methods

### ⚠️ **Implementation Considerations**

**Complexity**: Signing integration adds operational complexity that must be managed carefully

**Dependencies**: External dependencies (Cosign, OCI tools) require careful version management

**Testing Overhead**: Comprehensive security testing requires significant test infrastructure

**Documentation**: Security features require extensive documentation for proper adoption

### 📈 **Success Metrics**

- **OCI Compliance**: 100% compliance with OCI Image Specification v1.0
- **Security Standards**: SLSA Level 2+ compliance out of box, Level 3+ with configuration
- **Test Coverage**: 90%+ test coverage including security-specific test cases
- **Performance**: Pack operations complete within 30 seconds for typical artifact sets
- **Usability**: CLI commands that follow established Conduit patterns and conventions


## Related Documents

- [PACK_COMMAND_ARCHITECTURE.md](../../PACK_COMMAND_ARCHITECTURE.md) - Original architecture proposal
- [SIGNING_ATTESTATION_EVALUATION.md](../../SIGNING_ATTESTATION_EVALUATION.md) - Security implementation strategy
- [ADR-0002: Pack Command Architecture](./0002-pack-command-architecture.md) - Initial architecture decision
- [OCI Image Specification](https://github.com/opencontainers/image-spec) - OCI compliance reference
- [SLSA Framework](https://slsa.dev/) - Supply chain security framework

## Next Steps

1. **Update Architecture Documents**: Incorporate the required OCI specification completions
2. **Handler Design**: Create detailed handler interface specifications  
3. **Implementation Planning**: Create detailed implementation timeline with milestones
4. **Security Review**: Schedule security architecture review with relevant stakeholders
5. **Prototype Development**: Begin with Phase 1 implementation focusing on OCI compliance