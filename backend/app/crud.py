from sqlalchemy.orm import Session
import database
import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def create_or_update_user(db: Session, email: str, name: str, token: dict):
    user = get_user_by_email(db, email)

    token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=token.get("expires_in"))

    print(f"User: {user}")
    print(f"Email: {email}")
    print(f"Name: {name}")
    print(f"Token expiry time: {token_expiry}")
    print(f"Token: {token}")

    if user:
        user.access_token = token.get("access_token")
        user.refresh_token = token.get("refresh_token")
        user.token_expiry = token_expiry
    else:
        user = database.User(
            email=email,
            name=name,
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            token_expiry=token_expiry
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user
