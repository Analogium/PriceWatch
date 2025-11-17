from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user_preferences import UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesResponse
from app.models.user_preferences import UserPreferences
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/preferences", response_model=UserPreferencesResponse)
def get_user_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's notification preferences."""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    # If preferences don't exist, create default ones
    if not preferences:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


@router.post("/preferences", response_model=UserPreferencesResponse, status_code=status.HTTP_201_CREATED)
def create_user_preferences(
    preferences_data: UserPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create notification preferences for the current user."""
    # Check if preferences already exist
    existing_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if existing_preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Preferences already exist. Use PUT to update them."
        )

    # Validate webhook settings
    if preferences_data.webhook_notifications and not preferences_data.webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL is required when webhook notifications are enabled",
        )

    # Create new preferences
    preferences = UserPreferences(user_id=current_user.id, **preferences_data.model_dump())
    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


@router.put("/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's notification preferences."""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    # If preferences don't exist, create them
    if not preferences:
        # Create default preferences first
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    # Update only provided fields
    update_data = preferences_data.model_dump(exclude_unset=True)

    # Validate webhook settings if being updated
    if "webhook_notifications" in update_data:
        webhook_enabled = update_data["webhook_notifications"]
        webhook_url = update_data.get("webhook_url", preferences.webhook_url)
        if webhook_enabled and not webhook_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook URL is required when webhook notifications are enabled",
            )

    for field, value in update_data.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return preferences


@router.delete("/preferences", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete current user's notification preferences (reset to defaults)."""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if preferences:
        db.delete(preferences)
        db.commit()

    return None
