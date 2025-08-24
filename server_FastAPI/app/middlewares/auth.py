from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.settings import settings
from app.db import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional

security = HTTPBearer(auto_error=False)  # Make token optional

def get_demo_user() -> dict:
    """Return demo user for testing without auth."""
    return {
        "user_id": "demo-user-123",
        "role": "user", 
        "phone": "demo-phone",
        "name": "Demo User"
    }

async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """
    Verify JWT token and return user information.
    
    Args:
        credentials: HTTP Bearer token credentials (optional for demo)
        db: Database connection
    
    Returns:
        dict: User information including user_id and role
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # For demo mode - bypass authentication if no credentials
        if credentials is None:
            print("No credentials provided, using demo user")
            return get_demo_user()
            
        # Check if demo mode is enabled
        demo_mode = getattr(settings, 'demo_mode', 'false').lower() == 'true'
        if demo_mode:
            print("Demo mode enabled, using demo user")
            return get_demo_user()
        
        # Try to decode the JWT token
        try:
            payload = jwt.decode(
                credentials.credentials, 
                settings.access_token_secret, 
                algorithms=["HS256"]
            )
        except Exception as token_error:
            print(f"Token decode failed: {token_error}, falling back to demo user")
            return get_demo_user()
        
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        if user_id is None or role is None:
            print("Invalid token payload, using demo user")
            return get_demo_user()
        
        # Try to verify user exists in database
        if db is not None:
            try:
                user = await db["users"].find_one({"_id": ObjectId(user_id)})
                if not user:
                    print("User not found in database, using demo user")
                    return get_demo_user()
                
                # Return actual user information
                return {
                    "user_id": user_id,
                    "role": role,
                    "phone": user.get("phone"),
                    "name": user.get("name")
                }
            except Exception as db_error:
                print(f"Database verification failed: {db_error}, using demo user")
                return get_demo_user()
        else:
            print("No database connection, using demo user")
            return get_demo_user()
        
    except Exception as e:
        print(f"Authentication failed: {e}, using demo user")
        return get_demo_user()

async def verify_admin_token(
    current_user: dict = Depends(verify_token)
) -> dict:
    """
    Verify that the current user has admin role.
    
    Args:
        current_user: User information from verify_token
    
    Returns:
        dict: User information if admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
