"""Hand-curated code map for scrumlr.io.

Every evidence item is {path, symbol, match}. The generator resolves `match`
to a line number by searching the tracked working-tree file. If the path is
untracked or the match string is absent, generation aborts. Nothing here is
allowed to be a guess.
"""

REPO = "/Users/randallnoval/Code/scrumlr.io"

SCANNED_SCOPE = ["src", "server/src"]

# Real modules deliberately left off the 20-node map, so a reader knows they exist.
NOT_MAPPED = [
    {"path": "server/src/services/users", "why": "Same shape as svc-notes: DB + realtime broker. Reached via api-http /user and /login."},
    {"path": "server/src/services/reactions", "why": "Note-level emoji reactions. Same shape as svc-notes."},
    {"path": "server/src/services/board_reactions", "why": "Ephemeral board-wide reactions. Same shape as svc-notes."},
    {"path": "server/src/services/health", "why": "Backs GET /health; checks database and broker."},
    {"path": "server/src/services/services.go", "why": "The interface contract between api-http and every service. Read this first when tracing a handler."},
    {"path": "server/src/common", "why": "Shared DTOs, filters, error helpers and cookie sealing."},
    {"path": "server/src/logger", "why": "Zap logger plus chi request-id middleware."},
    {"path": "server/src/identifiers", "why": "Context key constants for board/user/column/note ids."},
    {"path": "src/utils", "why": "Auth helpers (utils/auth.ts drives sign-in), export, timer, toast, hooks."},
    {"path": "src/types", "why": "TypeScript models shared by store, api and components, including the websocket event union."},
    {"path": "src/constants", "why": "Colors, hotkeys, storage keys."},
    {"path": "cypress", "why": "One end-to-end spec (landingPageToBoard). Not part of the runtime graph."},
    {"path": "deployment", "why": "Docker compose, SKE manifests, nginx.conf and the root Dockerfile. Not scanned for this map."},
]

EXCLUDED_DIRS = [
    "node_modules",
    ".git",
    "build",
    "dist",
    "src/assets",
    "public",
    "docs",
    "k8s",
    "scripts",
    ".github",
]

# ---------------------------------------------------------------- nodes ----

