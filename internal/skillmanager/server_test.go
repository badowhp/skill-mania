package skillmanager

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestServerRejectsUntrustedHostAndSetsSecurityHeaders(t *testing.T) {
	repository, _, _ := createTestRepository(t)
	server, err := NewServer(repository)
	if err != nil {
		t.Fatalf("create server: %v", err)
	}
	handler := server.Handler()

	trustedRequest := httptest.NewRequest(http.MethodGet, "http://localhost/healthz", nil)
	trustedResponse := httptest.NewRecorder()
	handler.ServeHTTP(trustedResponse, trustedRequest)
	if trustedResponse.Code != http.StatusOK {
		t.Fatalf("health status = %d", trustedResponse.Code)
	}
	if value := trustedResponse.Header().Get("Content-Security-Policy"); value == "" {
		t.Fatal("Content-Security-Policy header is missing")
	}
	if value := trustedResponse.Header().Get("X-Content-Type-Options"); value != "nosniff" {
		t.Fatalf("X-Content-Type-Options = %q", value)
	}

	untrustedRequest := httptest.NewRequest(http.MethodGet, "http://attacker.example/healthz", nil)
	untrustedResponse := httptest.NewRecorder()
	handler.ServeHTTP(untrustedResponse, untrustedRequest)
	if untrustedResponse.Code != http.StatusMisdirectedRequest {
		t.Fatalf("untrusted host status = %d", untrustedResponse.Code)
	}
}

func TestServerRequiresOriginCSRFAndRemovalConfirmation(t *testing.T) {
	repository, _, _ := createTestRepository(t)
	server, err := NewServer(repository)
	if err != nil {
		t.Fatalf("create server: %v", err)
	}
	handler := server.Handler()
	body := `{"action":"install","target":"agents","skills":["demo-skill"]}`

	missingOrigin := httptest.NewRequest(http.MethodPost, "http://localhost/api/actions", strings.NewReader(body))
	missingOrigin.Header.Set("Content-Type", "application/json")
	missingOrigin.Header.Set("X-CSRF-Token", server.CSRFToken())
	missingOriginResponse := httptest.NewRecorder()
	handler.ServeHTTP(missingOriginResponse, missingOrigin)
	if missingOriginResponse.Code != http.StatusForbidden {
		t.Fatalf("missing-origin status = %d", missingOriginResponse.Code)
	}

	badToken := httptest.NewRequest(http.MethodPost, "http://localhost/api/actions", strings.NewReader(body))
	badToken.Header.Set("Content-Type", "application/json")
	badToken.Header.Set("Origin", "http://localhost")
	badToken.Header.Set("X-CSRF-Token", "wrong")
	badTokenResponse := httptest.NewRecorder()
	handler.ServeHTTP(badTokenResponse, badToken)
	if badTokenResponse.Code != http.StatusForbidden {
		t.Fatalf("bad-token status = %d", badTokenResponse.Code)
	}

	installRequest := httptest.NewRequest(http.MethodPost, "http://localhost/api/actions", strings.NewReader(body))
	installRequest.Header.Set("Content-Type", "application/json")
	installRequest.Header.Set("Origin", "http://localhost")
	installRequest.Header.Set("X-CSRF-Token", server.CSRFToken())
	installResponse := httptest.NewRecorder()
	handler.ServeHTTP(installResponse, installRequest)
	if installResponse.Code != http.StatusOK {
		t.Fatalf("valid install status = %d, body = %s", installResponse.Code, installResponse.Body.String())
	}

	removeBody := `{"action":"remove","target":"agents","skills":["demo-skill"]}`
	removeRequest := httptest.NewRequest(http.MethodPost, "http://localhost/api/actions", strings.NewReader(removeBody))
	removeRequest.Header.Set("Content-Type", "application/json")
	removeRequest.Header.Set("Origin", "http://localhost")
	removeRequest.Header.Set("X-CSRF-Token", server.CSRFToken())
	removeResponse := httptest.NewRecorder()
	handler.ServeHTTP(removeResponse, removeRequest)
	if removeResponse.Code != http.StatusBadRequest {
		t.Fatalf("unconfirmed remove status = %d", removeResponse.Code)
	}
}
