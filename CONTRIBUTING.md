# Contributing to Joulaa Platform

We welcome contributions to the Joulaa Platform! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Security](#security)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** (latest version)
- **Docker** and **Docker Compose**
- **Node.js** 18+ and **npm**
- **Python** 3.11+ and **Poetry**
- **kubectl** (for Kubernetes deployments)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/joulaa-platform.git
   cd joulaa-platform
   ```

2. **Set up the development environment**
   ```bash
   # Make the setup script executable and run it
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

3. **Verify the setup**
   ```bash
   # Check that all services are running
   docker-compose ps
   
   # Test backend API
   curl http://localhost:8000/health
   
   # Test frontend
   curl http://localhost:3000
   ```

## Development Workflow

### Branch Strategy

We use **Git Flow** branching model:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes
- `release/*` - Release preparation

### Creating a Feature Branch

```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes and commit
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks
- `perf` - Performance improvements
- `ci` - CI/CD changes

**Examples:**
```bash
feat(auth): add OAuth2 integration
fix(api): resolve user registration validation
docs(readme): update installation instructions
test(backend): add unit tests for user service
```

## Coding Standards

### Backend (Python)

#### Code Style
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: **88 characters**

#### Tools Configuration
```bash
# Format code
cd backend
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 .
poetry run mypy .

# Security check
poetry run bandit -r app/
```

#### Best Practices
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Follow dependency injection patterns
- Use Pydantic models for data validation
- Implement proper error handling

**Example:**
```python
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: str
    password: str
    full_name: Optional[str] = None

def create_user(user_data: UserCreate) -> User:
    """Create a new user in the database.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user instance
        
    Raises:
        ValueError: If email already exists
    """
    # Implementation here
    pass
```

### Frontend (React/TypeScript)

#### Code Style
- Use **TypeScript** for all components
- Follow **Airbnb** ESLint configuration
- Use **Prettier** for code formatting
- Use **functional components** with hooks

#### Tools Configuration
```bash
# Format and lint code
cd frontend
npm run lint
npm run lint:fix
npm run format

# Type checking
npm run type-check
```

#### Best Practices
- Use TypeScript interfaces for props and state
- Implement proper error boundaries
- Use React Query for API calls
- Follow atomic design principles
- Implement accessibility (a11y) standards

**Example:**
```typescript
interface UserCardProps {
  user: User;
  onEdit: (user: User) => void;
  className?: string;
}

const UserCard: React.FC<UserCardProps> = ({ user, onEdit, className }) => {
  const handleEditClick = useCallback(() => {
    onEdit(user);
  }, [user, onEdit]);

  return (
    <div className={`user-card ${className || ''}`}>
      <h3>{user.fullName}</h3>
      <p>{user.email}</p>
      <button onClick={handleEditClick} aria-label={`Edit ${user.fullName}`}>
        Edit
      </button>
    </div>
  );
};

export default UserCard;
```

### Database

#### Migrations
- Use **Alembic** for database migrations
- Write both upgrade and downgrade functions
- Include descriptive migration messages
- Test migrations on sample data

```bash
# Create migration
cd backend
poetry run alembic revision --autogenerate -m "Add user preferences table"

# Apply migration
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## Testing Guidelines

### Backend Testing

#### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test data
└── conftest.py    # Pytest configuration
```

#### Writing Tests
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert "password" not in response.json()

@pytest.mark.asyncio
async def test_user_service():
    """Test user service methods."""
    # Test implementation
    pass
```

#### Running Tests
```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_users.py

# Run tests matching pattern
poetry run pytest -k "test_user"
```

### Frontend Testing

#### Test Structure
```
src/
├── components/
│   └── __tests__/
├── pages/
│   └── __tests__/
├── utils/
│   └── __tests__/
└── __tests__/
    ├── setup.ts
    └── helpers/
```

#### Writing Tests
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UserCard from '../UserCard';

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('UserCard', () => {
  const mockUser = {
    id: '1',
    email: 'test@example.com',
    fullName: 'Test User',
  };
  
  const mockOnEdit = jest.fn();

  beforeEach(() => {
    mockOnEdit.mockClear();
  });

  it('renders user information', () => {
    renderWithProviders(
      <UserCard user={mockUser} onEdit={mockOnEdit} />
    );
    
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    renderWithProviders(
      <UserCard user={mockUser} onEdit={mockOnEdit} />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /edit test user/i }));
    
    expect(mockOnEdit).toHaveBeenCalledWith(mockUser);
  });
});
```

#### Running Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run tests in watch mode
npm run test:watch
```

