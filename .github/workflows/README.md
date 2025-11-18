# GitHub Actions Workflows

## CI/CD Pipeline

This project uses GitHub Actions for automated testing, linting, and Docker builds.

### Workflow: `ci.yml`

The CI pipeline runs on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Jobs

#### 1. Lint (`lint`)

- **Purpose**: Ensure code quality and formatting
- **Steps**:
  - Checkout code
  - Set up Python 3.13
  - Install flake8 and black
  - Run flake8 linter
  - Check code formatting with black
- **Triggers**: Always runs on push/PR

#### 2. Test (`test`)

- **Purpose**: Run unit tests with coverage
- **Steps**:
  - Checkout code
  - Set up Python 3.13
  - Install system dependencies (poppler, tesseract)
  - Install Python dependencies
  - Run pytest with coverage
  - Upload coverage to Codecov
- **Triggers**: Always runs on push/PR
- **Parallel**: Runs in parallel with `lint`

#### 3. Docker Build (`docker-build`)

- **Purpose**: Build and test Docker image
- **Steps**:
  - Checkout code
  - Set up Docker Buildx
  - Build Docker image
  - Test image can import code
- **Triggers**: Only after `lint` and `test` pass
- **Cache**: Uses GitHub Actions cache for layers

## Setup Requirements

No additional setup required! The workflow will run automatically on push/PR.

## Viewing Results

### Check Status

- Go to your repository on GitHub
- Click the **Actions** tab
- See all workflow runs and their status

### Check Badges

Add status badges to your README:

```markdown
![CI](https://github.com/USERNAME/REPO/workflows/CI/badge.svg)
```

### Coverage Reports

Coverage is automatically uploaded to Codecov if configured.

## Troubleshooting

### Lint Fails

```bash
# Run locally to see errors
flake8 src/ api.py main.py example.py

# Auto-fix formatting
black src/ api.py main.py example.py
```

### Tests Fail

```bash
# Run locally with verbose output
pytest -v

# Run specific test
pytest tests/test_api.py::test_health_endpoint -v
```

### Docker Build Fails

```bash
# Test build locally
docker build -t rag-api:test .

# Check logs
docker-compose logs
```

## Local Testing

Before pushing, test the CI pipeline locally:

```bash
# 1. Lint
flake8 src/ api.py main.py example.py
black --check src/ api.py main.py example.py

# 2. Test
pytest --cov=src

# 3. Docker Build
docker build -t rag-api:test .
docker run --rm rag-api:test python -c "import src; print('Success')"
```

Or use the Makefile:

```bash
make all  # Runs format, lint, and test
```

## Customization

### Modify Workflow

Edit `.github/workflows/ci.yml` to customize:

- Python version
- Branches to run on
- Additional jobs
- Deployment targets

### Add More Tests

Add new test files to `tests/` directory:

- Must start with `test_`
- Will automatically be discovered by pytest

### Change Docker Registry

To use a different registry (e.g., GitHub Container Registry):

1. Update `docker-push` job in `ci.yml`
2. Change `docker/login-action` configuration
3. Update image tags

## Best Practices

1. ✅ **Always run tests locally** before pushing
2. ✅ **Keep workflows fast** - use caching
3. ✅ **Fail fast** - run lint before tests
4. ✅ **Secure secrets** - never commit API keys
5. ✅ **Review logs** - check failed workflows immediately
6. ✅ **Update dependencies** - keep actions versions current

## Performance

Current workflow timing:

- **Lint**: ~30 seconds
- **Test**: ~1-2 minutes
- **Docker Build**: ~2-3 minutes
- **Total**: ~3-5 minutes

Tips to improve speed:

- Use caching for pip packages ✅
- Use caching for Docker layers ✅
- Run lint and test in parallel ✅
- Skip Docker push on PRs ✅
