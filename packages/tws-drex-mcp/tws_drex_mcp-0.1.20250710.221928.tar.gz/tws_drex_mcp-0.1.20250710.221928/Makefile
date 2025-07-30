.PHONY: build publish publish_test debug_local debug_pypi debug_testpypi_latest tag_version_local

build:
	uv run -m build

publish: 
	uv run twine upload dist/*

publish_test:
	uv run twine upload --repository testpypi dist/*

debug_local:
	npx @modelcontextprotocol/inspector uv run -m tws_drex_mcp

debug_pypi:
	npx @modelcontextprotocol/inspector uvx tws-drex-mcp

debug_testpypi_latest:
	npx @modelcontextprotocol/inspector uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --index-strategy unsafe-best-match tws-drex-mcp

tag_version_local:
	@echo "Creating local version tag with date/time..."
	@DATE=$$(date +%Y%m%d 2>/dev/null || powershell -c "Get-Date -Format 'yyyyMMdd'"); \
	TIME=$$(date +%H%M%S 2>/dev/null || powershell -c "Get-Date -Format 'HHmmss'"); \
	COMMIT_HASH=$$(git rev-parse --short HEAD); \
	NEW_VERSION="v0.1.$$DATE.$$TIME"; \
	echo "Creating version tag: $$NEW_VERSION (commit: $$COMMIT_HASH)"; \
	git tag $$NEW_VERSION; \
	echo "✅ Created tag: $$NEW_VERSION"

test_full_cycle:
	@echo "🚀 Testing full development cycle..."
	$(MAKE) tag_version_local
	$(MAKE) build
	$(MAKE) publish_test
	@echo "✅ Published to TestPyPI! Now test with: make debug_testpypi_latest"
