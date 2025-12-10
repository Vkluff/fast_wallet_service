Contributing to Fast Wallet Service

Thank you for your interest in contributing to the Fast Wallet Service! This document provides guidelines and instructions for contributing.

Table of Contents

•
Code of Conduct

•
Getting Started

•
Development Setup

•
Making Changes

•
Coding Standards

•
Testing

•
Commit Messages

•
Pull Requests

•
Reporting Bugs

•
Suggesting Features




Code of Conduct

Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our Code of Conduct:

•
Be respectful - Treat all contributors with respect and courtesy

•
Be inclusive - Welcome people of all backgrounds and experience levels

•
Be collaborative - Work together to solve problems

•
Be professional - Keep discussions focused and constructive

Unacceptable Behavior

The following behaviors are not tolerated:

•
Harassment, discrimination, or abuse

•
Offensive comments or language

•
Spam or self-promotion

•
Sharing private information without consent




Getting Started

1. Fork the Repository

Bash


# Click "Fork" on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fast_wallet_service.git
cd fast_wallet_service


2. Add Upstream Remote

Bash


# Add the original repository as upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/fast_wallet_service.git

# Verify remotes
git remote -v


3. Create a Feature Branch

Bash


# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name





Development Setup

1. Create Virtual Environment

Bash


# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate


2. Install Dependencies

Bash


# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt


3. Install Pre-commit Hooks

Bash


# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run against all files
pre-commit run --all-files


4. Set Up Environment

Bash


# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env


5. Run Tests

Bash


# Run all tests
pytest

# Run with coverage
pytest --cov=fast_wallet_service





Making Changes

1. Code Organization

Follow the existing project structure:

Plain Text


fast_wallet_service/
├── routers/              # API endpoints
├── core/                 # Business logic
├── schemas/              # Data validation
├── dependencies/         # Dependency injection
└── tests/                # Tests


2. File Naming Conventions

•
Modules: snake_case.py

•
Classes: PascalCase

•
Functions: snake_case

•
Constants: UPPER_SNAKE_CASE

3. Create New Features

Bash


# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# 3. Add tests
# 4. Update documentation
# 5. Commit changes
# 6. Push to your fork
git push origin feature/new-feature

# 7. Create pull request on GitHub


4. Bug Fixes

Bash


# 1. Create bugfix branch
git checkout -b bugfix/issue-description

# 2. Fix the bug
# 3. Add regression test
# 4. Verify fix works
# 5. Commit and push
git push origin bugfix/issue-description

# 6. Create pull request on GitHub





Coding Standards

Python Style Guide

Follow PEP 8 with these tools:

Bash


# Format code with black
black fast_wallet_service/

# Check style with flake8
flake8 fast_wallet_service/

# Type checking with mypy
mypy fast_wallet_service/


Code Style Rules

1. Type Hints

Python


# ✅ Good
def get_user_by_id(db: AsyncSession, user_id: str ) -> User | None:
    """Retrieve a user by ID."""
    pass

# ❌ Bad
def get_user_by_id(db, user_id):
    pass


2. Docstrings

Python


# ✅ Good
def transfer_funds(
    db: AsyncSession,
    sender_id: str,
    recipient_id: str,
    amount: float
) -> Transaction:
    """
    Transfer funds between two wallets.
    
    Args:
        db: Database session
        sender_id: ID of the sender
        recipient_id: ID of the recipient
        amount: Amount to transfer
        
    Returns:
        Transaction: Created transaction record
        
    Raises:
        ValueError: If sender has insufficient balance
        HTTPException: If recipient wallet not found
    """
    pass

# ❌ Bad
def transfer_funds(db, sender_id, recipient_id, amount):
    # transfer logic
    pass


3. Comments

Python


# ✅ Good
# Verify webhook signature before processing
if not verify_paystack_signature(body, signature, secret):
    raise HTTPException(status_code=401, detail="Invalid signature")

# ❌ Bad
# Check signature
if not verify_paystack_signature(body, signature, secret):
    raise HTTPException(status_code=401, detail="Invalid signature")


4. Error Handling

Python


# ✅ Good
try:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")

# ❌ Bad
try:
    user = await get_user_by_id(db, user_id)
except:
    pass


5. Constants

Python


# ✅ Good
TRANSACTION_TIMEOUT_SECONDS = 300
MAX_TRANSFER_AMOUNT = 1_000_000
MIN_DEPOSIT_AMOUNT = 100

# ❌ Bad
timeout = 300
max_amount = 1000000


FastAPI Conventions

Python


