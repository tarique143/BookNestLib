# file: utils.py
from sqlalchemy.orm import Session
from models import log_model, user_model

def create_log(
    db: Session, 
    user: user_model.User, 
    action_type: str, 
    description: str,
    target_type: str = None, 
    target_id: int = None
):
    """Database mein ek naya log entry create karta hai."""
    if not user:
        # Handle cases where action is not performed by a logged-in user
        log_entry = log_model.Log(
            action_by_id=None,
            action_type=action_type,
            description=description,
            target_type=target_type,
            target_id=target_id
        )
    else:
        log_entry = log_model.Log(
            action_by_id=user.id,
            action_type=action_type,
            description=description,
            target_type=target_type,
            target_id=target_id
        )
    db.add(log_entry)
    # Commit is handled by the calling function