# Support running both as a module and as a script
try:
	from .app import app  # type: ignore
except Exception:
	from app import app  # type: ignore

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