NODES = [
    # ---------------------------------------------------------- frontend --
    {
        "id": "web-entry",
        "path": "src/index.tsx",
        "role": "Browser app bootstrap. Mounts React, wires the Redux Provider, i18n, "
                "toasts and optional Plausible analytics, then renders the router.",
        "entrypoints": [
            "createRoot(document.getElementById(\"root\"))",
            "Plausible({domain: ANALYTICS_DATA_DOMAIN, apiHost: ANALYTICS_SRC})",
        ],
        "tests": [],
        "constraints": [
            "Runtime config comes from src/config.ts, which reads cookies first, then "
            "REACT_APP_* env vars, then falls back to window.location.origin + '/api'.",
            "Analytics only initialises when both ANALYTICS_DATA_DOMAIN and ANALYTICS_SRC cookies are set.",
        ],
        "evidence": [
            {"path": "src/index.tsx", "symbol": "root", "match": "const root = createRoot(document.getElementById(\"root\") as HTMLDivElement);"},
            {"path": "src/index.tsx", "symbol": "import store", "match": "import store from \"store\";"},
            {"path": "src/config.ts", "symbol": "SERVER_HTTP_URL", "match": "export const SERVER_HTTP_URL ="},
        ],
    },
    {
        "id": "web-routes",
        "path": "src/routes",
        "role": "React Router route table and route-level guards. Owns the URL surface: "
                "homepage, /new, /login, /board/:boardId (+ nested settings, voting, timer, stack).",
        "entrypoints": [
            "Router (src/routes/Router.tsx)",
            "BoardGuard (src/routes/Board/BoardGuard.tsx)",
            "RequireAuthentication (src/routes/RequireAuthentication.tsx)",
        ],
        "tests": [
            "src/routes/__tests__/RequireAuthentication.test.tsx",
            "src/routes/StackView/__tests__/StackView.test.tsx",
            "src/routes/NotFound/NotFound.test.tsx",
        ],
        "constraints": [
            "BoardGuard is the only place that dispatches joinBoard/leaveBoard; the websocket "
            "lifecycle hangs off those actions in the store middleware.",
            "Every board route is wrapped in RequireAuthentication.",
        ],
        "evidence": [
            {"path": "src/routes/Router.tsx", "symbol": "Router", "match": "const Router = () => ("},
            {"path": "src/routes/Router.tsx", "symbol": "board route", "match": "path=\"/board/:boardId\""},
            {"path": "src/routes/Board/BoardGuard.tsx", "symbol": "joinBoard dispatch", "match": "store.dispatch(Actions.joinBoard(boardId!));"},
        ],
    },
    {
        "id": "web-components",
        "path": "src/components",
        "role": "All React UI. Board canvas, columns, notes, voting, timer, settings dialogs, "
                "participant list. Components read state with useSelector and write by dispatching actions.",
        "entrypoints": [
            "Board (src/components/Board/Board.tsx)",
            "NoteInput (src/components/NoteInput/NoteInput.tsx)",
            "SettingsDialog (src/components/SettingsDialog)",
        ],
        "tests": [
            "src/components/Board/__tests__/Board.test.tsx",
            "src/components/NoteInput/__tests__/NoteInput.test.tsx",
            "src/components/Column/__tests__/Column.test.tsx",
            "src/components/Votes/__tests__/Votes.test.tsx",
            "src/components/SettingsDialog/__tests__/SettingsDialog.test.tsx",
        ],
        "constraints": [
            "Most components dispatch actions and let the store middleware do the HTTP call, but a few "
            "call src/api directly: Timer.tsx, SettingsDialog/ExportBoard/PrintView/PrintView.tsx and "
            "SettingsDialog/Feedback/Feedback.tsx.",
            "Largest module in the repo by file count - treat it as a directory, not a unit.",
        ],
        "evidence": [
            {"path": "src/components/NoteInput/NoteInput.tsx", "symbol": "addNote dispatch", "match": "dispatch(Actions.addNote(columnId!, content));"},
            {"path": "src/components/NoteInput/NoteInput.tsx", "symbol": "import Actions", "match": "import {Actions} from \"store/action\";"},
        ],
    },
    {
        "id": "web-store",
        "path": "src/store",
        "role": "Redux Toolkit store: actions, reducers, and a middleware chain. The middleware layer "
                "is the side-effect boundary - it issues REST calls and owns the board websocket.",
        "entrypoints": [
            "store (src/store/index.ts)",
            "passBoardMiddleware (src/store/middleware/board.tsx) - opens/closes the board socket",
            "passNoteMiddleware (src/store/middleware/note.tsx)",
        ],
        "tests": [],
        "constraints": [
            "One websocket per board, held in a module-level `socket` variable in middleware/board.tsx. "
            "Opened on Action.PermittedBoardAccess, closed on Action.LeaveBoard.",
            "Incoming server events are translated into dispatches inside the socket onmessage handler; "
            "reducers never talk to the network.",
            "parseMiddleware stamps every action with {user, board, voting, serverTimeOffset} context "
            "before the per-domain middleware run.",
        ],
        "evidence": [
            {"path": "src/store/index.ts", "symbol": "parseMiddleware", "match": "const parseMiddleware = (stateAPI: MiddlewareAPI<Dispatch, ApplicationState>)"},
            {"path": "src/store/middleware/board.tsx", "symbol": "socket", "match": "socket = new Socket(`${SERVER_WEBSOCKET_URL}/boards/${action.boardId}`, {"},
            {"path": "src/store/middleware/board.tsx", "symbol": "INIT handler", "match": "if (message.type === \"INIT\") {"},
            {"path": "src/store/middleware/note.tsx", "symbol": "API.addNote", "match": "API.addNote(action.context.board!, action.columnId, action.text)"},
        ],
    },
    {
        "id": "web-api",
        "path": "src/api",
        "role": "Thin REST client. One module per resource, all merged into a single `API` object. "
                "Every call is window.fetch with credentials: \"include\".",
        "entrypoints": [
            "API (src/api/index.ts)",
            "BoardAPI (src/api/board.ts)",
            "NoteAPI (src/api/note.ts)",
            "AuthAPI (src/api/auth.ts)",
        ],
        "tests": [],
        "constraints": [
            "Base URL is SERVER_HTTP_URL from src/config.ts; it already ends in /api in the default case.",
            "Auth is cookie-based - every fetch sets credentials: \"include\"; there is no Authorization header.",
            "Each function throws on a non-expected status rather than returning an error value.",
        ],
        "evidence": [
            {"path": "src/api/index.ts", "symbol": "API", "match": "export const API = {"},
            {"path": "src/api/board.ts", "symbol": "createBoard", "match": "const response = await fetch(`${SERVER_HTTP_URL}/boards`, {"},
            {"path": "src/api/note.ts", "symbol": "addNote", "match": "const response = await fetch(`${SERVER_HTTP_URL}/boards/${boardId}/notes`, {"},
            {"path": "src/api/auth.ts", "symbol": "signInAnonymously", "match": "const response = await fetch(`${SERVER_HTTP_URL}/login/anonymous`, {"},
        ],
    },
    # ----------------------------------------------------------- backend --
    {
        "id": "server-main",
        "path": "server/src/main.go",
        "role": "Go process entrypoint and composition root. Parses CLI flags / env / TOML, runs "
                "migrations, picks the message broker, builds every service, and starts the HTTP server.",
        "entrypoints": [
            "main()",
            "run(c *cli.Context)",
        ],
        "tests": [],
        "constraints": [
            "Migrations run before anything else; the process exits if they fail.",
            "Redis wins over NATS: if --redis-address is set, NATS is not used at all.",
            "Refuses to start without --key unless --insecure is passed (then a bundled dev keypair signs JWTs).",
            "OAuth providers are only registered when client id, secret and --auth-callback-host are all set.",
        ],
        "evidence": [
            {"path": "server/src/main.go", "symbol": "run", "match": "func run(c *cli.Context) error {"},
            {"path": "server/src/main.go", "symbol": "MigrateDatabase", "match": "db, err := migrations.MigrateDatabase(c.String(\"database\"))"},
            {"path": "server/src/main.go", "symbol": "broker selection", "match": "if c.String(\"redis-address\") != \"\" {"},
            {"path": "server/src/main.go", "symbol": "ListenAndServe", "match": "return http.ListenAndServe(port, s)"},
        ],
    },
    {
        "id": "api-http",
        "path": "server/src/api",
        "role": "HTTP + websocket layer (go-chi). Route table, auth middleware, board role guards "
                "(participant / moderator / editable), request and response DTO handling, and the two "
                "websocket endpoints that stream board state to clients.",
        "entrypoints": [
            "New (server/src/api/router.go)",
            "publicRoutes / protectedRoutes (server/src/api/router.go)",
            "openBoardSocket (server/src/api/boards_listen_on_board.go)",
            "listenOnBoardSessionRequest (server/src/api/board_session_requests_listen_on_request.go)",
        ],
        "tests": [
            "server/src/api/event_filter_test.go",
            "server/src/api/notes_test.go",
            "server/src/api/votes_test.go",
            "server/src/api/votings_test.go",
            "server/src/api/json_parse_test.go",
        ],
        "constraints": [
            "Public routes: /info, /health, /feedback, /login/*. Everything else sits behind "
            "auth.Verifier + jwtauth.Authenticator + auth.AuthContext.",
            "Board authorisation is middleware, not handler code: BoardParticipantContext, "
            "BoardModeratorContext, BoardEditableContext.",
            "Server holds a map of live board subscriptions keyed by board UUID; it is in-process "
            "state, so horizontal scaling relies on the broker fan-out, not shared memory.",
            "CORS is only installed when origin checking is disabled (--disable-check-origin).",
        ],
        "evidence": [
            {"path": "server/src/api/router.go", "symbol": "New", "match": "func New("},
            {"path": "server/src/api/router.go", "symbol": "publicRoutes", "match": "func (s *Server) publicRoutes(r chi.Router) chi.Router {"},
            {"path": "server/src/api/router.go", "symbol": "protectedRoutes", "match": "func (s *Server) protectedRoutes(r chi.Router) {"},
            {"path": "server/src/api/boards_listen_on_board.go", "symbol": "openBoardSocket", "match": "func (s *Server) openBoardSocket(w http.ResponseWriter, r *http.Request) {"},
            {"path": "server/src/api/context.go", "symbol": "BoardParticipantContext", "match": "func (s *Server) BoardParticipantContext(next http.Handler) http.Handler {"},
        ],
    },
    {
        "id": "auth",
        "path": "server/src/auth",
        "role": "JWT signing/verification and OAuth provider setup (goth). Turns an external identity "
                "into a scrumlr user and puts the user id into the request context.",
        "entrypoints": [
            "NewAuthConfiguration (server/src/auth/auth.go)",
            "Auth interface: Sign / Verifier / Exists",
            "AuthContext middleware (server/src/auth/auth_context.go)",
        ],
        "tests": [],
        "constraints": [
            "Supported providers are Google, GitHub, Microsoft, Azure AD and Apple - all via goth.",
            "Two JWT keys exist: a real one and an 'unsafe' bundled dev key under auth/devkeys. "
            "Never run with the unsafe key outside local development.",
            "Identity is carried in a cookie, which is why the browser client uses credentials: \"include\".",
        ],
        "evidence": [
            {"path": "server/src/auth/auth.go", "symbol": "Auth", "match": "type Auth interface {"},
            {"path": "server/src/auth/auth.go", "symbol": "NewAuthConfiguration", "match": "func NewAuthConfiguration(providers map[string]AuthProviderConfiguration, unsafePrivateKey, privateKey string, database *database.Database) Auth {"},
            {"path": "server/src/auth/auth.go", "symbol": "google provider", "match": "p := google.New("},
        ],
    },
    {
        "id": "svc-boards",
        "path": "server/src/services/boards",
        "role": "Board and board-session domain logic: create/update/delete boards and columns, timers, "
                "join requests, participant roles, and assembling the FullBoard payload.",
        "entrypoints": [
            "NewBoardService",
            "NewBoardSessionService",
            "FullBoard",
        ],
        "tests": [],
        "constraints": [
            "Every mutation that other participants must see ends in a realtime broadcast; forgetting "
            "the broadcast is the classic bug here.",
            "Unlike svc-notes and svc-votings, BoardService holds *database.Database directly instead of a "
            "package-local DB interface, so there is no mocking seam here.",
        ],
        "evidence": [
            {"path": "server/src/services/boards/boards.go", "symbol": "BroadcastToBoard", "match": "err := s.realtime.BroadcastToBoard(board.ID, realtime.BoardEvent{"},
            {"path": "server/src/services/boards/boards.go", "symbol": "package boards", "match": "package boards"},
            {"path": "server/src/services/services.go", "symbol": "Boards", "match": "type Boards interface {"},
        ],
    },
    {
        "id": "svc-notes",
        "path": "server/src/services/notes",
        "role": "Note domain logic: create, read, update (including stacking/unstacking), delete, and "
                "the NOTES_UPDATED / NOTES_SYNC broadcasts that keep every client in step.",
        "entrypoints": [
            "NewNoteService",
            "Create / Update / Delete",
            "UpdatedNotes",
        ],
        "tests": ["server/src/services/notes/notes_test.go"],
        "constraints": [
            "Per-user note visibility is NOT applied here. The service broadcasts the full set and the "
            "API layer filters per socket in server/src/api/event_filter.go (filterNotes).",
            "DB access goes through the package-local DB interface in notes.go.",
        ],
        "evidence": [
            {"path": "server/src/services/notes/notes.go", "symbol": "NewNoteService", "match": "func NewNoteService(db DB, rt *realtime.Broker) services.Notes {"},
            {"path": "server/src/services/notes/notes.go", "symbol": "DB", "match": "type DB interface {"},
            {"path": "server/src/services/notes/notes.go", "symbol": "CreateNote", "match": "note, err := s.database.CreateNote(database.NoteInsert{"},
            {"path": "server/src/services/notes/notes.go", "symbol": "BroadcastToBoard", "match": "err := s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"},
        ],
    },
    {
        "id": "svc-votings",
        "path": "server/src/services/votings",
        "role": "Voting sessions and individual votes: open/close a voting, enforce the vote limit, "
                "tally results, and broadcast VOTING_* / VOTES_UPDATED events.",
        "entrypoints": [
            "NewVotingService",
            "Create / Update / AddVote / RemoveVote",
        ],
        "tests": ["server/src/services/votings/votings_test.go"],
        "constraints": [
            "Vote results are re-filtered per socket in server/src/api/event_filter.go: filterVoting keeps "
            "only the results for notes that caller can see and recomputes the total from them.",
        ],
        "evidence": [
            {"path": "server/src/services/votings/votings.go", "symbol": "BroadcastToBoard", "match": "err = s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"},
            {"path": "server/src/services/services.go", "symbol": "Votings", "match": "type Votings interface {"},
            {"path": "server/src/api/event_filter.go", "symbol": "filterVotingUpdated", "match": "func filterVotingUpdated(voting *VotingUpdated, userID uuid.UUID, boardSettings *dto.Board, columns []*dto.Column) *VotingUpdated {"},
        ],
    },
    {
        "id": "svc-feedback",
        "path": "server/src/services/feedback",
        "role": "Forwards in-app feedback to an external chat webhook. The only backend module that makes "
                "an outbound HTTP call to a third party.",
        "entrypoints": [
            "NewFeedbackService(webhookUrl)",
            "Create / Enabled",
        ],
        "tests": [],
        "constraints": [
            "Disabled when --feedback-webhook-url (SCRUMLR_FEEDBACK_WEBHOOK_URL) is empty. Enabled() is "
            "surfaced to the client as feedbackEnabled on GET /info.",
            "Posts a hard-coded Slack-style block payload with a German title string.",
            "No retry, no timeout override - it uses http.Post with the default client.",
        ],
        "evidence": [
            {"path": "server/src/services/feedback/feedback.go", "symbol": "NewFeedbackService", "match": "func NewFeedbackService(webhookUrl string) services.Feedback {"},
            {"path": "server/src/services/feedback/feedback.go", "symbol": "http.Post", "match": "_, err := http.Post(s.webhookUrl, \"application/json\", bytes.NewBuffer(jsonData))"},
            {"path": "server/src/services/feedback/feedback.go", "symbol": "Enabled", "match": "func (s *FeedbackService) Enabled() bool {"},
        ],
    },
    {
        "id": "database",
        "path": "server/src/database",
        "role": "Persistence layer over PostgreSQL using bun. One file per aggregate (boards, columns, "
                "notes, reactions, sessions, votes, votings, users) plus shared enum types.",
        "entrypoints": [
            "New(db *sql.DB, verbose bool)",
            "Database.Get - loads a whole board in one call",
            "CreateNote / UpdateNote / DeleteNote",
        ],
        "tests": [
            "server/src/database/database_test.go",
            "server/src/database/boards_test.go",
            "server/src/database/notes_test.go",
            "server/src/database/votings_test.go",
            "server/src/database/votes_test.go",
            "server/src/database/users_test.go",
            "server/src/database/columns_test.go",
            "server/src/database/reactions_test.go",
            "server/src/database/board_sessions_test.go",
            "server/src/database/board_session_requests_test.go",
        ],
        "constraints": [
            "Connection pool is sized 4 * GOMAXPROCS for both max-open and max-idle.",
            "Multi-table writes are single SQL statements: CreateBoard composes the board insert, the column "
            "inserts and the owner session insert into one CTE query. Read the SQL before changing the "
            "service layer.",
            "DB tests run against a real PostgreSQL instance with fixtures under database/testdata.",
        ],
        "evidence": [
            {"path": "server/src/database/database.go", "symbol": "New", "match": "func New(db *sql.DB, verbose bool) *Database {"},
            {"path": "server/src/database/database.go", "symbol": "pool sizing", "match": "maxOpenConnections := 4 * runtime.GOMAXPROCS(0)"},
            {"path": "server/src/database/database.go", "symbol": "pgdialect", "match": "d.db = bun.NewDB(db, pgdialect.New())"},
            {"path": "server/src/database/notes.go", "symbol": "CreateNote", "match": "func (d *Database) CreateNote(insert NoteInsert) (Note, error) {"},
        ],
    },
    {
        "id": "migrations",
        "path": "server/src/database/migrations",
        "role": "Embedded SQL schema migrations, applied automatically at process start via golang-migrate.",
        "entrypoints": ["MigrateDatabase(databaseUrl string)"],
        "tests": [],
        "constraints": [
            "Migration SQL is embedded into the binary with //go:embed sql - adding a file without "
            "rebuilding the binary does nothing.",
            "Runs on every boot, so a bad migration takes the whole service down rather than degrading it.",
        ],
        "evidence": [
            {"path": "server/src/database/migrations/migrations.go", "symbol": "MigrateDatabase", "match": "func MigrateDatabase(databaseUrl string) (*sql.DB, error) {"},
            {"path": "server/src/database/migrations/migrations.go", "symbol": "go:embed", "match": "//go:embed sql"},
            {"path": "server/src/database/migrations/migrations.go", "symbol": "sql.Open", "match": "db, err := sql.Open(\"postgres\", databaseUrl)"},
        ],
    },
    {
        "id": "realtime",
        "path": "server/src/realtime",
        "role": "Pub/sub abstraction for board events. One Client interface with two implementations "
                "(NATS and Redis); the Broker adds board-scoped topics and the BoardEvent vocabulary.",
        "entrypoints": [
            "NewNats(url) / NewRedis(server)",
            "Broker.BroadcastToBoard",
            "Broker.GetBoardChannel",
        ],
        "tests": [
            "server/src/realtime/nats_test.go",
            "server/src/realtime/redis_test.go",
            "server/src/realtime/boards_test.go",
            "server/src/realtime/board_sessions_requests_test.go",
            "server/src/realtime/health_test.go",
        ],
        "constraints": [
            "Topic naming is 'board.<uuid>' - see boardsSubject in realtime/boards.go.",
            "BoardEventType is the full event vocabulary the browser switches on; adding an event means "
            "touching this file and src/store/middleware/board.tsx together.",
            "GetBoardChannel swallows subscribe errors and only logs them (there is a TODO about it), so a "
            "broker outage looks like a silent board.",
        ],
        "evidence": [
            {"path": "server/src/realtime/broker.go", "symbol": "Client", "match": "type Client interface {"},
            {"path": "server/src/realtime/boards.go", "symbol": "BroadcastToBoard", "match": "func (b *Broker) BroadcastToBoard(boardID uuid.UUID, msg BoardEvent) error {"},
            {"path": "server/src/realtime/boards.go", "symbol": "boardsSubject", "match": "func boardsSubject(boardID uuid.UUID) string {"},
            {"path": "server/src/realtime/boards.go", "symbol": "BoardEventType", "match": "type BoardEventType string"},
        ],
    },
    # ---------------------------------------------------------- external --
    {
        "id": "ext-postgres",
        "path": "external://postgresql",
        "role": "EXTERNAL. PostgreSQL - the system of record for boards, columns, notes, reactions, "
                "sessions, votes and users.",
        "entrypoints": ["postgres://<host>:5432/scrumlr (--database flag / SCRUMLR_SERVER_DATABASE_URL)"],
        "tests": [],
        "constraints": [
            "Only server/src/database and server/src/database/migrations talk to it.",
            "Local dev instance is started by deployment/docker or server/docker-compose.dev.yml.",
        ],
        "evidence": [
            {"path": "server/src/database/migrations/migrations.go", "symbol": "postgres driver", "match": "db, err := sql.Open(\"postgres\", databaseUrl)"},
            {"path": "server/src/database/database.go", "symbol": "pgdialect", "match": "\"github.com/uptrace/bun/dialect/pgdialect\""},
        ],
    },
    {
        "id": "ext-nats",
        "path": "external://nats",
        "role": "EXTERNAL. NATS - the default message broker for fanning board events out across server instances.",
        "entrypoints": ["nats://localhost:4222 (--nats flag / SCRUMLR_SERVER_NATS_URL)"],
        "tests": [],
        "constraints": ["Used only when --redis-address is empty."],
        "evidence": [
            {"path": "server/src/realtime/nats.go", "symbol": "NewNats", "match": "func NewNats(url string) (*Broker, error) {"},
            {"path": "server/src/realtime/nats.go", "symbol": "nats.Connect", "match": "nc, err := nats.Connect(url)"},
        ],
    },
    {
        "id": "ext-redis",
        "path": "external://redis",
        "role": "EXTERNAL. Redis pub/sub - the alternative message broker. Selected by setting --redis-address.",
        "entrypoints": ["--redis-address / SCRUMLR_SERVER_REDIS_HOST"],
        "tests": [],
        "constraints": [
            "Takes precedence over NATS when set.",
            "Events are JSON-encoded by hand (encodeEvent/decodeEvent) rather than by the client library.",
        ],
        "evidence": [
            {"path": "server/src/realtime/redis.go", "symbol": "NewRedis", "match": "func NewRedis(server RedisServer) (*Broker, error) {"},
            {"path": "server/src/realtime/redis.go", "symbol": "redis.NewClient", "match": "rdb := redis.NewClient(&redis.Options{"},
        ],
    },
    {
        "id": "ext-oauth",
        "path": "external://oauth-providers",
        "role": "EXTERNAL. Google, GitHub, Microsoft, Azure AD and Apple OAuth endpoints, reached through goth.",
        "entrypoints": [
            "GET /login/{provider}",
            "GET /login/{provider}/callback",
        ],
        "tests": [],
        "constraints": [
            "A provider is only wired up when its client id, client secret and --auth-callback-host are all set.",
            "Redirect URI is derived as <callback-host><base-path>/login/<provider>/callback.",
        ],
        "evidence": [
            {"path": "server/src/auth/auth.go", "symbol": "goth providers", "match": "\"github.com/markbates/goth/providers/google\""},
            {"path": "server/src/api/router.go", "symbol": "provider callback route", "match": "r.Get(\"/callback\", s.verifyAuthProviderCallback)"},
        ],
    },
    {
        "id": "ext-feedback-webhook",
        "path": "external://feedback-webhook",
        "role": "EXTERNAL. Slack-compatible incoming webhook that receives user feedback submitted from the app.",
        "entrypoints": ["--feedback-webhook-url / SCRUMLR_FEEDBACK_WEBHOOK_URL"],
        "tests": [],
        "constraints": [
            "Optional. When unset, the feedback service reports Enabled() == false and the UI hides the form.",
        ],
        "evidence": [
            {"path": "server/src/services/feedback/feedback.go", "symbol": "http.Post", "match": "_, err := http.Post(s.webhookUrl, \"application/json\", bytes.NewBuffer(jsonData))"},
            {"path": "server/src/services/feedback/feedback.go", "symbol": "webhookUrl", "match": "webhookUrl string"},
        ],
    },
]

