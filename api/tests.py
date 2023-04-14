from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from main.models import Honeypot, Honeynet
import json, uuid
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from main.management.commands.config import Command as HoneypotGroupInit


# class HoneypotCreationTest(APITestCase):
#     def test_create_honeypot(self):
#         url = reverse("honeypots")
#         data = {"name": "test"}
#         response = self.client.post(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Honeypot.objects.count(), 1)
#         self.assertEqual(Honeypot.objects.get().name, "test")


class HoneypotPermissionsTests(APITestCase):
    def setUp(self):
        if not Group.objects.filter(name="honeypot").exists():
            HoneypotGroupInit().handle()
        honeypot_group = Group.objects.get(name="honeypot")

        user1 = User.objects.create_user(
            username="honeypot-{}".format(str(uuid.uuid4()))
        )
        user1.groups.add(honeypot_group)

        user2 = User.objects.create_user(
            username="honeypot-{}".format(str(uuid.uuid4()))
        )
        user2.groups.add(honeypot_group)
        self.user2_id = user2.pk

        # self.user1_token = resp["token"]
        # self.user1_id = resp["id"]
        # self.user2_token = resp["token"]
        # self.user2_id = resp["id"]
        hn = Honeynet.objects.create(
            name="test",
        )
        hp1 = Honeypot.objects.create(
            name="test1",
            honeynet=hn,
            author=user1,
        )
        hp2 = Honeypot.objects.create(name="test2", honeynet=hn, author=user2)
        self.user1_token = str(Token.objects.create(user=user1))
        self.user1_id = hp1.id
        self.user2_token = str(Token.objects.create(user=user2))
        self.user2_id = hp2.id

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
        url = reverse("attack", kwargs={"pk": self.user1_id})
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
        url = reverse("attack", kwargs={"pk": self.user1_id})
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

    # def test_get_honeypots(self):
    #     url = reverse("honeypots")
    #     # Test with correct token
    #     self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     # Test with missing token
    #     self.client.credentials()
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_honeypot(self):
    #     url = reverse("honeypot", kwargs={"pk":self.user1_id})
    #     # Test with correct token
    #     self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     # Test with incorrect token
    #     self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    #     # Test with missing token
    #     self.client.credentials()
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
