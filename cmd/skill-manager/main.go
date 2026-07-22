package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/badowhp/skill-mania/internal/skillmanager"
)

const version = "0.6.0"

func main() {
	if err := run(os.Args[1:]); err != nil {
		log.Printf("skill manager: %v", err)
		os.Exit(1)
	}
}

func run(arguments []string) error {
	command := "serve"
	if len(arguments) > 0 && len(arguments[0]) > 0 && arguments[0][0] != '-' {
		command = arguments[0]
		arguments = arguments[1:]
	}
	switch command {
	case "serve":
		return serve(arguments)
	case "healthcheck":
		return healthcheck(arguments)
	case "version":
		fmt.Println(version)
		return nil
	default:
		return fmt.Errorf("unknown command %q", command)
	}
}

func serve(arguments []string) error {
	flags := flag.NewFlagSet("serve", flag.ContinueOnError)
	catalog := flags.String("catalog", environment("SKILL_MANAGER_CATALOG", "."), "catalog root containing skills, config, and benchmarks")
	listen := flags.String("listen", environment("SKILL_MANAGER_LISTEN", "127.0.0.1:8787"), "HTTP listen address")
	agentsDir := flags.String("agents-dir", environment("AGENT_SKILLS_DIR", "/targets/agents"), "Codex skills target directory")
	claudeDir := flags.String("claude-dir", environment("CLAUDE_SKILLS_DIR", "/targets/claude"), "Claude Code target directory")
	if err := flags.Parse(arguments); err != nil {
		return err
	}

	repository, err := skillmanager.Open(*catalog, []skillmanager.TargetConfig{
		{ID: "agents", Name: "Codex", Path: *agentsDir},
		{ID: "claude", Name: "Claude Code", Path: *claudeDir},
	})
	if err != nil {
		return err
	}
	application, err := skillmanager.NewServer(repository)
	if err != nil {
		return err
	}

	server := &http.Server{
		Addr:              *listen,
		Handler:           application.Handler(),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
		MaxHeaderBytes:    1 << 20,
	}
	context, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	serverError := make(chan error, 1)
	go func() {
		log.Printf("Skill Mania Manager %s listening on %s", version, *listen)
		serverError <- server.ListenAndServe()
	}()

	select {
	case <-context.Done():
		shutdownContext, cancel := contextWithTimeout(10 * time.Second)
		defer cancel()
		if err := server.Shutdown(shutdownContext); err != nil {
			return fmt.Errorf("shutdown: %w", err)
		}
		return nil
	case err := <-serverError:
		if errors.Is(err, http.ErrServerClosed) {
			return nil
		}
		return err
	}
}

func healthcheck(arguments []string) error {
	flags := flag.NewFlagSet("healthcheck", flag.ContinueOnError)
	endpoint := flags.String("url", "http://127.0.0.1:8080/healthz", "health endpoint")
	if err := flags.Parse(arguments); err != nil {
		return err
	}
	client := &http.Client{Timeout: 2 * time.Second}
	response, err := client.Get(*endpoint)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("health endpoint returned %s", response.Status)
	}
	return nil
}

func contextWithTimeout(timeout time.Duration) (context.Context, context.CancelFunc) {
	return context.WithTimeout(context.Background(), timeout)
}

func environment(name string, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}
