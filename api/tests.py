from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from main.models import Honeypot
import json
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class HoneypotCreationTest(APITestCase):
    def test_create_honeypot(self):
        url = reverse("honeypots")
        data = {"name": "test", "type": "general"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Honeypot.objects.count(), 1)
        self.assertEqual(Honeypot.objects.get().name, "test")
        self.assertEqual(Honeypot.objects.get().type, "general")


class HoneypotPermissionsTests(APITestCase):
    def setUp(self):
        url = reverse("honeypots")

        data = {"name": "test1", "type": "general"}
        resp = json.loads(self.client.post(url, data, format="json").content)
        self.user1_token = resp["token"]
        self.user1_id = resp["id"]

        data = {"name": "test2", "type": "general"}
        resp = json.loads(self.client.post(url, data, format="json").content)
        self.user2_token = resp["token"]
        self.user2_id = resp["id"]

    def test_honeypot_user_token(self):
        user_from_token = Token.objects.get(key=self.user1_token).user
        self.assertEqual(Honeypot.objects.get(pk=self.user1_id).author, user_from_token)
        self.assertNotEqual(
            Honeypot.objects.get(pk=self.user2_id).author, user_from_token
        )
        self.assertNotEqual(self.user1_token, self.user2_token)
        self.assertNotEqual(self.user1_id, self.user2_id)

    def test_post_attack(self):
        data = {
            "attacker": {
                "source_addr": "192.168.2.200",
                "source_port": 10213,
                "mac": "41-56-E6-AF-CD-BE",
            },
            "data": {"test": "test"},
        }
        url = reverse("attack", args=[self.user1_id])
        # Test with correct token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test with incorrect token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with missing token
        self.client.credentials()
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_attack(self):
        url = reverse("attack", args=[self.user1_id])
        # Test with correct token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with incorrect token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with missing token
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_honeypots(self):
        url = reverse("honeypots")
        # Test with correct token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with missing token
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_honeypot(self):
        url = reverse("honeypot", args=[self.user1_id])
        # Test with correct token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with incorrect token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test with missing token
        self.client.credentials()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
