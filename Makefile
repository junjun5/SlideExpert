PROJECT_ID := YOUR_PROJECT_ID
LOCATION := us-central1
AGENT_NAME := slide_agent
APP_NAME := slide_agent_app

.PHONY: install
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync

.PHONY: deploy
deploy:
	# Export dependencies to requirements file
	(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > slide_app/app_utils/.requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > slide_app/app_utils/.requirements.txt) && \
	uv run -m slide_app.app_utils.deploy \
		--source-packages=./slide_app \
		--entrypoint-module=slide_app.agent_engine_app \
		--entrypoint-object=agent_engine \
		--requirements-file=slide_app/app_utils/.requirements.txt

register-gemini-enterprise:
	@UV_INDEX_URL="https://pypi.org/simple/" UV_EXTRA_INDEX_URL="" uvx agent-starter-pack@0.39.4 register-gemini-enterprise