## Documentation

### Code Documentation
- Write clear, concise comments
- Document complex algorithms and business logic
- Use JSDoc for JavaScript/TypeScript
- Use docstrings for Python

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Document all endpoints, parameters, and responses
- Provide example requests and responses
- Keep documentation up-to-date with code changes

### README Updates
- Update README.md for significant changes
- Include setup instructions
- Document new features and breaking changes
- Provide troubleshooting guides

## Pull Request Process

### Before Submitting

1. **Ensure your code follows our standards**
   ```bash
   # Backend
   cd backend
   poetry run black .
   poetry run isort .
   poetry run flake8 .
   poetry run mypy .
   poetry run pytest
   
   # Frontend
   cd frontend
   npm run lint:fix
   npm run format
   npm run type-check
   npm test
   ```

2. **Update documentation**
   - Update relevant README sections
   - Add/update API documentation
   - Update CHANGELOG.md

3. **Test your changes**
   - Run full test suite
   - Test manually in development environment
   - Verify no breaking changes

### Submitting Pull Request

1. **Create descriptive PR title**
   ```
   feat(auth): implement OAuth2 integration with Google
   fix(api): resolve user registration validation issue
   docs(readme): update installation instructions
   ```

2. **Fill out PR template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

3. **Request review**
   - Assign relevant reviewers
   - Add appropriate labels
   - Link related issues

### Review Process

1. **Automated checks must pass**
   - CI/CD pipeline
   - Code quality checks
   - Security scans

2. **Code review requirements**
   - At least 2 approvals for main branch
   - At least 1 approval for develop branch
   - All conversations resolved

3. **Merge requirements**
   - All checks passing
   - Up-to-date with target branch
   - No merge conflicts

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 13.0]
- Browser: [e.g., Chrome 118]
- Version: [e.g., 1.0.0]

**Screenshots**
If applicable, add screenshots

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this be implemented?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Any other relevant information
```

### Security Issues

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email security@your-domain.com
2. Include detailed description
3. Provide steps to reproduce
4. Allow time for fix before disclosure

## Security

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow OWASP security guidelines
- Implement proper input validation
- Use parameterized queries
- Implement rate limiting
- Use HTTPS in production

### Security Review Process

1. **Automated security scanning**
   - Dependency vulnerability checks
   - Static code analysis
   - Container image scanning

2. **Manual security review**
   - Code review for security issues
   - Architecture review
   - Penetration testing (for major releases)

## Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and discussions
- **Slack** - Real-time communication (invite only)
- **Email** - security@your-domain.com for security issues

### Getting Help

1. **Check existing documentation**
   - README.md
   - API documentation
   - GitHub wiki

2. **Search existing issues**
   - Open issues
   - Closed issues
   - GitHub discussions

3. **Create new issue**
   - Use appropriate template
   - Provide detailed information
   - Add relevant labels

### Recognition

We recognize contributors through:

- **Contributors list** in README
- **Release notes** mentions
- **GitHub achievements** and badges
- **Annual contributor awards**

## License

By contributing to Joulaa Platform, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Joulaa Platform!** 🚀

Your contributions help make this project better for everyone. If you have any questions about contributing, please don't hesitate to ask in our community channels.