from django.test import TestCase
from django.contrib.auth.models import User
from books.models import BookReview
from personalization.models import Follows, Critic
from django.urls import reverse, resolve

# Model Unit Tests
class BooksTest(TestCase):
    def setUp(self):
        self.testUser = User.objects.create_user("John Doe", "johndoe@gmail.com", "johndoe")
        BookReview.objects.create(user=self.testUser, book_id="test book id", text_review="test book review", star_review=5)
    
    def tearDown(self):
        self.testUser.delete()

    def test_book_review_retrieve_by_user(self):
        review = BookReview.objects.get(user=self.testUser)
        self.assertEqual(review.book_id, "test book id")
        self.assertEqual(review.text_review, "test book review")
        self.assertEqual(review.star_review, 5)

# Testing books URLs
class BooksURLTest(TestCase):
    def test_books_url(self):
        url = reverse("books")
        self.assertEqual(url, "/books/")

    def test_book_view_url(self):
        url = reverse("book_view", args=["bookviewtest"])
        self.assertEqual(url, "/books/book_view/bookviewtest/")

    def test_book_review_url(self):
        url = reverse("book_review")
        self.assertEqual(url, "/books/book_review/")
        
# Testing URLs connect to correct view
class BooksURLtoViewTest(TestCase):
    def test_books_url_to_view(self):
        res = resolve("/books/")
        self.assertEqual(res.view_name, "books")

    def test_book_view_url_to_view(self):
        res = resolve("/books/book_view/bookviewtest/")
        self.assertEqual(res.view_name, "book_view")

    def test_book_review_url_to_view(self):
        res = resolve("/books/book_review/")
        self.assertEqual(res.view_name, "book_review")

# Testing books views
class BooksViewTest(TestCase):
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
        self.testBookID = "/works/OL82563W"
        self.testBookIDURL = "%works%OL82563W"

    def tearDown(self):
        self.testUser.delete()
        self.guestUser.delete()
    
    # books
    def test_book_search_get_request(self):
        self.client.post("/login/", self.login)
        resp = self.client.get("/books/", {
            "book_search": "harry potter",
            "search_books": "Search"
        }, follow=True)
        self.assertTrue(resp.context["form_data"])
        with self.assertRaises(KeyError):
            resp.context["book_preview"]

    def test_book_search_populated(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/", {
            "book_search": "harry potter",
            "search_books": "Search"
        }, follow=True)
        self.assertTrue(resp.context["book_preview"])

    def test_book_search_empty(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/", {
            "book_search": " ",
            "search_books": "Search"
        }, follow=True)
        with self.assertRaises(KeyError):
            resp.context["book_preview"]

    def test_book_search_no_search_books_keyword(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/", {
            "book_search": "harry potter",
        }, follow=True)
        with self.assertRaises(KeyError):
            resp.context["book_preview"]

    def test_books_favorite(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/", {
            "favorite": self.testBookID
        }, follow=True)
        self.assertTrue(resp.context["favorited_title"])

    def test_books_favorite_duplicate(self):
        self.client.post("/login/", self.login)
        self.client.post("/books/", {
            "favorite": self.testBookID
        })
        resp = self.client.post("/books/", {
            "favorite": self.testBookID
        }, follow=True)
        with self.assertRaises(KeyError):
            resp.context["favorited_title"]

    # book_view
    def test_book_view_valid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertTrue(resp.context["book_id"])

    def test_book_view_invalid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_view/invalid/", follow=True)
        with self.assertRaises(KeyError):
            resp.context["book_id"]
    
    def test_book_view_favorite(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", {
            "favorite": self.testBookID
        }, follow=True)
        self.assertTrue(resp.context["favorited_title"])

    def test_book_view_favorite_duplicate(self):
        self.client.post("/login/", self.login)
        self.client.post("/books/book_view/" + self.testBookIDURL + "/", {
            "favorite": self.testBookID
        })
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", {
            "favorite": self.testBookID
        }, follow=True)
        with self.assertRaises(KeyError):
            resp.context["favorited_title"]

    def test_book_view_with_my_review(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.testUser, book_id=self.testBookID, text_review="this is my review", star_review=3, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["my_review_exists"], 1)

    def test_book_view_without_my_review(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["my_review_exists"], 0)

    def test_book_view_with_general_reviews(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["general_reviews_exists"], 1)

    def test_book_view_without_general_reviews(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["general_reviews_exists"], 0)

    def test_book_view_with_follower_review(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["follow_reviews_exist"], 1)

    def test_book_view_without_follower_review(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["follow_reviews_exist"], 0)

    def test_book_view_low_follower_aggregate(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=2, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["follows_icon"], "low")

    def test_book_view_mid_follower_aggregate(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3.5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["follows_icon"], "mid")
    
    def test_book_view_high_follower_aggregate(self):
        self.client.post("/login/", self.login)
        Follows.objects.create(user=self.testUser, following_user=self.guestUser)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["follows_icon"], "high")

    def test_book_view_low_critic_aggregate(self):
        self.client.post("/login/", self.login)
        Critic.objects.create(user=self.guestUser, is_critic=True)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=2, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["critic_icon"], "low")

    def test_book_view_mid_critic_aggregate(self):
        self.client.post("/login/", self.login)
        Critic.objects.create(user=self.guestUser, is_critic=True)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3.5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["critic_icon"], "mid")
    
    def test_book_view_high_critic_aggregate(self):
        self.client.post("/login/", self.login)
        Critic.objects.create(user=self.guestUser, is_critic=True)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["critic_icon"], "high")

    def test_book_view_low_general_aggregate(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=2, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["general_icon"], "low")

    def test_book_view_mid_general_aggregate(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=3.5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["general_icon"], "mid")
    
    def test_book_view_high_general_aggregate(self):
        self.client.post("/login/", self.login)
        BookReview.objects.create(user=self.guestUser, book_id=self.testBookID, text_review="this is my review", star_review=5, book_title="Harry Potter and the Philosopher's Stone", book_cover="cover here")
        resp = self.client.post("/books/book_view/" + self.testBookIDURL + "/", follow=True)
        self.assertEquals(resp.context["general_icon"], "high")

    # book_review
    def test_book_review_valid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_review/", {
            "review": self.testBookID
        } , follow=True)
        self.assertTrue(resp.context["book_id"])

    def test_book_review_invalid(self):
        self.client.post("/login/", self.login)
        resp = self.client.post("/books/book_review/", follow=True)
        with self.assertRaises(KeyError):
            resp.context["book_id"]