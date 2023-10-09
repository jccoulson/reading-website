from django.test import TestCase
from django.contrib.auth.models import User
from personalization.models import PersonalInfo, Critic, Follows, FavoriteBooks
from posts.models import Post
from django.urls import reverse, resolve

# Model Unit Tests
class PersonalizationTest(TestCase):
    def setUp(self):
        self.testUser = User.objects.create_user("John Doe", "johndoe@gmail.com", "johndoe")
        self.testUser1 = User.objects.create_user("Jane Doe", "janedoe@gmail.com", "janedoe")
        PersonalInfo.objects.create(user=self.testUser, about_user="test personal about") # unsure about personal_image attr for testing
        Critic.objects.create(user=self.testUser1, is_critic=True)
        Critic.objects.create(user=self.testUser, is_critic=False)
        Follows.objects.create(user=self.testUser, following_user=self.testUser1)
        FavoriteBooks.objects.create(user=self.testUser, favorite_id="test fav book id", favorite_title="test fav book title", favorite_cover="test fav book cover")

    def tearDown(self):
        self.testUser.delete()
        self.testUser1.delete()

    def test_personal_info_retrieve_by_user(self):
        pInfo = PersonalInfo.objects.get(user=self.testUser)
        self.assertEqual(pInfo.about_user, "test personal about")

    def test_critic_retrieve_by_user_true(self):
        criticT = Critic.objects.get(user=self.testUser1)
        self.assertEqual(criticT.is_critic, True)

    def test_critic_retrieve_by_user_false(self):
        criticF = Critic.objects.get(user=self.testUser)
        self.assertEqual(criticF.is_critic, False)

    def test_follows_retrieve_by_user(self):
        follow = Follows.objects.get(user=self.testUser)
        self.assertEqual(follow.following_user, self.testUser1)

    def test_follows_retrieve_by_following(self):
        follow = Follows.objects.get(following_user=self.testUser1)
        self.assertEqual(follow.user, self.testUser)

    def test_favorite_books_retrieve_by_user(self):
        favBook = FavoriteBooks.objects.get(user=self.testUser)
        self.assertEqual(favBook.favorite_id, "test fav book id")
        self.assertEqual(favBook.favorite_title, "test fav book title")
        self.assertEqual(favBook.favorite_cover, "test fav book cover")

    def test_favorite_books_string(self):
        favBook = FavoriteBooks.objects.get(user=self.testUser)
        self.assertEqual(str(favBook), "test fav book title")

# Testing personalization URLs
class PersonalURLTest(TestCase):
    def test_profile_url(self):
        url = reverse("personalization", args=["johnd"])
        self.assertEqual(url, "/personalization/johnd/")

    def test_edit_profile_url(self):
        url = reverse("edit_profile", args=[1])
        self.assertEqual(url, "/personalization/edit_profile/1/")

# Testing URLs connect to correct view
class PersonalURLtoViewTest(TestCase):
    def test_profile_url_to_view(self):
        res = resolve("/personalization/johnd/")
        self.assertEqual(res.view_name, "personalization")

    def test_edit_profile_url_to_view(self):
        res = resolve("/personalization/edit_profile/1/")
        self.assertEqual(res.view_name, "edit_profile")

# Testing books views
class PersonalViewTest(TestCase):
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
        PersonalInfo.objects.create(user=self.testUser)
        PersonalInfo.objects.create(user=self.guestUser)
        self.testBookID = "/works/OL82563W"

    def tearDown(self):
        self.testUser.delete()
        self.guestUser.delete()

    def test_personal_valid_empty(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/personalization/" + self.guest["username"] + "/", follow=True)
        self.assertTrue(resp.context["profile"])
        self.assertEquals(resp.context["req_user"], self.guestUser.username)

    def test_personal_valid_followed(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        resp = self.client.get("/personalization/" + self.guest["username"] + "/", follow=True)
        self.assertEquals(resp.context["al_fol"], True)

    def test_personal_follow_post_request(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/personalization/" + self.guest["username"] + "/", follow=True)
        self.assertEquals(resp.context["al_fol"], True)

    def test_personal_valid_with_fav_books(self):
        self.client.post("/login/", self.login)
        FavoriteBooks.objects.create(user=self.guestUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        resp = self.client.get("/personalization/" + self.guest["username"] + "/", follow=True)
        self.assertTrue(resp.context["favorite_books"])

    def test_personal_valid_with_posts(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.guestUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        Post.objects.create(user=self.guestUser, title="test_title", content="test_content", book_object=fBook)
        resp = self.client.get("/personalization/" + self.guest["username"] + "/", follow=True)
        self.assertTrue(resp.context["posts"])

    # edit_profile
    def test_edit_profile_get_request(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/personalization/edit_profile/" + str(self.testUser.id) + "/", follow=True)
        self.assertTrue(resp.context["form_data"])
        self.assertEquals(resp.context["user"], self.testUser)

    def test_edit_profile_valid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/personalization/edit_profile/" + str(self.testUser.id) + "/", {
                "about_user": "about me",
                "edit": "edit"
            }, follow=True)
        self.assertEquals(resp.context["profile"].about_user, "about me")

    def test_edit_profile_no_edit(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/personalization/edit_profile/" + str(self.testUser.id) + "/", {
                "about_user": "about me",
            }, follow=True)
        self.assertFalse(resp.context["profile"].about_user)

    def test_edit_profile_invalid_form(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/personalization/edit_profile/" + str(self.testUser.id) + "/", {
                "edit": "edit"
            }, follow=True)
        self.assertTrue(resp.context["form_data"])

    # add_friend
    def test_add_friend_get_request_empty(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/addFriends/", follow=True)
        self.assertTrue(resp.context["form"])
        self.assertFalse(resp.context["following"])
        self.assertFalse(resp.context["followers"])

    def test_add_friend_get_request_following(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        resp = self.client.get("/addFriends/", follow=True)
        self.assertTrue(resp.context["following"])

    def test_add_friend_get_request_followers(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.guestUser, following_user=self.testUser)
        resp = self.client.get("/addFriends/", follow=True)
        self.assertTrue(resp.context["followers"])

    def test_add_friend_search_valid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/addFriends/", {
            "userName": self.guest["username"]
        }, follow=True)
        self.assertEquals(resp.context["following"][0].following_user, self.guestUser)

    def test_add_friend_search_invalid_form(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/addFriends/", follow=True)
        self.assertTrue(resp.context["form"])
        self.assertFalse(resp.context["following"])
        self.assertFalse(resp.context["followers"])

    def test_add_friend_search_invalid_username(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/addFriends/", {
            "userName": "invalid"
        }, follow=True)
        self.assertEquals(resp.context["dne"], "invalid")