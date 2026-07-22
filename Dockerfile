FROM golang:1.26.5-alpine3.24 AS build

WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal

RUN go test ./...
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/skill-manager ./cmd/skill-manager
RUN mkdir -p /out/targets/agents /out/targets/claude

FROM scratch

COPY --from=build --chown=65532:65532 /out/skill-manager /skill-manager
COPY --from=build --chown=65532:65532 /out/targets /targets
COPY --chown=65532:65532 skills /catalog/skills
COPY --chown=65532:65532 config/skill-groups.json /catalog/config/skill-groups.json
COPY --chown=65532:65532 benchmarks/catalog.json /catalog/benchmarks/catalog.json

USER 65532:65532
EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=2s --start-period=3s --retries=5 \
  CMD ["/skill-manager", "healthcheck", "--url", "http://127.0.0.1:8080/healthz"]

ENTRYPOINT ["/skill-manager"]
CMD ["serve", "--catalog", "/catalog", "--listen", "0.0.0.0:8080", "--agents-dir", "/targets/agents", "--claude-dir", "/targets/claude"]