# ✅ Good
@router.post("/wallet/transfer", response_model=TransactionResponse)
async def transfer_funds(
    transfer_request: TransferRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """Transfer funds to another wallet."""
    pass

# ❌ Bad
@app.post("/transfer")
def transfer(transfer_request, user_id, db):
    pass





Testing

Test Structure

Python


# tests/test_wallet.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_transfer_funds_success(async_client: AsyncClient ):
    """Test successful fund transfer."""
    # Arrange
    sender_id = "user-1"
    recipient_id = "user-2"
    amount = 1000
    
    # Act
    response = await async_client.post(
        "/wallet/transfer",
        json={"recipient_wallet_number": recipient_id, "amount": amount},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["amount"] == amount


Test Requirements

•
Coverage: Minimum 80% code coverage

•
Unit Tests: Test individual functions

•
Integration Tests: Test endpoint flows

•
Edge Cases: Test boundary conditions

Running Tests

Bash


# Run all tests
pytest

# Run specific test file
pytest tests/test_wallet.py

# Run specific test
pytest tests/test_wallet.py::test_transfer_funds_success

# Run with coverage
pytest --cov=fast_wallet_service --cov-report=html

# Run with verbose output
pytest -v

# Run with markers
pytest -m "not slow"





Commit Messages

Format

Plain Text


<type>(<scope>): <subject>

<body>

<footer>


Types

•
feat: New feature

•
fix: Bug fix

•
docs: Documentation changes

•
style: Code style changes (formatting, missing semicolons, etc.)

•
refactor: Code refactoring without feature changes

•
perf: Performance improvements

•
test: Test additions or changes

•
chore: Build, dependency, or tooling changes

•
ci: CI/CD configuration changes

Examples

Bash


# Feature
git commit -m "feat(auth): add JWT token refresh endpoint"

# Bug fix
git commit -m "fix(wallet): correct balance calculation for transfers"

# Documentation
git commit -m "docs(readme): add deployment instructions"

# Multiple line commit
git commit -m "feat(webhook): add Paystack webhook signature verification

- Implement HMAC-SHA512 signature verification
- Add webhook secret to environment variables
- Add tests for signature validation"


Commit Best Practices

•
✅ Commit frequently with logical changes

•
✅ Write clear, descriptive messages

•
✅ Reference issues in commits: fix #123

•
✅ Keep commits focused and atomic

•
❌ Don't mix multiple features in one commit

•
❌ Don't commit debug code or print statements




Pull Requests

Before Creating a PR




Fork and clone the repository




Create a feature branch




Make your changes




Write/update tests




Update documentation




Run tests locally: pytest




Run code quality checks: black, flake8, mypy




Commit with clear messages




Push to your fork

Creating a PR

1.
Go to GitHub and click "New Pull Request"

2.
Select branches:

•
Base: main (original repository)

•
Compare: your-feature-branch (your fork)



3.
Fill in PR template:

Markdown


## Description
Brief description of changes

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally


PR Review Process

1.
Automated Checks:

•
Tests must pass

•
Code coverage must be maintained

•
Style checks must pass



2.
Code Review:

•
Maintainers will review your code

•
Respond to feedback professionally

•
Make requested changes



3.
Approval:

•
Once approved, PR will be merged

•
Your changes will be included in next release



Addressing Feedback

Bash


# Make requested changes
# Commit with descriptive message
git commit -m "refactor: address PR feedback on wallet service"

# Push changes
git push origin feature/your-feature-name

# Don't force push unless requested





Reporting Bugs

Before Reporting




Check existing issues




Update to latest version




Try to reproduce the issue




Gather relevant information

Bug Report Template

Markdown


## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: macOS/Linux/Windows
- Python: 3.11
- FastAPI: 0.104
- Other relevant info

## Error Message


Full error traceback

Plain Text



## Additional Context
Screenshots, logs, or other relevant information


Bug Report Example

Markdown


## Description
Wallet balance is not updated after successful Paystack deposit

## Steps to Reproduce
1. Create user and get JWT token
2. Initiate deposit with amount 5000
3. Complete payment on Paystack
4. Check wallet balance

## Expected Behavior
Wallet balance should be 5000

## Actual Behavior
Wallet balance remains 0

## Environment
- OS: macOS 13.1
- Python: 3.11.0
- FastAPI: 0.104.1

## Error Message
No error in logs, webhook processed successfully

## Additional Context
Webhook signature verified successfully, transaction status is 'success'





Suggesting Features

Before Suggesting




Check existing issues and discussions




Verify it aligns with project goals




Consider implementation complexity

Feature Request Template

Markdown


## Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternative Solutions
Other possible approaches

## Additional Context
Related issues, discussions, or examples


Feature Request Example

Markdown


## Description
Add support for scheduled/recurring transactions

## Use Case
Users want to set up automatic recurring payments (e.g., subscriptions)

## Proposed Solution
- New endpoint: POST /wallet/recurring
- Schedule field with cron expression
- Automatic processing at scheduled times
- Ability to pause/cancel recurring transactions

## Alternative Solutions
- Use external scheduler service
- Client-side scheduling with API calls

## Additional Context
Similar to Stripe recurring charges





Development Workflow

Complete Example

Bash


# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/fast_wallet_service.git
cd fast_wallet_service

# 2. Add upstream
git remote add upstream https://github.com/ORIGINAL/fast_wallet_service.git

# 3. Create feature branch
git checkout -b feature/add-recurring-payments

# 4. Set up development environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Make changes
# Edit files, add features

# 6. Write tests
# Add tests in tests/ directory

# 7. Run tests
pytest --cov=fast_wallet_service

# 8. Format code
black fast_wallet_service/
flake8 fast_wallet_service/
mypy fast_wallet_service/

# 9. Commit changes
git add .
git commit -m "feat(wallet ): add recurring transaction support"

# 10. Push to fork
git push origin feature/add-recurring-payments

# 11. Create pull request on GitHub
# Fill in PR template with description and changes

# 12. Address feedback
# Make requested changes and push again
git commit -m "refactor: address PR feedback"
git push origin feature/add-recurring-payments

# 13. PR gets merged
# Celebrate! 🎉





Resources

•
FastAPI Documentation: https://fastapi.tiangolo.com/

•
SQLAlchemy Documentation: https://docs.sqlalchemy.org/

•
Python PEP 8: https://pep8.org/

•
Git Documentation: https://git-scm.com/doc

•
GitHub Help: https://docs.github.com/




Questions?

•
GitHub Discussions: https://github.com/yourusername/fast_wallet_service/discussions

•
GitHub Issues: https://github.com/yourusername/fast_wallet_service/issues

•
Email: support@example.com




Thank You!

Thank you for contributing to Fast Wallet Service! Your efforts help make this project better for everyone.

Happy coding! 🚀

