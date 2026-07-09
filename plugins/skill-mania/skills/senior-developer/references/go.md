# Go

## Change Discipline
- Use the repository's declared Go version and toolchain. Inspect `go.mod`, `go.work`, build tags, and generated-code conventions before changing dependencies or packages.
- Keep public errors and interfaces stable unless a contract change is explicit. Wrap errors only when the caller can still use `errors.Is` or `errors.As` meaningfully.
- Pass request-scoped `context.Context` through I/O boundaries. Do not replace a caller context with `context.Background()` inside request or worker paths.
- Make goroutine ownership, cancellation, completion, and error collection explicit. Do not start work that a caller cannot stop or wait for.

## Services And Concurrency
- Set server, client, and database timeouts deliberately. A context deadline does not replace every transport-level limit.
- Avoid shared mutable package state in handlers. Prefer dependency injection through small structs and constructors already used by the repository.
- Use channels for ownership transfer or coordination, not as a default queue. Close only from the sending side that owns completion.
- Bound fan-out, retries, and queues. Preserve cancellation and backpressure when parallelizing work.

## Verification And Diagnostics
- Start with the narrow package test. Use `go test ./...` when shared behavior changed; use `go test -race ./...` when changed code has meaningful concurrent access.
- Run `go vet ./...` or the repository's equivalent before claiming a broad change is complete.
- Profile a reproduced production-shaped problem with `pprof` before tuning allocations, locks, or goroutines. Measure before retaining caches or pools.
- Keep structured logs request-safe and correlate errors, traces, and metrics without logging credentials or personal data.
