# Contributing to MorphoVue

Thank you for your interest in contributing to MorphoVue! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- Git
- Firebase CLI
- Basic knowledge of React, FastAPI, PyTorch, and MONAI

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/MorphoVue.git
   cd MorphoVue
   ```

3. Set up backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your Firebase credentials
   ```

4. Set up frontend:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start services:
   ```bash
   cd docker
   docker-compose up -d
   ```

## Development Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactor: `refactor/description`

Example: `feature/add-vtk-3d-viewer`

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(frontend): add 3D visualization with VTK.js

Implement VTK.js viewer component for displaying CT scans
with segmentation overlays.

Closes #123

fix(backend): resolve Firebase timeout issue

Increase timeout for large file uploads.

docs(readme): update installation instructions
```

### Pull Request Process

1. Create a new branch from `main`
2. Make your changes
3. Write/update tests if applicable
4. Update documentation if needed
5. Run linters and tests:
   ```bash
   # Backend
   cd backend
   black app/
   flake8 app/
   
   # Frontend
   cd frontend
   npm run lint
   npm test
   ```

6. Push to your fork
7. Create a Pull Request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots (if UI changes)
   - Test results

8. Address review feedback
9. Squash commits if requested
10. Wait for approval and merge

### Code Review

Reviewers will check for:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations

Please be patient and responsive to feedback.

## Project Structure

```
MorphoVue/
├── frontend/          # React application
├── backend/          # FastAPI server
├── ml-pipeline/      # Kamiak ML scripts
├── slicer-module/    # 3D Slicer extension
├── docker/           # Docker Compose config
├── firebase/         # Firebase configuration
└── docs/             # Documentation
```

## Coding Standards

### Python (Backend/ML)

- Follow PEP 8
- Use Black for formatting
- Type hints where appropriate
- Docstrings for all functions/classes
- Maximum line length: 100 characters

Example:
```python
from typing import List, Dict

def process_scan(scan_id: str, options: Dict[str, Any]) -> List[Dict]:
    """
    Process CT scan with given options.
    
    Args:
        scan_id: Unique scan identifier
        options: Processing options dictionary
    
    Returns:
        List of segmentation results
    
    Raises:
        ValueError: If scan_id is invalid
    """
    pass
```

### JavaScript/React (Frontend)

- Use ESLint configuration
- Functional components with hooks
- PropTypes or TypeScript types
- Descriptive variable names
- Comments for complex logic

Example:
```javascript
import React, { useState, useEffect } from 'react';

/**
 * Component for displaying CT scan information
 * @param {Object} props - Component props
 * @param {string} props.scanId - Scan identifier
 */
function ScanView({ scanId }) {
  const [scan, setScan] = useState(null);
  
  useEffect(() => {
    loadScan(scanId);
  }, [scanId]);
  
  // ...
}
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

Create tests in `backend/tests/`:
```python
def test_create_project():
    """Test project creation"""
    response = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'Test'
    })
    assert response.status_code == 200
```

### Frontend Tests

```bash
cd frontend
npm test
```

Create tests in `frontend/src/`:
```javascript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  expect(screen.getByText(/projects/i)).toBeInTheDocument();
});
```

### ML Pipeline Tests

```bash
cd ml-pipeline
python -m pytest
```

## Documentation

### Code Documentation

- Document all public APIs
- Include usage examples
- Update README files
- Add inline comments for complex logic

### User Documentation

Update documentation in `docs/`:
- API endpoints: `docs/api.md`
- User guides: `docs/user-guide.md`
- Deployment: `docs/deployment-guide.md`

## Feature Requests

1. Check existing issues for duplicates
2. Create new issue with:
   - Clear description
   - Use case
   - Proposed solution (optional)
   - Screenshots/mockups (if applicable)

## Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, browser, versions)
- Screenshots/logs
- Possible fix (optional)

Template:
```markdown
**Description**
Brief description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

## Adding New Features

### ML Models

To add a new model:

1. Create module in `ml-pipeline/`:
   ```python
   # ml-pipeline/new_model.py
   class NewModel:
       def __init__(self):
           pass
       
       def train(self, data):
           pass
       
       def predict(self, input):
           pass
   ```

2. Integrate into pipeline
3. Add tests
4. Update documentation

### API Endpoints

To add a new endpoint:

1. Define model in `backend/app/models.py`
2. Create router in `backend/app/routers/`
3. Add to `backend/app/main.py`
4. Update API documentation
5. Add frontend integration

### Frontend Components

To add a new component:

1. Create in `frontend/src/components/`
2. Add to relevant page
3. Style with Tailwind CSS
4. Add tests
5. Update documentation

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch: `release/v1.0.0`
4. Run all tests
5. Create pull request to main
6. Merge after approval
7. Tag release: `git tag v1.0.0`
8. Push tag: `git push origin v1.0.0`
9. Create GitHub release
10. Deploy to production

## Getting Help

- GitHub Issues: Technical questions
- Discussions: General questions
- Email: Project team contact
- Documentation: Check docs/ directory

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in publications (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

Feel free to ask questions by:
- Opening an issue
- Starting a discussion
- Contacting the maintainers

Thank you for contributing to MorphoVue!

