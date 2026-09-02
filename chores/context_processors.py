from .demo_credentials import DEMO_LOGIN_PASSWORD, DEMO_LOGIN_USERNAME


def demo_credentials(request):
    return {
        "demo_login_username": DEMO_LOGIN_USERNAME,
        "demo_login_password": DEMO_LOGIN_PASSWORD,
    }
