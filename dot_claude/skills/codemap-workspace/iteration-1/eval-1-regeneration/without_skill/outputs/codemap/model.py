"""Hand-curated code map model for the Aerie repo.

Every node, edge and flow step here was read out of the working tree. `generate.py`
re-verifies each `evidence` entry against the file it names before writing anything,
so a symbol that moves or disappears fails the build instead of rotting silently.

Edge `type` is closed to the six values the spec allows. A relationship we cannot
point at a source line for carries `"evidence": "unknown"` — never a made-up symbol
and never an invented type.
"""

# --- module fingerprint scope -------------------------------------------------
# One entry per internal node. `include` / `exclude` are path prefixes matched
# against `git ls-files` output. Externals and datastores have no source and are
# absent here.
MODULES = {
    "client-v1": {"include": ["client/src/"], "exclude": [], "tests": ["client/tests/"]},
    "client-v2": {"include": ["client-v2/src/"], "exclude": [], "tests": ["client-v2/tests/"]},
    "shared-ts": {"include": ["shared/src/", "packages/ui/src/"], "exclude": []},
    "api-core": {"include": ["server/aerie/core/"], "exclude": []},
    "api-surveys": {
        "include": ["server/aerie/surveys/"],
        "exclude": ["server/aerie/surveys/services/"],
    },
    "surveys-services": {
        "include": ["server/aerie/surveys/services/"],
        "exclude": [],
        "tests": ["server/aerie/surveys/tests/"],
        "tests_match": [
            "switchbird",
            "firsthx",
            "dropbox_sign",
            "ingestion",
            "notification_delivery",
            "signature_service",
            "phase_schedule",
            "assessment_schedule",
        ],
    },
    "api-medications": {"include": ["server/aerie/medications/"], "exclude": []},
    "api-chat": {"include": ["server/aerie/chat/"], "exclude": []},
    "ops-tooling": {"include": ["server/aerie/ops/", "server/aerie/seeds/"], "exclude": []},
    "platform": {
        "include": [
            "server/aerie/common/",
            "server/aerie/utils/",
            "server/aerie/db/",
            "server/aerie/settings/",
            "server/aerie/urls.py",
            "server/aerie/routing.py",
            "server/aerie/asgi.py",
            "server/aerie/conftest.py",
        ],
        "exclude": ["server/aerie/common/background_tasks.py"],
    },
    "task-queue": {
        "include": ["server/aerie/common/background_tasks.py"],
        "exclude": [],
        "tests": ["server/aerie/common/tests/", "server/aerie/surveys/tests/"],
        "tests_match": ["background", "task", "auto_start", "start_once"],
    },
}

SCOPE = [
    "client/src",
    "client-v2/src",
    "shared/src",
    "packages/ui/src",
    "server/aerie",
]

EXCLUDED_DIRS = [
    ".claude/worktrees",
    ".venv",
    "__pycache__",
    "client-v2/node_modules",
    "client/node_modules",
    "dist",
    "docs/_build",
    "graphify-out",
    "infra",
    "node_modules",
    "observations",
    "server/aerie/*/migrations",
    "specs",
    "static",
]

# --- nodes --------------------------------------------------------------------
# role drives the legend colour. Roles: client, api, service, queue, datastore, external.
NODES = [
    {
        "id": "client-v1",
        "path": "client/src",
        "role": "client",
        "title": "Client v1 (React SPA)",
        "summary": "Shipping clinician portal. TanStack Query over tn-models service modules.",
        "entrypoints": [
            {"path": "client/src/main.tsx", "symbol": "createRoot"},
            {"path": "client/src/app.tsx", "symbol": "App"},
        ],
        "constraints": [
            "axiosInstance pre-pends /api — a service baseUri must not repeat it.",
            "Server state lives in TanStack Query; Zustand holds UI state only.",
        ],
        "evidence": {"path": "client/src/services/axios-instance.ts", "symbol": "axiosInstance"},
    },
    {
        "id": "client-v2",
        "path": "client-v2/src",
        "role": "client",
        "title": "Client v2 (React SPA)",
        "summary": "Work-in-progress replacement UI. Ships alongside v1; owns the medication-reminder screens.",
        "entrypoints": [
            {"path": "client-v2/src/main.tsx", "symbol": "createRoot"},
            {"path": "client-v2/src/app.tsx", "symbol": "App"},
        ],
        "constraints": [
            "Deployed builds set VITE_BACKEND_URL; local dev relies on the Vite proxy at same-origin /api.",
            "Only client-v2 consumes @aerie/shared and @aerie/ui.",
        ],
        "evidence": {"path": "client-v2/src/services/axios-instance.ts", "symbol": "axiosInstance"},
    },
    {
        "id": "shared-ts",
        "path": "shared/src",
        "role": "client",
        "title": "Shared TS packages",
        "summary": "@aerie/shared API models plus the @aerie/ui Tailwind preset, built with tsup and consumed by client-v2.",
        "entrypoints": [
            {"path": "shared/src/index.ts", "symbol": "export"},
            {"path": "packages/ui/src/preset.ts", "symbol": "preset"},
        ],
        "constraints": [
            "npm workspace packages — must be built (tsup) before client-v2 can resolve dist/.",
        ],
        "evidence": {"path": "shared/package.json", "symbol": "@aerie/shared"},
    },
    {
        "id": "api-core",
        "path": "server/aerie/core",
        "role": "api",
        "title": "core (identity + RBAC)",
        "summary": "User, Organization, Clinic, UserClinicMembership, token auth, permissions, admin.",
        "entrypoints": [
            {"path": "server/aerie/core/urls.py", "symbol": "urlpatterns"},
            {"path": "server/aerie/core/views.py", "symbol": "UserViewSet"},
            {"path": "server/aerie/core/authentication.py", "symbol": "ExpiringTokenAuthentication"},
        ],
        "constraints": [
            "AUTH_USER_MODEL = core.User; email is the username field.",
            "core/common URLs are included last so they cannot shadow other apps.",
            "Non-staff querysets must be filtered by User.get_clinics().",
        ],
        "evidence": {"path": "server/aerie/core/models.py", "symbol": "class User"},
    },
    {
        "id": "api-surveys",
        "path": "server/aerie/surveys",
        "role": "api",
        "title": "surveys (patients, studies, notifications)",
        "summary": "Largest app: Patient, Study, Survey, NotificationInstance, consent + signature flows, dashboard.",
        "entrypoints": [
            {"path": "server/aerie/surveys/urls.py", "symbol": "urlpatterns"},
            {"path": "server/aerie/surveys/views.py", "symbol": "PatientViewSet"},
            {"path": "server/aerie/surveys/views.py", "symbol": "dropbox_sign_webhook"},
            {"path": "server/aerie/surveys/tasks.py", "symbol": "sync_switchbird_surveys_continuous"},
        ],
        "constraints": [
            "Assessment in the UI is Survey in code and in the vendor API (glossary divergence).",
            "PHI-touching viewsets mix in PHIAuditMixin.",
            "Deletes are soft (is_active=False).",
        ],
        "evidence": {"path": "server/aerie/surveys/apps.py", "symbol": "class SurveysConfig"},
    },
    {
        "id": "surveys-services",
        "path": "server/aerie/surveys/services",
        "role": "service",
        "title": "surveys services (vendor doors)",
        "summary": "Single door per external vendor plus notification delivery, scheduling and caches.",
        "entrypoints": [
            {"path": "server/aerie/surveys/services/switchbird.py", "symbol": "get_switchbird_service"},
            {"path": "server/aerie/surveys/services/firsthx.py", "symbol": "class FirstHxService"},
            {"path": "server/aerie/surveys/services/dropbox_sign.py", "symbol": "class DropboxSignService"},
            {"path": "server/aerie/surveys/services/survey_ingestion.py", "symbol": "class SurveyIngestionService"},
        ],
        "constraints": [
            "Never construct SwitchBirdService directly — use get_switchbird_service() (ruff TID251).",
            "A SwitchBird calendar event that is not scheduled must never be written.",
            "Credentials and PHI must not be logged.",
        ],
        "evidence": {"path": "server/aerie/surveys/services/switchbird.py", "symbol": "class SwitchBirdService"},
    },
    {
        "id": "api-medications",
        "path": "server/aerie/medications",
        "role": "api",
        "title": "medications (reminders + RTM)",
        "summary": "MedicationSchedule, dose generation, missed-dose sweeps, RTM billing summaries, drug search.",
        "entrypoints": [
            {"path": "server/aerie/medications/urls.py", "symbol": "urlpatterns"},
            {"path": "server/aerie/medications/views.py", "symbol": "MedicationScheduleViewSet"},
            {"path": "server/aerie/medications/tasks.py", "symbol": "sync_med_reminder_messages_continuous"},
        ],
        "constraints": [
            "Medication-reminder rules are admin-authored; seeds must not create them.",
            "Reminder enrolment resolves the inbox per clinic (Clinic.med_reminder_inbox_id).",
        ],
        "evidence": {"path": "server/aerie/medications/apps.py", "symbol": "class MedicationsConfig"},
    },
    {
        "id": "api-chat",
        "path": "server/aerie/chat",
        "role": "api",
        "title": "chat (WebSocket assistant)",
        "summary": "Channels consumer that authenticates over the socket and streams OpenAI completions.",
        "entrypoints": [
            {"path": "server/aerie/chat/consumers.py", "symbol": "class ChatConsumer"},
            {"path": "server/aerie/chat/urls.py", "symbol": "get_current_system_prompt"},
        ],
        "constraints": [
            "Auth token arrives in the first socket message, never in the URL.",
        ],
        "evidence": {"path": "server/aerie/routing.py", "symbol": "websocket_urlpatterns"},
    },
    {
        "id": "ops-tooling",
        "path": "server/aerie/ops",
        "role": "service",
        "title": "ops + seeds (staff tooling)",
        "summary": "Token-gated /_ops/* SQL, logs, settings and command runner, plus the seed/demo command tree.",
        "entrypoints": [
            {"path": "server/aerie/ops/urls.py", "symbol": "urlpatterns"},
            {"path": "server/aerie/ops/views/sql.py", "symbol": "OpsSqlView"},
            {"path": "server/aerie/seeds/management/commands/seed_test.py", "symbol": "Command"},
        ],
        "constraints": [
            "aerie.ops is in INSTALLED_APPS on dev/staging only — prod stays clean.",
            "urls.py gates the ops include on apps.is_installed; importing its views unguarded crashes boot.",
        ],
        "evidence": {"path": "server/aerie/urls.py", "symbol": "apps.is_installed(\"aerie.ops\")"},
    },
    {
        "id": "platform",
        "path": "server/aerie/common",
        "role": "service",
        "title": "platform (common, utils, db, settings)",
        "summary": "AbstractBaseModel, URL/ASGI wiring, settings, storages and the email backends.",
        "entrypoints": [
            {"path": "server/aerie/urls.py", "symbol": "urlpatterns"},
            {"path": "server/aerie/asgi.py", "symbol": "application"},
            {"path": "server/aerie/common/urls.py", "symbol": "health_check"},
        ],
        "constraints": [
            "IN_PROD is computed at import time — override_settings cannot move it.",
            "Deployed environments force sslmode=require on the default connection.",
            "Application-level field encryption is not permitted; encryption is database-native.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "INSTALLED_APPS"},
    },
    {
        "id": "task-queue",
        "path": "server/aerie/common/background_tasks.py",
        "role": "queue",
        "title": "background_task queue",
        "summary": "django4-background-tasks (not Celery). Rows live in Postgres; apps self-schedule repeating tasks from ready().",
        "entrypoints": [
            {"path": "server/aerie/common/background_tasks.py", "symbol": "start_once"},
        ],
        "constraints": [
            "Auto-start is env-gated (AUTO_START_SWITCHBIRD_SYNC, AUTO_START_MED_REMINDER_TASKS, ...).",
            "start_once takes a pg advisory lock so parallel containers cannot double-schedule.",
            "The background_task table is shared across lanes sharing a dev DB.",
        ],
        "evidence": {"path": "server/aerie/common/background_tasks.py", "symbol": "pg_advisory_xact_lock"},
    },
    {
        "id": "postgres",
        "path": "server/aerie/settings/base.py",
        "role": "datastore",
        "title": "PostgreSQL (RDS)",
        "summary": "Primary store for every model plus the background_task queue. Optional read-only alias for staging debug.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "DATABASES"}],
        "constraints": [
            "Bounded libpq timeouts: connect_timeout=2, statement_timeout=2000.",
            "default_readonly alias exists only when DB_READONLY_USER/PASSWORD are set.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "DATABASES"},
    },
    {
        "id": "redis",
        "path": "server/aerie/settings/base.py",
        "role": "datastore",
        "title": "Redis (channel layer)",
        "summary": "Backs CHANNEL_LAYERS for the chat WebSocket group fan-out.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "CHANNEL_LAYERS"}],
        "constraints": [
            "RedisChannelLayer only — no cache or queue duties.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "channels_redis.core.RedisChannelLayer"},
    },
    {
        "id": "ext-switchbird",
        "path": "server/aerie/surveys/services/switchbird.py",
        "role": "external",
        "title": "SwitchBird API",
        "summary": "SMS surveys and calendar-event scheduling. The busiest integration.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "SWITCHBIRD_API_BASE_URL"}],
        "constraints": [
            "Vendor truncates long message bodies — abort before rule evaluation.",
            "Surveys are single-threaded per contact; `stopped` is terminal.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "SWITCHBIRD_API_BASE_URL"},
    },
    {
        "id": "ext-firsthx",
        "path": "server/aerie/surveys/services/firsthx.py",
        "role": "external",
        "title": "FirstHx API",
        "summary": "Patient intake interviews. Blank intake is created server-side; the report is pulled back.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "FIRSTHX_API_BASE_URL"}],
        "constraints": [
            "Intake is rendered in an iframe from FIRSTHX_INTAKE_URL; CSP frame-src must allow it.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "FIRSTHX_API_BASE_URL"},
    },
    {
        "id": "ext-dropbox-sign",
        "path": "server/aerie/surveys/services/dropbox_sign.py",
        "role": "external",
        "title": "Dropbox Sign API",
        "summary": "E-consent signature requests; status changes arrive back on a webhook.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "DROPBOX_SIGN_API_BASE_URL"}],
        "constraints": [
            "Gated by USE_DROPBOX_SIGN; test mode is on everywhere but prod.",
            "Callback URL must exactly match the configured Amplify domain.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "DROPBOX_SIGN_API_BASE_URL"},
    },
    {
        "id": "ext-openai",
        "path": "server/aerie/chat/consumers.py",
        "role": "external",
        "title": "OpenAI API",
        "summary": "Streaming chat completions for the in-app assistant.",
        "entrypoints": [{"path": "server/aerie/settings/base.py", "symbol": "OPENAI_API_KEY"}],
        "constraints": [
            "Called from async consumer code via AsyncOpenAI.",
        ],
        "evidence": {"path": "server/aerie/chat/consumers.py", "symbol": "AsyncOpenAI"},
    },
    {
        "id": "ext-rxnav",
        "path": "server/aerie/medications/services/rxnav.py",
        "role": "external",
        "title": "NIH RxNav API",
        "summary": "Drug-name search proxied through the medications app; replaced a bulk RRF sync.",
        "entrypoints": [{"path": "server/aerie/medications/services/rxnav.py", "symbol": "RXNAV_BASE_URL"}],
        "constraints": [
            "Per-request timeout 5s with an 8s overall fan-out budget; partial results are returned on exhaustion.",
            "Only SBD/SCD (prescribable) concepts are kept.",
        ],
        "evidence": {"path": "server/aerie/medications/services/rxnav.py", "symbol": "RXNAV_BASE_URL"},
    },
    {
        "id": "ext-s3",
        "path": "server/aerie/utils/storages.py",
        "role": "external",
        "title": "AWS S3 (private media)",
        "summary": "Consent PDFs and uploads behind presigned URLs, optionally per-organization KMS keys.",
        "entrypoints": [{"path": "server/aerie/utils/storages.py", "symbol": "class PrivateMediaStorage"}],
        "constraints": [
            "SigV4 is explicit — the buckets are SSE-KMS and S3 serves those only over SigV4.",
            "Presigned URLs expire after one hour.",
        ],
        "evidence": {"path": "server/aerie/utils/storages.py", "symbol": "S3Boto3Storage"},
    },
    {
        "id": "ext-email",
        "path": "server/aerie/utils/ses_backend.py",
        "role": "external",
        "title": "Email (SES / Mailgun)",
        "summary": "Anymail backends; staging assumes the prod SES role. Bounces and complaints feed a suppression list.",
        "entrypoints": [
            {"path": "server/aerie/utils/ses_backend.py", "symbol": "AssumeRoleSESBackend"},
            {"path": "server/aerie/core/signals.py", "symbol": "handle_ses_tracking_event"},
        ],
        "constraints": [
            "Provider is chosen at import time by ENABLE_EMAILS + EMAIL_PROVIDER.",
            "Anymail 8.4 does not verify SNS signatures — the webhook relies on HTTP Basic auth.",
        ],
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "EMAIL_BACKEND"},
    },
]

# --- edges --------------------------------------------------------------------
# type ∈ {imports, calls, reads, writes, publishes, subscribes}
EDGES = [
    # clients → API
    {
        "from": "client-v1",
        "to": "api-surveys",
        "type": "calls",
        "evidence": {"path": "client/src/services/patient/api.ts", "symbol": "axiosInstance"},
    },
    {
        "from": "client-v1",
        "to": "api-core",
        "type": "calls",
        "evidence": {"path": "client/src/services/user/api.ts", "symbol": "axiosInstance"},
    },
    {
        "from": "client-v1",
        "to": "api-chat",
        "type": "calls",
        "evidence": {"path": "client/src/components/chat-interface.tsx", "symbol": "WebSocket"},
    },
    {
        "from": "client-v2",
        "to": "api-medications",
        "type": "calls",
        "evidence": {
            "path": "client-v2/src/services/medication-schedule/api.ts",
            "symbol": "searchDrugsCall",
        },
    },
    {
        "from": "client-v2",
        "to": "api-core",
        "type": "calls",
        "evidence": {"path": "client-v2/src/services/user/api.ts", "symbol": "axiosInstance"},
    },
    {
        "from": "client-v2",
        "to": "api-chat",
        "type": "calls",
        "evidence": {"path": "client-v2/src/components/chat-interface.tsx", "symbol": "WebSocket"},
    },
    {
        "from": "client-v2",
        "to": "shared-ts",
        "type": "imports",
        "evidence": {"path": "client-v2/package.json", "symbol": "@aerie/shared"},
    },
    # URL wiring
    {
        "from": "platform",
        "to": "api-surveys",
        "type": "imports",
        "evidence": {"path": "server/aerie/urls.py", "symbol": "aerie.surveys.urls"},
    },
    {
        "from": "platform",
        "to": "api-medications",
        "type": "imports",
        "evidence": {"path": "server/aerie/urls.py", "symbol": "aerie.medications.urls"},
    },
    {
        "from": "platform",
        "to": "api-core",
        "type": "imports",
        "evidence": {"path": "server/aerie/urls.py", "symbol": "aerie.core.urls"},
    },
    {
        "from": "platform",
        "to": "api-chat",
        "type": "imports",
        "evidence": {"path": "server/aerie/routing.py", "symbol": "ChatConsumer"},
    },
    {
        "from": "platform",
        "to": "ops-tooling",
        "type": "imports",
        "evidence": {"path": "server/aerie/urls.py", "symbol": "aerie.ops.urls"},
    },
    # apps → platform base model / auth
    {
        "from": "api-surveys",
        "to": "platform",
        "type": "imports",
        "evidence": {"path": "server/aerie/surveys/models.py", "symbol": "AbstractBaseModel"},
    },
    {
        "from": "api-medications",
        "to": "platform",
        "type": "imports",
        "evidence": {"path": "server/aerie/medications/models.py", "symbol": "AbstractBaseModel"},
    },
    {
        "from": "api-surveys",
        "to": "api-core",
        "type": "imports",
        "evidence": {
            "path": "server/aerie/surveys/admin_displays.py",
            "symbol": "from aerie.core.models import UserClinicMembership",
        },
    },
    {
        "from": "api-medications",
        "to": "api-surveys",
        "type": "imports",
        "evidence": {
            "path": "server/aerie/medications/rtm_summaries.py",
            "symbol": "from aerie.surveys.models import",
        },
    },
    {
        "from": "api-chat",
        "to": "api-core",
        "type": "imports",
        "evidence": {"path": "server/aerie/chat/middleware.py", "symbol": "Token"},
    },
    # apps → services
    {
        "from": "api-surveys",
        "to": "surveys-services",
        "type": "calls",
        "evidence": {"path": "server/aerie/surveys/helpers.py", "symbol": "get_switchbird_service"},
    },
    {
        "from": "api-medications",
        "to": "surveys-services",
        "type": "calls",
        "evidence": {"path": "server/aerie/medications/tasks.py", "symbol": "get_switchbird_service"},
    },
    {
        "from": "ops-tooling",
        "to": "surveys-services",
        "type": "calls",
        "evidence": {"path": "server/aerie/ops/services/phone_reset.py", "symbol": "get_switchbird_service"},
    },
    # services → externals
    {
        "from": "surveys-services",
        "to": "ext-switchbird",
        "type": "calls",
        "evidence": {"path": "server/aerie/surveys/services/switchbird.py", "symbol": "self.api_base_url"},
    },
    {
        "from": "surveys-services",
        "to": "ext-firsthx",
        "type": "calls",
        "evidence": {"path": "server/aerie/surveys/services/firsthx.py", "symbol": "retrieve_report"},
    },
    {
        "from": "surveys-services",
        "to": "ext-dropbox-sign",
        "type": "calls",
        "evidence": {"path": "server/aerie/surveys/services/dropbox_sign.py", "symbol": "class DropboxSignService"},
    },
    {
        "from": "api-chat",
        "to": "ext-openai",
        "type": "calls",
        "evidence": {"path": "server/aerie/chat/consumers.py", "symbol": "handle_streaming_chat"},
    },
    {
        "from": "api-medications",
        "to": "ext-rxnav",
        "type": "calls",
        "evidence": {"path": "server/aerie/medications/services/rxnav.py", "symbol": "search_drugs"},
    },
    {
        "from": "platform",
        "to": "ext-s3",
        "type": "writes",
        "evidence": {"path": "server/aerie/utils/storages.py", "symbol": "class PrivateMediaStorage"},
    },
    {
        "from": "platform",
        "to": "ext-email",
        "type": "calls",
        "evidence": {"path": "server/aerie/utils/ses_backend.py", "symbol": "AssumeRoleSESBackend"},
    },
    {
        "from": "api-core",
        "to": "ext-email",
        "type": "subscribes",
        "evidence": {"path": "server/aerie/core/apps.py", "symbol": "tracking.connect"},
    },
    # inbound webhooks
    {
        "from": "ext-dropbox-sign",
        "to": "api-surveys",
        "type": "publishes",
        "evidence": {"path": "server/aerie/surveys/urls.py", "symbol": "dropbox-sign/webhook/"},
    },
    # datastores
    {
        "from": "api-core",
        "to": "postgres",
        "type": "writes",
        "evidence": {"path": "server/aerie/core/models.py", "symbol": "class User"},
    },
    {
        "from": "api-surveys",
        "to": "postgres",
        "type": "writes",
        "evidence": {"path": "server/aerie/surveys/models.py", "symbol": "class Survey"},
    },
    {
        "from": "api-medications",
        "to": "postgres",
        "type": "writes",
        "evidence": {"path": "server/aerie/medications/models.py", "symbol": "class MedicationSchedule"},
    },
    {
        "from": "ops-tooling",
        "to": "postgres",
        "type": "reads",
        "evidence": {"path": "server/aerie/ops/views/sql.py", "symbol": "connections"},
    },
    {
        "from": "task-queue",
        "to": "postgres",
        "type": "writes",
        "evidence": {"path": "server/aerie/common/background_tasks.py", "symbol": "Task.objects.filter"},
    },
    {
        "from": "api-chat",
        "to": "redis",
        "type": "publishes",
        "evidence": {"path": "server/aerie/chat/consumers.py", "symbol": "channel_layer.group_add"},
    },
    {
        "from": "platform",
        "to": "redis",
        "type": "reads",
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "CHANNEL_LAYERS"},
    },
    {
        "from": "platform",
        "to": "postgres",
        "type": "reads",
        "evidence": {"path": "server/aerie/settings/base.py", "symbol": "dj_database_url.config"},
    },
    # queue wiring
    {
        "from": "api-surveys",
        "to": "task-queue",
        "type": "publishes",
        "evidence": {"path": "server/aerie/surveys/apps.py", "symbol": "start_once"},
    },
    {
        "from": "api-medications",
        "to": "task-queue",
        "type": "publishes",
        "evidence": {"path": "server/aerie/medications/apps.py", "symbol": "start_once"},
    },
    {
        "from": "task-queue",
        "to": "api-surveys",
        "type": "calls",
        "evidence": {"path": "server/aerie/surveys/tasks.py", "symbol": "@background"},
    },
    {
        "from": "task-queue",
        "to": "api-medications",
        "type": "calls",
        "evidence": {"path": "server/aerie/medications/tasks.py", "symbol": "@background"},
    },
    # seeds/ops touching domain data
    {
        "from": "ops-tooling",
        "to": "api-surveys",
        "type": "imports",
        "evidence": {"path": "server/aerie/seeds/_common.py", "symbol": "from aerie.surveys.models import"},
    },
    # The intake interview renders straight from the vendor origin in the browser,
    # so this hop does not pass through the Aerie API at all.
    {
        "from": "client-v1",
        "to": "ext-firsthx",
        "type": "reads",
        "evidence": {
            "path": "client/src/components/firsthx-iframe.tsx",
            "symbol": "https://intake.firsthx.com",
        },
    },
]

# --- flows --------------------------------------------------------------------
FLOWS = [
    {
        "id": "flow-switchbird-survey",
        "name": "SwitchBird SMS assessment round-trip",
        "trigger": "The self-scheduling background task sync_switchbird_surveys_continuous fires (every 60s when AUTO_START_SWITCHBIRD_SYNC=true).",
        "steps": [
            {"node": "task-queue", "detail": "start_once schedules the repeating sync under a pg advisory lock."},
            {"node": "api-surveys", "detail": "tasks.sync_switchbird_surveys_continuous walks Organizations with a switchbird_inbox_id."},
            {"node": "surveys-services", "detail": "SwitchBirdSyncService pages the vendor via get_switchbird_service()."},
            {"node": "ext-switchbird", "detail": "SwitchBird returns survey runs and message bodies for the inbox."},
            {"node": "surveys-services", "detail": "SurveyIngestionService normalizes the payload into Survey fields."},
            {"node": "postgres", "detail": "Survey rows are created or updated."},
            {"node": "api-surveys", "detail": "PatientViewSet dashboard action aggregates the rows per study."},
            {"node": "client-v1", "detail": "The dashboard page renders the assessment results."},
        ],
        "outcome": "Patient SMS assessment responses land as Survey rows and surface on the clinician dashboard.",
    },
    {
        "id": "flow-econsent",
        "name": "E-consent signature",
        "trigger": "A staff user creates a SignatureRequest, or a survey completion schedules trigger_signature_request.",
        "steps": [
            {"node": "client-v1", "detail": "Signature request is created from the study console."},
            {"node": "api-surveys", "detail": "SignatureRequestViewSet validates and persists the request."},
            {"node": "surveys-services", "detail": "DropboxSignService sends the signature request to the vendor."},
            {"node": "ext-dropbox-sign", "detail": "Vendor emails the signer and hosts the signing page."},
            {"node": "api-surveys", "detail": "dropbox_sign_webhook verifies the event and routes it."},
            {"node": "postgres", "detail": "SignatureRequest / PendingConsent status is advanced."},
            {"node": "ext-s3", "detail": "The executed consent PDF is stored under PrivateMediaStorage."},
        ],
        "outcome": "A countersigned consent document is on file and the patient's consent status is current.",
    },
    {
        "id": "flow-firsthx-intake",
        "name": "FirstHx intake capture",
        "trigger": "A patient intake is started for a study configured with a FirstHx intake plan.",
        "steps": [
            {"node": "api-surveys", "detail": "Survey/patient views call into the FirstHx door."},
            {"node": "surveys-services", "detail": "FirstHxService.create_blank_intake provisions the interview."},
            {"node": "ext-firsthx", "detail": "FirstHx hosts the interview and holds the report."},
            {"node": "surveys-services", "detail": "retrieve_report / extract_processed_data pull and normalize the result."},
            {"node": "postgres", "detail": "Survey.processed_data and patient identity fields are written."},
            {"node": "task-queue", "detail": "complete_patient_creation is queued off the survey signal."},
        ],
        "outcome": "An intake interview becomes a Survey row with processed_data plus a fully created Patient.",
    },
    {
        "id": "flow-med-reminder",
        "name": "Medication reminder enrolment and adherence",
        "trigger": "A clinician creates a MedicationSchedule in client-v2.",
        "steps": [
            {"node": "client-v2", "detail": "Medication schedule form posts to the schedules endpoint."},
            {"node": "api-medications", "detail": "MedicationScheduleViewSet validates drug, dose windows and clinic inbox."},
            {"node": "ext-rxnav", "detail": "RxNav resolves the drug concept during search."},
            {"node": "postgres", "detail": "MedicationSchedule plus generated dose rows are written."},
            {"node": "task-queue", "detail": "sync_med_reminder_messages_continuous and the missed-dose sweep are scheduled."},
            {"node": "surveys-services", "detail": "get_switchbird_service builds the per-clinic calendar events."},
            {"node": "ext-switchbird", "detail": "SwitchBird sends the reminder texts and reports replies."},
            {"node": "api-medications", "detail": "mark_missed_doses records non-responses and RTM summaries are generated."},
        ],
        "outcome": "A patient receives scheduled reminder texts and adherence is tracked for RTM billing.",
    },
    {
        "id": "flow-chat",
        "name": "In-app assistant chat",
        "trigger": "A user opens the chat panel and the browser connects to ws/chat/.",
        "steps": [
            {"node": "client-v1", "detail": "chat-interface opens a WebSocket and sends an auth message first."},
            {"node": "api-chat", "detail": "ChatConsumer authenticates the token and joins the user group."},
            {"node": "redis", "detail": "The channel layer holds group membership for fan-out and force-disconnect."},
            {"node": "ext-openai", "detail": "AsyncOpenAI streams completion chunks."},
            {"node": "api-chat", "detail": "handle_streaming_chat relays chunks back over the socket."},
        ],
        "outcome": "The user gets a streamed assistant reply without the auth token ever appearing in a URL.",
    },
]
