# Path: tests/test_token.py
import pytest
from app.dependencies import jwt, SECRET_KEY, ALGORITHM

@pytest.mark.asyncio
async def test_token_generation_and_validation(test_user, test_session):
    """Test token generation and validation."""
    # Generate token
    token = test_user.get_token()
    print(f"Generated token: {token}")
    
    # Decode token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(test_user.id)
    
    # Test user retrieval
    from app.crud import get_user
    user = await get_user(test_session, user_id=payload["sub"])
    assert user is not None
    assert user.id == test_user.id
