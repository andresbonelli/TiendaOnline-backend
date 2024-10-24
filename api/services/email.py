from fastapi.background import BackgroundTasks

from ..models import PrivateUserFromDB, UserFromDB, OrderFromDB, CompletedOrderProduct
from ..config import send_email, FRONTEND_HOST, APP_TITLE
from ..services import AuthService

async def send_account_verification_email(user: PrivateUserFromDB, background_tasks: BackgroundTasks):
    
    context_string = f"{user.hash_password}{user.created_at.strftime('%d/%m/%Y,%H:%M:%S')}-verify" 
    token = AuthService.get_password_hash(context_string)
    activate_url = f"{FRONTEND_HOST}/auth/verify?token={token}&email={user.email}"
    print(activate_url)
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
    
async def send_reset_password_email(user: PrivateUserFromDB, background_tasks: BackgroundTasks):

    context_string = f"{user.hash_password}{user.modified_at.strftime('%d/%m/%Y,%H:%M:%S')}-reset-password" 
    token = AuthService.get_password_hash(context_string)
    reset_password_url = f"{FRONTEND_HOST}/auth/reset-password?token={token}&email={user.email}"
    print(reset_password_url)
    data = {
        "app_name": APP_TITLE,
        "name": user.username,
        "reset_url": reset_password_url
    }
    subject = f"Reset Password - {APP_TITLE}"
    await send_email(
        recipients=[user.email],
        subject=subject,
        template_name="password-reset.html",
        context=data,
        background_tasks=background_tasks
    )
    
async def send_order_completion_email(
    user: UserFromDB,
    order: OrderFromDB,
    product_details: list[CompletedOrderProduct],
    background_tasks: BackgroundTasks):
    data = {
        "app_name": APP_TITLE,
        "name": user.username,
        "order": order.model_dump(),
        "products": product_details,
        "tracking_url": "https://fakecourier.com/tracking/orders/1234"
    }
    subject = f"Order completed - {APP_TITLE}"
    await send_email(
        recipients=[user.email],
        subject=subject,
        template_name="order-completion.html",
        context=data,
        background_tasks=background_tasks
    )
        
        