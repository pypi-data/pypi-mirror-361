# Implementation Guide: Add Trace Context to Response Objects

## 🎯 Objective

Add OpenTelemetry trace context information to all response objects in sik-llms to enable span linking without requiring manual wrapper spans.

## 🤔 Problem Statement

**Current State:**
- sik-llms automatically creates traces for all LLM operations
- Users who want to implement span linking (e.g., for evaluation pipelines) must create manual wrapper spans just to capture trace_id and span_id
- This creates redundant spans and makes the API more complex than necessary

**Desired State:**
- Response objects include trace context information when telemetry is enabled
- Users can create span links directly from response objects
- No manual wrapper spans needed for basic span linking scenarios

## 📋 Requirements

### 1. Create TraceContext Model

Create a new Pydantic model (suggest name: `TraceContext` instead of `OTELMetadata`) that contains:

**Required Fields:**
- `trace_id: str | None` - Hexadecimal string representation of the trace ID
- `span_id: str | None` - Hexadecimal string representation of the span ID

**Design Principles:**
- Fields should be `None` when telemetry is disabled (no overhead)
- Model should be extensible for future OpenTelemetry fields
- Should include helpful docstrings explaining the purpose

**Convenience Methods:**
- Add a method to create span links easily (reducing boilerplate for users)
- Method should handle None values gracefully
- Should integrate with existing `create_span_link()` function

### 2. Add TraceContext to All Response Objects

**Target Models:**
- `TextResponse`
- `ToolPredictionResponse` 
- `StructuredOutputResponse`
- Any other response models that inherit from `TokenSummary`

**Implementation Requirements:**
- Add `trace_context: TraceContext | None = None` field to each model
- Field should be `None` by default
- Should not affect existing serialization/deserialization behavior
- Must be backward compatible

### 3. Populate TraceContext During Response Creation

**When to Populate:**
- Only when telemetry is enabled (`is_telemetry_enabled()` returns `True`)
- Only when a valid span is currently active and recording
- Should extract from the current OpenTelemetry span context

**Where to Populate:**
- In the `Client.run_async()` method (base class) - this ensures all providers get the functionality
- Should happen after span creation but before response return
- Must handle cases where span context is not available

**Error Handling:**
- Should never throw exceptions if OpenTelemetry is not available
- Should gracefully handle malformed trace IDs
- Should default to `None` when extraction fails

### 4. Utility Function for Context Extraction

Create a utility function in `telemetry.py` that:
- Extracts current span context safely
- Converts trace_id and span_id to hexadecimal strings
- Returns (trace_id, span_id) tuple with proper error handling
- Returns (None, None) when telemetry disabled or no active span

## 🧪 Testing Requirements

### Unit Tests Required

**TraceContext Model Tests:**
- Test model creation with valid trace_id/span_id
- Test model creation with None values
- Test convenience methods (span link creation)
- Test model serialization/deserialization
- Test field validation and error handling

**Response Object Integration Tests:**
- Test that all response objects accept TraceContext
- Test backward compatibility (existing code continues to work)
- Test serialization includes/excludes trace_context appropriately

**Context Extraction Tests:**
- Test extraction when telemetry enabled with active span
- Test extraction when telemetry enabled but no active span
- Test extraction when telemetry disabled
- Test extraction when OpenTelemetry not available
- Test proper hex string formatting

**Integration Tests:**
- Test end-to-end: make LLM call → response includes trace context
- Test with different providers (OpenAI, Anthropic)
- Test with different response types (TextResponse, ToolPredictionResponse, etc.)
- Test that manual spans still work (don't break existing functionality)

**Edge Case Tests:**
- Test with malformed span contexts
- Test with missing OpenTelemetry imports
- Test with concurrent operations
- Test memory usage when telemetry disabled (should be minimal)

## 🎯 Success Criteria

### Functional Goals
1. **Simplified Span Linking:** Users can create span links without manual wrapper spans
2. **Zero Overhead When Disabled:** No performance impact when telemetry is disabled
3. **Backward Compatibility:** Existing code continues to work unchanged
4. **Provider Agnostic:** Works with all LLM providers (OpenAI, Anthropic, etc.)

### Code Quality Goals
1. **Comprehensive Test Coverage:** All new functionality must have unit tests
2. **Documentation:** New fields and methods must be documented
3. **Type Safety:** Proper type hints throughout
4. **Error Resilience:** Never crash the main application due to telemetry issues

## 📖 Expected Usage Patterns

### Before (Current - Requires Manual Spans)
```python
# User currently needs this verbose pattern:
with tracer.start_as_current_span("generation") as span:
    response = client([{"role": "user", "content": "Hello"}])
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

# Later for evaluation:
link = create_span_link(trace_id, span_id, {"link.type": "evaluation"})
```

### After (Desired - Direct from Response)
```python
# User can do this simple pattern:
response = client([{"role": "user", "content": "Hello"}])

# Later for evaluation:
if response.trace_context:
    link = response.trace_context.create_link({"link.type": "evaluation"})
```

## 🚫 What NOT to Change

**Preserve Existing Behavior:**
- Don't modify existing automatic span creation
- Don't change existing telemetry configuration patterns
- Don't alter performance characteristics when telemetry is disabled
- Don't break existing span linking utilities

**Maintain Design Principles:**
- Keep the "detect and respect" pattern for user configurations
- Maintain graceful degradation when OpenTelemetry not available
- Preserve the optional nature of telemetry

## 🔧 Implementation Notes

**Location Considerations:**
- `TraceContext` model should go in `models_base.py` (with other response models)
- Context extraction utility should go in `telemetry.py`
- Response object modifications happen in `models_base.py`
- Population logic goes in `Client.run_async()` method

**Performance Considerations:**
- Context extraction should be fast (happens on every LLM call when telemetry enabled)
- Should not impact response serialization performance
- Memory overhead should be minimal

**Extensibility Considerations:**
- Design should accommodate future OpenTelemetry fields (trace_state, baggage, etc.)
- Should not preclude adding more advanced telemetry features later
- API should be intuitive for users not familiar with OpenTelemetry internals