# ---------------------------------------------------------------- edges ----
# type is restricted to: imports | calls | reads | writes | publishes | subscribes
# evidence_status is "verified" when evidence is present, "unknown" when it is not.

EDGES = [
    # frontend internal
    {"from": "web-entry", "to": "web-store", "type": "imports", "evidence": [
        {"path": "src/index.tsx", "symbol": "import store", "match": "import store from \"store\";"}]},
    {"from": "web-entry", "to": "web-routes", "type": "imports", "evidence": [
        {"path": "src/index.tsx", "symbol": "import Router", "match": "import Router from \"routes/Router\";"}]},
    {"from": "web-routes", "to": "web-components", "type": "imports", "evidence": [
        {"path": "src/routes/Router.tsx", "symbol": "import SettingsDialog", "match": "import {SettingsDialog} from \"components/SettingsDialog\";"}]},
    {"from": "web-routes", "to": "web-store", "type": "calls", "evidence": [
        {"path": "src/routes/Board/BoardGuard.tsx", "symbol": "joinBoard dispatch", "match": "store.dispatch(Actions.joinBoard(boardId!));"}]},
    {"from": "web-components", "to": "web-store", "type": "calls", "evidence": [
        {"path": "src/components/NoteInput/NoteInput.tsx", "symbol": "addNote dispatch", "match": "dispatch(Actions.addNote(columnId!, content));"}]},
    {"from": "web-store", "to": "web-api", "type": "calls", "evidence": [
        {"path": "src/store/middleware/note.tsx", "symbol": "API.addNote", "match": "API.addNote(action.context.board!, action.columnId, action.text)"},
        {"path": "src/store/middleware/board.tsx", "symbol": "import API", "match": "import {API} from \"api\";"}]},

    # frontend -> backend
    {"from": "web-api", "to": "api-http", "type": "calls", "evidence": [
        {"path": "src/api/board.ts", "symbol": "POST /boards", "match": "const response = await fetch(`${SERVER_HTTP_URL}/boards`, {"},
        {"path": "server/src/api/router.go", "symbol": "POST /boards route", "match": "r.Post(\"/boards\", s.createBoard)"}]},
    {"from": "web-store", "to": "api-http", "type": "subscribes", "evidence": [
        {"path": "src/store/middleware/board.tsx", "symbol": "board socket", "match": "socket = new Socket(`${SERVER_WEBSOCKET_URL}/boards/${action.boardId}`, {"},
        {"path": "server/src/api/boards_listen_on_board.go", "symbol": "openBoardSocket", "match": "func (s *Server) openBoardSocket(w http.ResponseWriter, r *http.Request) {"}]},

    # composition root
    {"from": "server-main", "to": "migrations", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "MigrateDatabase", "match": "db, err := migrations.MigrateDatabase(c.String(\"database\"))"}]},
    {"from": "server-main", "to": "database", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "database.New", "match": "dbConnection := database.New(db, c.Bool(\"verbose\"))"}]},
    {"from": "server-main", "to": "realtime", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "realtime.NewNats", "match": "rt, err = realtime.NewNats(c.String(\"nats\"))"},
        {"path": "server/src/main.go", "symbol": "realtime.NewRedis", "match": "rt, err = realtime.NewRedis(realtime.RedisServer{"}]},
    {"from": "server-main", "to": "auth", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "NewAuthConfiguration", "match": "authConfig := auth.NewAuthConfiguration(providersMap, unsafeKeyWithNewlines, keyWithNewlines, dbConnection)"}]},
    {"from": "server-main", "to": "svc-boards", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "NewBoardService", "match": "boardService := boards.NewBoardService(dbConnection, rt)"}]},
    {"from": "server-main", "to": "svc-notes", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "NewNoteService", "match": "noteService := notes.NewNoteService(dbConnection, rt)"}]},
    {"from": "server-main", "to": "svc-votings", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "NewVotingService", "match": "votingService := votings.NewVotingService(dbConnection, rt)"}]},
    {"from": "server-main", "to": "svc-feedback", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "NewFeedbackService", "match": "feedbackService := feedback.NewFeedbackService(c.String(\"feedback-webhook-url\"))"}]},
    {"from": "server-main", "to": "api-http", "type": "calls", "evidence": [
        {"path": "server/src/main.go", "symbol": "api.New", "match": "s := api.New("},
        {"path": "server/src/main.go", "symbol": "ListenAndServe", "match": "return http.ListenAndServe(port, s)"}]},

    # api layer
    {"from": "api-http", "to": "auth", "type": "calls", "evidence": [
        {"path": "server/src/api/router.go", "symbol": "auth.Verifier", "match": "r.Use(s.auth.Verifier())"},
        {"path": "server/src/api/router.go", "symbol": "AuthContext", "match": "r.Use(auth.AuthContext)"}]},
    {"from": "api-http", "to": "svc-boards", "type": "calls", "evidence": [
        {"path": "server/src/api/boards.go", "symbol": "boards.Create", "match": "b, err := s.boards.Create(r.Context(), body)"},
        {"path": "server/src/api/boards_listen_on_board.go", "symbol": "boards.FullBoard", "match": "board, requests, sessions, columns, notes, reactions, votings, votes, err := s.boards.FullBoard(r.Context(), id)"}]},
    {"from": "api-http", "to": "svc-notes", "type": "calls", "evidence": [
        {"path": "server/src/api/notes.go", "symbol": "notes.Create", "match": "note, err := s.notes.Create(r.Context(), body)"},
        {"path": "server/src/api/notes.go", "symbol": "notes.Delete", "match": "if err := s.notes.Delete(r.Context(), body, note); err != nil {"},
        {"path": "server/src/api/router.go", "symbol": "initNoteResources", "match": "func (s *Server) initNoteResources(r chi.Router) {"}]},
    {"from": "api-http", "to": "svc-votings", "type": "calls", "evidence": [
        {"path": "server/src/api/votings.go", "symbol": "votings.Create", "match": "voting, err := s.votings.Create(r.Context(), body)"},
        {"path": "server/src/api/votings.go", "symbol": "votings.Update", "match": "voting, err := s.votings.Update(r.Context(), body)"},
        {"path": "server/src/api/router.go", "symbol": "initVotingResources", "match": "func (s *Server) initVotingResources(r chi.Router) {"}]},
    {"from": "api-http", "to": "svc-feedback", "type": "calls", "evidence": [
        {"path": "server/src/api/feedback.go", "symbol": "feedback.Create", "match": "err := s.feedback.Create(r.Context(), string(body.Type), *body.Contact, *body.Text)"},
        {"path": "server/src/api/router.go", "symbol": "POST /feedback", "match": "r.Post(\"/feedback\", s.createFeedback)"}]},
    {"from": "api-http", "to": "realtime", "type": "subscribes", "evidence": [
        {"path": "server/src/api/boards_listen_on_board.go", "symbol": "GetBoardChannel", "match": "b.subscription = s.realtime.GetBoardChannel(boardID)"}]},

    # services
    {"from": "svc-notes", "to": "database", "type": "writes", "evidence": [
        {"path": "server/src/services/notes/notes.go", "symbol": "CreateNote", "match": "note, err := s.database.CreateNote(database.NoteInsert{"}]},
    {"from": "svc-notes", "to": "database", "type": "reads", "evidence": [
        {"path": "server/src/services/notes/notes.go", "symbol": "GetNotes", "match": "notes, err := s.database.GetNotes(boardID)"}]},
    {"from": "svc-notes", "to": "realtime", "type": "publishes", "evidence": [
        {"path": "server/src/services/notes/notes.go", "symbol": "BroadcastToBoard", "match": "err := s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"}]},
    {"from": "svc-boards", "to": "database", "type": "writes", "evidence": [
        {"path": "server/src/services/boards/boards.go", "symbol": "CreateBoard", "match": "b, err := s.database.CreateBoard("}]},
    {"from": "svc-boards", "to": "realtime", "type": "publishes", "evidence": [
        {"path": "server/src/services/boards/boards.go", "symbol": "BroadcastToBoard", "match": "err := s.realtime.BroadcastToBoard(board.ID, realtime.BoardEvent{"}]},
    {"from": "svc-votings", "to": "realtime", "type": "publishes", "evidence": [
        {"path": "server/src/services/votings/votings.go", "symbol": "BroadcastToBoard", "match": "err = s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"}]},
    {"from": "svc-votings", "to": "database", "type": "writes", "evidence": [
        {"path": "server/src/services/votings/votings.go", "symbol": "CreateVoting", "match": "s.database.CreateVoting("}]},
    {"from": "svc-feedback", "to": "ext-feedback-webhook", "type": "calls", "evidence": [
        {"path": "server/src/services/feedback/feedback.go", "symbol": "http.Post", "match": "_, err := http.Post(s.webhookUrl, \"application/json\", bytes.NewBuffer(jsonData))"}]},

    # infrastructure
    {"from": "database", "to": "ext-postgres", "type": "reads", "evidence": [
        {"path": "server/src/database/boards.go", "symbol": "GetBoard", "match": "func (d *Database) GetBoard(id uuid.UUID) (Board, error) {"},
        {"path": "server/src/database/database.go", "symbol": "pgdialect", "match": "d.db = bun.NewDB(db, pgdialect.New())"}]},
    {"from": "database", "to": "ext-postgres", "type": "writes", "evidence": [
        {"path": "server/src/database/notes.go", "symbol": "CreateNote", "match": "func (d *Database) CreateNote(insert NoteInsert) (Note, error) {"}]},
    {"from": "migrations", "to": "ext-postgres", "type": "writes", "evidence": [
        {"path": "server/src/database/migrations/migrations.go", "symbol": "sql.Open", "match": "db, err := sql.Open(\"postgres\", databaseUrl)"}]},
    {"from": "realtime", "to": "ext-nats", "type": "publishes", "evidence": [
        {"path": "server/src/realtime/nats.go", "symbol": "natsClient.Publish", "match": "return n.con.Publish(subject, event)"}]},
    {"from": "realtime", "to": "ext-nats", "type": "subscribes", "evidence": [
        {"path": "server/src/realtime/nats.go", "symbol": "SubscribeToBoardEvents", "match": "func (n *natsClient) SubscribeToBoardEvents(subject string) (chan *BoardEvent, error) {"}]},
    {"from": "realtime", "to": "ext-redis", "type": "publishes", "evidence": [
        {"path": "server/src/realtime/redis.go", "symbol": "redisClient.Publish", "match": "_, err = r.con.Publish(context.Background(), subject, payload).Result()"}]},
    {"from": "realtime", "to": "ext-redis", "type": "subscribes", "evidence": [
        {"path": "server/src/realtime/redis.go", "symbol": "SubscribeToBoardEvents", "match": "func (r *redisClient) SubscribeToBoardEvents(subject string) (chan *BoardEvent, error) {"}]},
    {"from": "auth", "to": "ext-oauth", "type": "calls", "evidence": [
        {"path": "server/src/auth/auth.go", "symbol": "google.New", "match": "p := google.New("},
        {"path": "server/src/api/router.go", "symbol": "provider begin route", "match": "r.Get(\"/\", s.beginAuthProviderVerification)"}]},
    {"from": "auth", "to": "database", "type": "reads", "evidence": [
        {"path": "server/src/auth/auth.go", "symbol": "IsUserAvailableForKeyMigration", "match": "if ok, err = a.database.IsUserAvailableForKeyMigration(user); ok {"}]},

    # relationships asserted by the running system but not by any single source line
    {"from": "web-components", "to": "web-api", "type": "calls", "evidence": [
        {"path": "src/components/SettingsDialog/Feedback/Feedback.tsx", "symbol": "FeedbackAPI.sendFeedback", "match": "FeedbackAPI.sendFeedback(feedbackType.value, feedback.value.trim(), contact.value.trim());"},
        {"path": "src/components/Timer/Timer.tsx", "symbol": "import API", "match": "import {API} from \"api\";"}]},
    {"from": "web-routes", "to": "web-api", "type": "calls", "evidence": [
        {"path": "src/routes/NewBoard/NewBoard.tsx", "symbol": "API.createBoard", "match": "const boardId = await API.createBoard("},
        {"path": "src/utils/auth.ts", "symbol": "API.signInAnonymously", "match": "const user = await API.signInAnonymously(displayName);"}]},
]

