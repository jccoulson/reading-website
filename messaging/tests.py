from django.test import TestCase
from django.contrib.auth.models import User
from messaging.models import Message
from django.urls import reverse, resolve

# Model Unit Tests
class MessageTest(TestCase):
    def setUp(self):
        self.testUser = User.objects.create_user("John Doe", "johndoe@gmail.com", "johndoe")
        self.testUser1 = User.objects.create_user("Jane Doe", "janedoe@gmail.com", "janedoe")
        Message.objects.create(sender=self.testUser, receiver=self.testUser1, content="test message content")
    
    def tearDown(self):
        self.testUser.delete()
        self.testUser1.delete()

    def test_message_retrieve_by_sender(self):
        msg = Message.objects.get(sender=self.testUser)
        self.assertEqual(msg.receiver, self.testUser1)
        self.assertEqual(msg.content, "test message content")

    def test_message_retrieve_by_receiver(self):
        msg = Message.objects.get(receiver=self.testUser1)
        self.assertEqual(msg.sender, self.testUser)
        self.assertEqual(msg.content, "test message content")

# Testing messaging URLs
class MessagingURLTest(TestCase):
    def test_inbox_url(self):
        url = reverse("inbox")
        self.assertEqual(url, "/inbox/")

    def test_compose_message_url(self):
        url = reverse("compose_message")
        self.assertEqual(url, "/inbox/compose_message/")

# Testing URLs connect to correct view
class MessagingURLtoViewTest(TestCase):
    def test_inbox_url_to_view(self):
        res = resolve("/inbox/")
        self.assertEqual(res.view_name, "inbox")

    def test_compose_message_url_to_view(self):
        res = resolve("/inbox/compose_message/")
        self.assertEqual(res.view_name, "compose_message")

# Testing app1 views
class MessagingViewTest(TestCase):
    def setUp(self):
        self.info = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johnd",
            "email": "johndoe@gmail.com",
            "password": "johndoe"
        }
        self.guest = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janed",
            "email": "janed@gmail.com",
            "password": "janed"
        }
        self.login = {
            "username": "johnd",
            "password": "johndoe"
        }
        self.testUser = User.objects.create_user(**self.info)
        self.guestUser = User.objects.create_user(**self.guest)

    def tearDown(self):
        self.testUser.delete()
        self.guestUser.delete()

    # inbox
    def test_inbox_empty(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/inbox/", follow=True)
        self.assertFalse(resp.context["incoming"])
        self.assertFalse(resp.context["outgoing"])

    def test_inbox_incoming(self):
        self.client.post("/login/", self.login)
        Message.objects.create(sender=self.guestUser, receiver=self.testUser, content="test")
        resp = self.client.post("/inbox/", follow=True)
        self.assertTrue(resp.context["incoming"])
        self.assertFalse(resp.context["outgoing"])

    def test_inbox_outgoing(self):
        self.client.post("/login/", self.login)
        Message.objects.create(sender=self.testUser, receiver=self.guestUser, content="test")
        resp = self.client.post("/inbox/", follow=True)
        self.assertFalse(resp.context["incoming"])
        self.assertTrue(resp.context["outgoing"])

    def test_inbox_incoming_and_outgoing(self):
        self.client.post("/login/", self.login)
        Message.objects.create(sender=self.guestUser, receiver=self.testUser, content="test")
        Message.objects.create(sender=self.testUser, receiver=self.guestUser, content="test")
        resp = self.client.post("/inbox/", follow=True)
        self.assertTrue(resp.context["incoming"])
        self.assertTrue(resp.context["outgoing"])

    def test_inbox_delete_valid_id(self):
        self.client.post("/login/", self.login)
        msg = Message.objects.create(sender=self.guestUser, receiver=self.testUser, content="test")
        resp = self.client.get("/inbox/", {
            "delete": msg.id
        }, follow=True)
        self.assertFalse(resp.context["incoming"])

    def test_inbox_delete_invalid_id(self):
        self.client.post("/login/", self.login)
        Message.objects.create(sender=self.guestUser, receiver=self.testUser, content="test")
        resp = self.client.get("/inbox/", {
            "delete": 20
        }, follow=True)
        self.assertTrue(resp.context["incoming"])

    # compose
    def test_compose_valid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/inbox/compose_message/", {
            "recipient": self.guest["username"],
            "content": "hello",
            "add": "Compose+Message"
        }, follow=True)
        self.assertEquals(resp.context["outgoing"][0].content, "hello")

    def test_compose_invalid_user(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/inbox/compose_message/", {
            "recipient": "invalid",
            "content": "hello",
            "add": "Compose+Message"
        }, follow=True)
        self.assertEquals(resp.context["dne"], "invalid")

    def test_compose_invalid_form(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/inbox/compose_message/", {
            "add": "Compose+Message"
        }, follow=True)
        self.assertTrue(resp.context["form_data"])

    def test_compose_invalid_no_add(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/inbox/compose_message/", {
            "recipient": self.guest["username"],
            "content": "hello",
        }, follow=True)
        self.assertFalse(resp.context["outgoing"])

    def test_compose_get_request(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/inbox/compose_message/", follow=True)
        self.assertTrue(resp.context["form_data"])
