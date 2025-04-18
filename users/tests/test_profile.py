from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from users.models import CustomUser
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='9399857569',
        )
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_complete_profile(self):
        url = reverse('users:profile-update')
        data = {
            'first_name': 'mohamamd',
            'last_name': 'hejazi',
            'email': 'updated@example.com',
            'password': 'password',
        }
        
        response = self.client.post(url, data)
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.first_name, 'mohamamd')