# ---------------------------------------------------------------- flows ----

FLOWS = [
    {
        "id": "flow-anonymous-login",
        "name": "Anonymous sign-in",
        "trigger": "A visitor enters a display name on the landing page and continues without an account.",
        "steps": [
            {"node": "web-routes", "detail": "LoginBoard calls Auth.signInAnonymously (src/utils/auth.ts) - no store middleware is involved."},
            {"node": "web-api", "detail": "AuthAPI.signInAnonymously POSTs to /login/anonymous with credentials: \"include\"."},
            {"node": "api-http", "detail": "The public route /login/anonymous hits Server.signInAnonymously."},
            {"node": "database", "detail": "users.LoginAnonymous persists an anonymous user; this happens BEFORE the token is signed."},
            {"node": "ext-postgres", "detail": "The user record lands in PostgreSQL."},
            {"node": "auth", "detail": "auth.Sign issues a JWT for the new user id; the handler sets it as the HttpOnly 'jwt' cookie."},
            {"node": "web-store", "detail": "utils/auth.ts dispatches Actions.signIn with the returned user."},
        ],
        "outcome": "The browser holds a session cookie and every later request is authenticated by it. "
                   "Protected routes now pass auth.Verifier and jwtauth.Authenticator.",
        "evidence": [
            {"path": "src/routes/LoginBoard/LoginBoard.tsx", "symbol": "Auth.signInAnonymously", "match": "await Auth.signInAnonymously(displayName);"},
            {"path": "src/utils/auth.ts", "symbol": "API.signInAnonymously", "match": "const user = await API.signInAnonymously(displayName);"},
            {"path": "src/api/auth.ts", "symbol": "signInAnonymously", "match": "const response = await fetch(`${SERVER_HTTP_URL}/login/anonymous`, {"},
            {"path": "server/src/api/router.go", "symbol": "anonymous route", "match": "r.Post(\"/anonymous\", s.signInAnonymously)"},
            {"path": "server/src/api/login.go", "symbol": "users.LoginAnonymous", "match": "user, err := s.users.LoginAnonymous(r.Context(), body.Name)"},
            {"path": "server/src/api/login.go", "symbol": "auth.Sign", "match": "tokenString, err := s.auth.Sign(map[string]interface{}{\"id\": user.ID})"},
            {"path": "server/src/api/login.go", "symbol": "jwt cookie", "match": "cookie := http.Cookie{Name: \"jwt\", Value: tokenString, Path: \"/\", HttpOnly: true, MaxAge: math.MaxInt32}"},
        ],
    },
    {
        "id": "flow-join-board",
        "name": "Open a board and receive the initial state",
        "trigger": "An authenticated user navigates to /board/:boardId.",
        "steps": [
            {"node": "web-routes", "detail": "BoardGuard dispatches joinBoard(boardId)."},
            {"node": "web-store", "detail": "On PermittedBoardAccess the board middleware opens a sockette connection to SERVER_WEBSOCKET_URL/boards/<id>."},
            {"node": "api-http", "detail": "GET /boards/{id} upgrades to a websocket in openBoardSocket, guarded by BoardParticipantContext."},
            {"node": "svc-boards", "detail": "FullBoard assembles board, columns, notes, reactions, votings, votes, sessions and requests."},
            {"node": "database", "detail": "Database.Get loads every aggregate for the board."},
            {"node": "ext-postgres", "detail": "The rows come out of PostgreSQL."},
            {"node": "api-http", "detail": "eventInitFilter strips data the caller may not see, then the INIT event is written to the socket."},
            {"node": "web-store", "detail": "The onmessage handler dispatches Actions.initializeBoard with the INIT payload."},
            {"node": "web-components", "detail": "Board, columns and notes render from the hydrated store."},
        ],
        "outcome": "The client has the full board state and a live subscription for every later change.",
        "evidence": [
            {"path": "src/routes/Board/BoardGuard.tsx", "symbol": "joinBoard", "match": "store.dispatch(Actions.joinBoard(boardId!));"},
            {"path": "src/store/middleware/board.tsx", "symbol": "socket open", "match": "socket = new Socket(`${SERVER_WEBSOCKET_URL}/boards/${action.boardId}`, {"},
            {"path": "server/src/api/boards_listen_on_board.go", "symbol": "FullBoard", "match": "board, requests, sessions, columns, notes, reactions, votings, votes, err := s.boards.FullBoard(r.Context(), id)"},
            {"path": "server/src/api/boards_listen_on_board.go", "symbol": "eventInitFilter", "match": "initEvent = eventInitFilter(initEvent, userID)"},
            {"path": "src/store/middleware/board.tsx", "symbol": "INIT dispatch", "match": "store.dispatch(Actions.initializeBoard(board, participants, requests || [], columns, notes || [], reactions || [], votes || [], votings || []));"},
        ],
    },
    {
        "id": "flow-add-note",
        "name": "Add a note and fan it out to every participant",
        "trigger": "A participant types into a column and submits a note.",
        "steps": [
            {"node": "web-components", "detail": "NoteInput dispatches Actions.addNote(columnId, content)."},
            {"node": "web-store", "detail": "passNoteMiddleware calls API.addNote with the board id from the action context."},
            {"node": "web-api", "detail": "NoteAPI.addNote POSTs to /boards/{boardId}/notes."},
            {"node": "api-http", "detail": "The note routes run BoardParticipantContext, then Server.createNote."},
            {"node": "svc-notes", "detail": "NoteService.Create writes the note, then calls UpdatedNotes."},
            {"node": "database", "detail": "Database.CreateNote inserts the row."},
            {"node": "ext-postgres", "detail": "The note is persisted."},
            {"node": "svc-notes", "detail": "UpdatedNotes broadcasts a NOTES_UPDATED BoardEvent."},
            {"node": "realtime", "detail": "Broker.BroadcastToBoard publishes on topic board.<uuid>."},
            {"node": "ext-nats", "detail": "NATS (or Redis when configured) fans the event out to every server instance."},
            {"node": "api-http", "detail": "Each instance's board subscription receives the event and writes it to its websockets."},
            {"node": "web-store", "detail": "The onmessage handler dispatches Actions.updatedNotes."},
            {"node": "web-components", "detail": "Every participant's board re-renders with the new note."},
        ],
        "outcome": "The note is durable in PostgreSQL and visible to every connected participant without a refresh.",
        "evidence": [
            {"path": "src/components/NoteInput/NoteInput.tsx", "symbol": "addNote", "match": "dispatch(Actions.addNote(columnId!, content));"},
            {"path": "src/store/middleware/note.tsx", "symbol": "API.addNote", "match": "API.addNote(action.context.board!, action.columnId, action.text)"},
            {"path": "src/api/note.ts", "symbol": "POST notes", "match": "const response = await fetch(`${SERVER_HTTP_URL}/boards/${boardId}/notes`, {"},
            {"path": "server/src/api/notes.go", "symbol": "createNote", "match": "func (s *Server) createNote(w http.ResponseWriter, r *http.Request) {"},
            {"path": "server/src/services/notes/notes.go", "symbol": "CreateNote", "match": "note, err := s.database.CreateNote(database.NoteInsert{"},
            {"path": "server/src/services/notes/notes.go", "symbol": "broadcast", "match": "err := s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"},
            {"path": "server/src/realtime/boards.go", "symbol": "BroadcastToBoard", "match": "func (b *Broker) BroadcastToBoard(boardID uuid.UUID, msg BoardEvent) error {"},
            {"path": "src/store/middleware/board.tsx", "symbol": "NOTES_UPDATED", "match": "if (message.type === \"NOTES_UPDATED\") {"},
        ],
    },
    {
        "id": "flow-create-board",
        "name": "Create a new board",
        "trigger": "A user configures columns and an access policy on /new and submits.",
        "steps": [
            {"node": "web-routes", "detail": "The /new route renders NewBoard behind RequireAuthentication."},
            {"node": "web-components", "detail": "The template picker and AccessPolicySelection collect name, policy and columns."},
            {"node": "web-api", "detail": "NewBoard.tsx calls API.createBoard directly (no store middleware); it POSTs to /boards and returns the new board id."},
            {"node": "api-http", "detail": "Server.createBoard runs behind the JWT middleware stack."},
            {"node": "svc-boards", "detail": "BoardService.Create persists the board plus its columns and the creator's owner session."},
            {"node": "database", "detail": "Database.CreateBoard composes the board, column and owner-session inserts into a single CTE query."},
            {"node": "ext-postgres", "detail": "The board is stored."},
            {"node": "web-routes", "detail": "The browser navigates to /board/<new id>, which starts the join-board flow."},
        ],
        "outcome": "A board exists with its columns, the creator is its owner, and the user lands on the live board.",
        "evidence": [
            {"path": "src/routes/NewBoard/NewBoard.tsx", "symbol": "API.createBoard", "match": "const boardId = await API.createBoard("},
            {"path": "src/api/board.ts", "symbol": "createBoard", "match": "createBoard: async (name: string | undefined, accessPolicy: {type: string; passphrase?: string}, columns: {name: string; hidden: boolean; color: Color}[]) => {"},
            {"path": "server/src/api/router.go", "symbol": "POST /boards", "match": "r.Post(\"/boards\", s.createBoard)"},
            {"path": "server/src/api/boards.go", "symbol": "createBoard", "match": "b, err := s.boards.Create(r.Context(), body)"},
            {"path": "server/src/database/boards.go", "symbol": "CreateBoard", "match": "func (d *Database) CreateBoard(creator uuid.UUID, board BoardInsert, columns []ColumnInsert) (Board, error) {"},
        ],
    },
    {
        "id": "flow-voting",
        "name": "Run a voting session",
        "trigger": "A moderator opens a voting from the voting dialog.",
        "steps": [
            {"node": "web-components", "detail": "VotingDialog dispatches the create-voting action."},
            {"node": "web-store", "detail": "passVotingMiddleware calls the votings REST client."},
            {"node": "web-api", "detail": "VotingAPI posts to /boards/{id}/votings."},
            {"node": "api-http", "detail": "initVotingResources guards create/update with BoardModeratorContext."},
            {"node": "svc-votings", "detail": "VotingService creates the voting and broadcasts VOTING_CREATED."},
            {"node": "database", "detail": "The voting row is written; votes are later counted in SQL."},
            {"node": "ext-postgres", "detail": "Voting and vote rows are persisted."},
            {"node": "realtime", "detail": "The voting events are published on the board topic."},
            {"node": "api-http", "detail": "eventFilter hides vote counts from participants while the voting is open."},
            {"node": "web-store", "detail": "Clients dispatch the voting updates into the votings reducer."},
            {"node": "web-components", "detail": "Vote buttons appear; results render once the voting closes."},
        ],
        "outcome": "Participants cast votes under the configured limit, and totals become visible only after the moderator closes the voting.",
        "evidence": [
            {"path": "server/src/api/router.go", "symbol": "initVotingResources", "match": "func (s *Server) initVotingResources(r chi.Router) {"},
            {"path": "server/src/api/router.go", "symbol": "moderator guard", "match": "r.With(s.BoardModeratorContext).Post(\"/\", s.createVoting)"},
            {"path": "server/src/services/votings/votings.go", "symbol": "broadcast", "match": "err = s.realtime.BroadcastToBoard(board, realtime.BoardEvent{"},
            {"path": "server/src/api/event_filter.go", "symbol": "filterVotingUpdated", "match": "func filterVotingUpdated(voting *VotingUpdated, userID uuid.UUID, boardSettings *dto.Board, columns []*dto.Column) *VotingUpdated {"},
            {"path": "src/store/middleware/board.tsx", "symbol": "VOTING_UPDATED", "match": "if (message.type === \"VOTING_UPDATED\") {"},
        ],
    },
    {
        "id": "flow-feedback",
        "name": "Submit feedback to the external webhook",
        "trigger": "A user fills in the feedback form in the settings dialog.",
        "steps": [
            {"node": "web-components", "detail": "The Feedback settings panel posts the form."},
            {"node": "web-api", "detail": "Feedback.tsx imports FeedbackAPI from api/feedback directly and posts to the public /feedback endpoint. Note api/feedback is NOT merged into the shared API object in api/index.ts."},
            {"node": "api-http", "detail": "Server.createFeedback handles it - no authentication required."},
            {"node": "svc-feedback", "detail": "FeedbackService.Create builds a Slack block payload and posts it."},
            {"node": "ext-feedback-webhook", "detail": "The external webhook receives the message."},
        ],
        "outcome": "Feedback reaches the team's chat channel. If --feedback-webhook-url is unset the feature is disabled and the form is hidden.",
        "evidence": [
            {"path": "src/components/SettingsDialog/Feedback/Feedback.tsx", "symbol": "FeedbackAPI.sendFeedback", "match": "FeedbackAPI.sendFeedback(feedbackType.value, feedback.value.trim(), contact.value.trim());"},
            {"path": "server/src/api/router.go", "symbol": "POST /feedback", "match": "r.Post(\"/feedback\", s.createFeedback)"},
            {"path": "server/src/api/feedback.go", "symbol": "feedback.Create", "match": "err := s.feedback.Create(r.Context(), string(body.Type), *body.Contact, *body.Text)"},
            {"path": "server/src/api/info.go", "symbol": "feedbackEnabled", "match": "if s.feedback.Enabled() {"},
            {"path": "server/src/services/feedback/feedback.go", "symbol": "http.Post", "match": "_, err := http.Post(s.webhookUrl, \"application/json\", bytes.NewBuffer(jsonData))"},
            {"path": "src/components/SettingsDialog/Feedback/__tests__/Feedback.test.tsx", "symbol": "describe(Feedback)", "match": "describe(\"Feedback\", () => {"},
        ],
    },
]
