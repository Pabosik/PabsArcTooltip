lock:
	rm uv.lock
	uv lock

env:
	rm uv.lock
	uv lock
	uv sync

run:
	uv run arc-helper

calibrate:
	uv run arc-calibrate

db_list:
	uv run arc-db list
