from django.test import TestCase
from django.contrib.auth.models import User
from personalization.models import PersonalInfo, FavoriteBooks
from django.urls import reverse, resolve

# Testing app1 URLs
class App1URLTest(TestCase):
    def test_home_url(self):
        url = reverse("home")
        self.assertEqual(url, "/")

    def test_join_url(self):
        url = reverse("join")
        self.assertEqual(url, "/join/")

    def test_login_url(self):
        url = reverse("login")
        self.assertEqual(url, "/login/")

    def test_home_url(self):
        url = reverse("logout")
        self.assertEqual(url, "/logout/")

# Testing URLs connect to correct view
class App1URLtoViewTest(TestCase):
    def test_home_url_to_view(self):
        res = resolve("/")
        self.assertEqual(res.view_name, "home")

    def test_join_url_to_view(self):
        res = resolve("/join/")
        self.assertEqual(res.view_name, "join")

    def test_login_url_to_view(self):
        res = resolve("/login/")
        self.assertEqual(res.view_name, "login")

    def test_logout_url_to_view(self):
        res = resolve("/logout/")
        self.assertEqual(res.view_name, "logout")

# Testing app1 views
class JoinTest(TestCase):
    def setUp(self):
        self.infoGood = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johnd",
            "email": "johndoe@gmail.com",
            "password": "johndoe"
        }
        self.infoBad = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janed",
            "email": "janedoe.com",
            "password": "janedoe"
        }
    
    def test_join_valid(self):
        self.client.post("/join/", self.infoGood, follow=True)
        self.assertTrue(User.objects.get(username=self.infoGood["username"]))

    def test_join_false_bad_info(self):
        resp = self.client.post("/join/", self.infoBad, follow=True)
        self.assertRaises(User.DoesNotExist, User.objects.get, username=self.infoBad["username"])
        self.assertTrue(resp.context["join_form"])

    def test_join_get_request(self):
        resp = self.client.get("/join/", follow=True)
        self.assertTrue(resp.context["join_form"])

class LoginLogoutTest(TestCase):
    def setUp(self):
        self.info = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johnd",
            "email": "johndoe@gmail.com",
            "password": "johndoe"
        }
        self.loginT = {
            "username": "johnd",
            "password": "johndoe"
        }
        self.loginF = {
            "username": "janed",
            "password": "janedoe"
        }
        self.testUser = User.objects.create_user(**self.info)

    def tearDown(self):
        self.testUser.delete()

    def test_login_true(self):
        resp = self.client.post("/login/", self.loginT, follow=True)
        self.assertTrue(resp.context["user"].is_authenticated)

    def test_login_false(self):
        resp = self.client.post("/login/", self.loginF, follow=True)
        self.assertFalse(resp.context["user"].is_authenticated)

    def test_login_invalid_form(self):
        resp = self.client.post("/login/", follow=True)
        self.assertTrue(resp.context["login_form"])

    def test_login_inactive_user(self):
        self.testUser.is_active = False
        self.testUser.save()
        resp = self.client.post("/login/", self.loginT, follow=True)
        self.assertFalse(resp.context["user"].is_authenticated)

    def test_login_get_request(self):
        resp = self.client.get("/login/", follow=True)
        self.assertTrue(resp.context["login_form"])

    def test_logout(self):
        self.client.post("/login/", self.loginT, follow=True)
        resp = self.client.post("/logout/", follow=True)
        self.assertFalse(resp.context["user"].is_authenticated)

class HomeTest(TestCase):
    def setUp(self):
        self.info = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johnd",
            "email": "johndoe@gmail.com",
            "password": "johndoe"
        }
        self.login = {
            "username": "johnd",
            "password": "johndoe"
        }
        self.testUser = User.objects.create_user(**self.info)

    def tearDown(self):
        self.testUser.delete()

    def test_no_activity_no_personal_info_home(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/")
        self.assertTrue(resp.context["current_profile"])
        with self.assertRaises(StopIteration):
            next(resp.context["activity"])

    def test_exisiting_personal_info_home(self):
        PersonalInfo.objects.create(user=self.testUser)
        self.client.post("/login/", self.login)
        resp = self.client.post("/")
        self.assertTrue(resp.context["current_profile"])

    # NOTE: The "activity" attr is empty even though view returns a tuple - unsure why this does not work
    # def test_with_activity_home(self):
    #     self.client.post("/login/", self.login)
    #     PersonalInfo.objects.create(user=self.testUser)
    #     FavoriteBooks.objects.create(user=self.testUser, favorite_id="test id", favorite_title="test title", favorite_cover="test cover")
    #     resp = self.client.post("/")
    #     # print(list(resp.context["activity"]))
    #     self.assertTrue(next(resp.context["activity"]))