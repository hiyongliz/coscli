.PHONY: sync
sync:
	@ECHO "Syncing the package..."
	uv sync
	@ECHO "Sync completed."

.PHONY: build
build:
	@ECHO "Building the package..."
	bash build.sh
	@ECHO "Build completed."
