package skillmanager

import (
	"crypto/rand"
	"crypto/subtle"
	"embed"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	"io"
	"io/fs"
	"mime"
	"net"
	"net/http"
	"net/url"
	"strings"
)

//go:embed web/*
var webFiles embed.FS

type Server struct {
	repository *Repository
	csrfToken  string
	index      *template.Template
	assets     http.Handler
}

type actionRequest struct {
	Action  string   `json:"action"`
	Target  string   `json:"target"`
	Skills  []string `json:"skills"`
	Confirm bool     `json:"confirm"`
}

func NewServer(repository *Repository) (*Server, error) {
	tokenBytes := make([]byte, 32)
	if _, err := rand.Read(tokenBytes); err != nil {
		return nil, fmt.Errorf("generate request token: %w", err)
	}
	indexData, err := webFiles.ReadFile("web/index.html")
	if err != nil {
		return nil, fmt.Errorf("read index template: %w", err)
	}
	index, err := template.New("index").Parse(string(indexData))
	if err != nil {
		return nil, fmt.Errorf("parse index template: %w", err)
	}
	assetsFS, err := fs.Sub(webFiles, "web")
	if err != nil {
		return nil, fmt.Errorf("open embedded assets: %w", err)
	}
	return &Server{
		repository: repository,
		csrfToken:  base64.RawURLEncoding.EncodeToString(tokenBytes),
		index:      index,
		assets:     http.FileServer(http.FS(assetsFS)),
	}, nil
}

func (s *Server) CSRFToken() string {
	return s.csrfToken
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", s.handleIndex)
	mux.HandleFunc("GET /healthz", s.handleHealth)
	mux.HandleFunc("GET /api/catalog", s.handleCatalog)
	mux.HandleFunc("POST /api/actions", s.handleAction)
	mux.Handle("GET /assets/", http.StripPrefix("/assets/", s.assets))
	return s.securityHeaders(s.allowedHost(mux))
}

func (s *Server) handleIndex(writer http.ResponseWriter, request *http.Request) {
	if request.URL.Path != "/" {
		http.NotFound(writer, request)
		return
	}
	writer.Header().Set("Content-Type", "text/html; charset=utf-8")
	writer.Header().Set("Cache-Control", "no-store")
	if err := s.index.Execute(writer, map[string]string{"CSRFToken": s.csrfToken}); err != nil {
		http.Error(writer, "Unable to render the manager.", http.StatusInternalServerError)
	}
}

func (s *Server) handleHealth(writer http.ResponseWriter, _ *http.Request) {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.WriteHeader(http.StatusOK)
	_, _ = writer.Write([]byte("{\"status\":\"ok\"}\n"))
}

func (s *Server) handleCatalog(writer http.ResponseWriter, _ *http.Request) {
	writeJSON(writer, http.StatusOK, s.repository.Snapshot())
}

func (s *Server) handleAction(writer http.ResponseWriter, request *http.Request) {
	if !sameOrigin(request) {
		writeJSON(writer, http.StatusForbidden, map[string]string{"error": "Origin is not allowed."})
		return
	}
	provided := request.Header.Get("X-CSRF-Token")
	if subtle.ConstantTimeCompare([]byte(provided), []byte(s.csrfToken)) != 1 {
		writeJSON(writer, http.StatusForbidden, map[string]string{"error": "Request token is invalid."})
		return
	}
	if mediaType, _, err := mime.ParseMediaType(request.Header.Get("Content-Type")); err != nil || mediaType != "application/json" {
		writeJSON(writer, http.StatusUnsupportedMediaType, map[string]string{"error": "Content-Type must be application/json."})
		return
	}
	request.Body = http.MaxBytesReader(writer, request.Body, 64<<10)
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()
	var input actionRequest
	if err := decoder.Decode(&input); err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]string{"error": "Request body is invalid."})
		return
	}
	if err := decoder.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
		writeJSON(writer, http.StatusBadRequest, map[string]string{"error": "Request body must contain one JSON object."})
		return
	}
	if input.Action != "install" && input.Action != "remove" {
		writeJSON(writer, http.StatusBadRequest, map[string]string{"error": "Action must be install or remove."})
		return
	}
	if input.Action == "remove" && !input.Confirm {
		writeJSON(writer, http.StatusBadRequest, map[string]string{"error": "Removal requires explicit confirmation."})
		return
	}
	if len(input.Skills) == 0 || len(input.Skills) > 100 {
		writeJSON(writer, http.StatusBadRequest, map[string]string{"error": "Select between 1 and 100 skills."})
		return
	}
	response := s.repository.Apply(input.Action, input.Target, input.Skills)
	status := http.StatusOK
	if responseHasErrors(response) {
		status = http.StatusMultiStatus
	}
	writeJSON(writer, status, response)
}

func (s *Server) securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writer.Header().Set("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
		writer.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
		writer.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
		writer.Header().Set("Referrer-Policy", "no-referrer")
		writer.Header().Set("X-Content-Type-Options", "nosniff")
		writer.Header().Set("X-Frame-Options", "DENY")
		next.ServeHTTP(writer, request)
	})
}

func (s *Server) allowedHost(next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		host := strings.ToLower(request.Host)
		if parsedHost, _, err := net.SplitHostPort(request.Host); err == nil {
			host = parsedHost
		}
		host = strings.Trim(host, "[]")
		if host != "localhost" && host != "127.0.0.1" && host != "::1" {
			writeJSON(writer, http.StatusMisdirectedRequest, map[string]string{"error": "Use localhost or a loopback address."})
			return
		}
		next.ServeHTTP(writer, request)
	})
}

func sameOrigin(request *http.Request) bool {
	origin := request.Header.Get("Origin")
	if origin == "" {
		return false
	}
	parsed, err := url.Parse(origin)
	if err != nil || parsed.Scheme != "http" {
		return false
	}
	return strings.EqualFold(parsed.Host, request.Host)
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.Header().Set("Cache-Control", "no-store")
	writer.WriteHeader(status)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(true)
	if err := encoder.Encode(value); err != nil && !errors.Is(err, http.ErrHandlerTimeout) {
		return
	}
}
