Remove-Item -Path "dist", "build", "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*