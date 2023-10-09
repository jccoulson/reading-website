from django.test import TestCase
from django.contrib.auth.models import User
from personalization.models import FavoriteBooks
from posts.models import Post
from django.urls import reverse, resolve

# Model Unit Tests
class PostTest(TestCase):
    def setUp(self):
        self.testUser = User.objects.create_user("John Doe", "johndoe@gmail.com", "johndoe")
        self.favBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id="testid", favorite_title="testtitle", favorite_cover="testcover")
        Post.objects.create(title="test post title", content="test post content", user=self.testUser, book_object=FavoriteBooks.objects.get(favorite_id="testid"))

    def tearDown(self):
        self.favBook.delete()
        self.testUser.delete()

    def test_post_retrieve_by_user(self):
        post = Post.objects.get(user=self.testUser)
        self.assertEqual(post.title, "test post title")
        self.assertEqual(post.content, "test post content")
        self.assertEqual(post.book_object, self.favBook)

    def test_post_string(self):
        post = Post.objects.get(user=self.testUser)
        self.assertEqual(str(post), post.title)

# Testing posts URLs
class PostsURLTest(TestCase):
    def test_posts_url(self):
        url = reverse("posts")
        self.assertEqual(url, "/posts/")

    def test_add_post_url(self):
        url = reverse("add_post")
        self.assertEqual(url, "/posts/add_post/")

    def test_edit_post_url(self):
        url = reverse("edit_post", args=["1"])
        self.assertEqual(url, "/posts/edit_post/1/")

# Testing URLs connect to correct view
class PostsURLtoViewTest(TestCase):
    def test_posts_url_to_view(self):
        res = resolve("/posts/")
        self.assertEqual(res.view_name, "posts")

    def test_add_post_url_to_view(self):
        res = resolve("/posts/add_post/")
        self.assertEqual(res.view_name, "add_post")

    def test_edit_post_url_to_view(self):
        res = resolve("/posts/edit_post/1/")
        self.assertEqual(res.view_name, "edit_post")

# Testing posts views
class PostsViewTest(TestCase):
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
        self.testBookID = "/works/OL82563W"

    def tearDown(self):
        self.testUser.delete()

    # posts
    def test_posts_empty(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/posts/", follow=True)
        self.assertFalse(resp.context["posts"])

    def test_posts_populated(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.post("/posts/", follow=True)
        self.assertEquals(resp.context["posts"][0].title, "test post")
        self.assertEquals(resp.context["posts"][0].content, "hello")

    def test_posts_delete_post(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        post = Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.get("/posts/", {
            "delete": post.id
        }, follow=True)
        self.assertFalse(resp.context["posts"])

    # add_post
    def test_add_post_valid(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        resp = self.client.post("/posts/add_post/", {
            "title": "test_title",
            "content": "test_content",
            "book_object": fBook.id,
            "add": "Add+Post"
        }, follow=True)
        self.assertEquals(resp.context["posts"][0].title, "test_title")
        self.assertEquals(resp.context["posts"][0].content, "test_content")

    def test_add_post_invalid_form(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/posts/add_post/", {
            "add": "Add+Post"
        }, follow=True)
        self.assertTrue(resp.context["form_data"])

    def test_add_post_no_add_keyword(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        resp = self.client.post("/posts/add_post/", {
            "title": "test_title",
            "content": "test_content",
            "book_object": fBook.id,
        }, follow=True)
        self.assertFalse(resp.context["posts"])

    def test_add_post_get_request(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/posts/add_post/", follow=True)
        self.assertTrue(resp.context["form_data"])

    # edit_post
    def test_edit_post_get_request(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        post = Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.get("/posts/edit_post/" + str(post.id) + "/", follow=True)
        self.assertTrue(resp.context["form_data"])

    def test_edit_post_valid(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        post = Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.post("/posts/edit_post/" + str(post.id) + "/", {
            "title": "test_title",
            "content": "test_content",
            "book_object": fBook.id,
            "edit": "Edit+Post"
        }, follow=True)
        self.assertEquals(resp.context["posts"][0].title, "test_title")
        self.assertEquals(resp.context["posts"][0].content, "test_content")

    def test_edit_post_invalid_form(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        post = Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.post("/posts/edit_post/" + str(post.id) + "/", {
            "edit": "Edit+Post"
        }, follow=True)
        self.assertTrue(resp.context["form_data"])

    def test_edit_post_no_edit_keyword(self):
        self.client.post("/login/", self.login)
        fBook = FavoriteBooks.objects.create(user=self.testUser, favorite_id=self.testBookID, favorite_title="test_title", favorite_cover="test_cover")
        post = Post.objects.create(user=self.testUser, title="test post", content="hello", book_object=fBook)
        resp = self.client.post("/posts/edit_post/" + str(post.id) + "/", {
            "title": "test_title",
            "content": "test_content",
        }, follow=True)
        self.assertEquals(resp.context["posts"][0].title, "test post")
        self.assertEquals(resp.context["posts"][0].content, "hello")