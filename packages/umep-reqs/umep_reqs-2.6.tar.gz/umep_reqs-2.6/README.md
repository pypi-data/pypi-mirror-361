# umep-reqs
A minimal Python package outlining UMEP dependencies.

## Installation

```bash
pip install umep-reqs
```

## Version Management

This package uses `setuptools_scm` for automatic versioning based on Git tags. The package version is automatically determined from the latest Git tag.

### How to Update Dependencies

When a new version of SuPy or other dependencies is released:

1. **Update the dependency version** in `pyproject.toml`:
   ```toml
   dependencies = [
       "supy==2025.6.2.dev0",  # Update this version number
       "numba==0.59.0",
       # ... other dependencies
   ]
   ```

2. **Commit your changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Update SuPy to version X.X.X"
   ```

3. **Create a new release tag**:
   ```bash
   git tag 2.6  # Use the next version number
   git push origin main
   git push origin 2.6
   ```

4. **The CI/CD pipeline will automatically**:
   - Build the package with the new dependencies
   - Publish to Test PyPI (for all pushes)
   - Publish to PyPI (for tagged releases)
   - Create a GitHub release

### Important Notes

- **DO NOT** manually update version numbers in code - they are managed by Git tags
- All dependency updates should be made in `pyproject.toml`
- The `setup.py` file has been removed in favour of modern `pyproject.toml` configuration
- Version numbers follow semantic versioning (MAJOR.MINOR.PATCH)
