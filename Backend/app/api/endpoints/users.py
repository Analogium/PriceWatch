"""
User self-service endpoints (GDPR rights: erasure Art.17, portability Art.20)
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_language
from app.core.security import verify_password
from app.db.base import get_db
from app.i18n import t
from app.models.product import Product
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.user import DeleteAccountRequest

router = APIRouter()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Delete the current user's account and all associated data (GDPR Art. 17).

    - Local/both auth: password confirmation required.
    - Google-only auth: no password needed, JWT is sufficient.
    """
    if current_user.auth_provider in ("local", "both") and current_user.password_hash:
        if not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=t("password_required_for_deletion", lang),
            )
        if not verify_password(request.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=t("incorrect_password", lang),
            )

    db.delete(current_user)
    db.commit()
    return None


@router.get("/me/export")
def export_own_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export all personal data for the current user as a JSON file (GDPR Art. 20).

    Includes: account info, tracked products, price history, and preferences.
    """
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    export_data = {
        "exported_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "auth_provider": current_user.auth_provider,
            "created_at": current_user.created_at.isoformat(),
        },
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "url": p.url,
                "current_price": p.current_price,
                "target_price": p.target_price,
                "is_available": p.is_available,
                "check_frequency_hours": p.check_frequency,
                "created_at": p.created_at.isoformat(),
                "last_checked": p.last_checked.isoformat(),
                "price_history": [
                    {"price": ph.price, "recorded_at": ph.recorded_at.isoformat()} for ph in p.price_history
                ],
            }
            for p in products
        ],
        "preferences": (
            {
                "email_notifications": preferences.email_notifications,
                "webhook_notifications": preferences.webhook_notifications,
                "price_drop_alerts": preferences.price_drop_alerts,
                "weekly_summary": preferences.weekly_summary,
                "language": preferences.language,
            }
            if preferences
            else None
        ),
    }

    return Response(
        content=json.dumps(export_data, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=pricewatch_data_{current_user.id}.json"},
    )
