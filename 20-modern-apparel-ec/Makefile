.PHONY: spanner-up spanner-down backend frontend

spanner-up:
	docker compose up -d

spanner-down:
	docker compose down

backend:
	export SPANNER_EMULATOR_HOST=localhost:9010 && \
	export GOOGLE_CLOUD_PROJECT=test-project && \
	export SPANNER_INSTANCE=test-instance && \
	export SPANNER_DATABASE=test-database && \
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev
