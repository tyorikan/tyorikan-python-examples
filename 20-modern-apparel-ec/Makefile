.PHONY: spanner-up spanner-down spanner-init backend frontend

spanner-up:
	podman-compose up -d

spanner-down:
	podman-compose down

spanner-init:
	export SPANNER_EMULATOR_HOST=localhost:9010 && \
	export GOOGLE_CLOUD_PROJECT=test-project && \
	export SPANNER_INSTANCE=test-instance && \
	export SPANNER_DATABASE=test-database && \
	./backend/scripts/setup_db.sh

backend:
	export SPANNER_EMULATOR_HOST=localhost:9010 && \
	export GOOGLE_CLOUD_PROJECT=test-project && \
	export SPANNER_INSTANCE=test-instance && \
	export SPANNER_DATABASE=test-database && \
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev
