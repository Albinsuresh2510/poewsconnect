# accounts/adapters.py
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialAccount

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):

    def complete_login(self, request, app, token, response):
        login = super().complete_login(request, app, token, response)
        
        user = login.user
        extra_data = login.account.extra_data  # this is the Google profile data

        # Map extra fields if available
        user.full_name = extra_data.get("name", "")
        user.email = extra_data.get("email", "")
        user.phone = extra_data.get("phoneNumber", "")  # usually empty, need Google People API
        user.address = extra_data.get("address", "")     # usually empty

        return login
