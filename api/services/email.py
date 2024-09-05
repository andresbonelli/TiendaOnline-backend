from fastapi.background import BackgroundTasks
from ..models import PrivateUserFromDB
from ..config import send_email, FRONTEND_HOST, FRONTEND_PORT, APP_TITLE
from ..services import AuthService

async def send_account_verification_email(user: PrivateUserFromDB, background_tasks: BackgroundTasks):
    
    context_string = f"{user.hash_password}{user.created_at.strftime('%d/%m/%Y,%H:%M:%S')}-verify" 
    token = AuthService.get_password_hash(context_string)
    activate_url = f"{FRONTEND_HOST}:{FRONTEND_PORT}/auth/account-verify?token={token}&email={user.email}"
    data = {
        "app_name": APP_TITLE,
        "name": user.username,
        "activate_url": activate_url
    }
    subject = f"Account Verification - {APP_TITLE}"
    await send_email(
        recipients=[user.email],
        subject=subject,
        template_name="account-verification.html",
        context=data,
        background_tasks=background_tasks
    )