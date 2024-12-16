from django.conf import settings

def user_balance(request):
    if request.user.is_authenticated:
        return {'user_balance': request.user.balance}
    return {'user_balance': 0.00}