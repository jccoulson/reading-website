from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app1.forms import JoinForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from personalization.models import PersonalInfo
from personalization.models import FavoriteBooks
from personalization.models import Follows
from personalization.models import Critic
from books.forms import BooksForm
from books.forms import BookReviewForm
from books.models import BookReview
#import urllib library
from urllib.request import urlopen
# import json
import json

@login_required(login_url='/login/')
def books(request):
    if (request.method == "POST"):
        if ("search_books" in request.POST):
            books_form = BooksForm(request.POST)
            if (books_form.is_valid()):
                book_search = books_form.cleaned_data["book_search"]
                #replace spaces with + for query
                book_search = book_search.replace(" ", "+")
                json_url = ".json"
                mode = "mode=ebooks" #make sure it has an ebook to filter out garbage submitted books on open library
                text = "has_fulltext=true" #also helps filter out incomplete books
                url = 'https://openlibrary.org/search{}?q={}&{}&{}'.format(json_url, book_search, mode, text )
                response = urlopen(url)
                #store json object from url response
                book_json = json.loads(response.read())
                book_cover = []
                book_title = []
                book_id = []
                book_original_id = [] #needed for favoriting the book, need unaltered id
                num_display = 0
                #choosing to display 5 books
                while num_display != 5:
                    #if it reaches how many books were found from query, cannot continue
                    if num_display == book_json["numFound"]:
                        break
                    book_cover.append("http://covers.openlibrary.org/b/id/"+str(book_json["docs"][num_display]["cover_i"])+"-L.jpg") #cover pic
                    book_title.append(book_json["docs"][num_display]["title"]) #title
                    book_temp_id = book_json["docs"][num_display]["key"] #getting id
                    book_original_id.append(book_temp_id) #need this for favorite book
                    book_temp_id = book_temp_id.replace("/", "%") #need to replace backslashes to pass through url or it messes up
                    book_id.append(book_temp_id)
                    num_display = num_display+1
                book_preview = zip(book_title, book_cover, book_id, book_original_id) #combine the lists to be able to display with loop
                context = {
                    "form_data": BooksForm(), #continue displaying form after searching
                    "book_preview": book_preview,
                }
                return render(request,'books/books.html', context)
            else:
                context = {
                    "form_data": BooksForm(), #display form
                }
                return render(request, 'books/books.html', context)
        elif("favorite" in request.POST): #user favorited book
            cur_user = request.user
            book_id = request.POST.get('favorite')
            book_url = 'https://openlibrary.org{}.json'.format(book_id)
            book_response = urlopen(book_url)
            book_json = json.loads(book_response.read()) #query to store title in FavoriteBooks
            book_title = book_json["title"]
            if 'covers' not in book_json:
                book_cover = "no_book"
            else:
                book_cover = ("http://covers.openlibrary.org/b/id/"+str(book_json["covers"][0])+"-L.jpg")

            if FavoriteBooks.objects.filter(favorite_id = book_id) & FavoriteBooks.objects.filter(user = cur_user):
                return redirect('/books/')
            FavoriteBooks(user = cur_user, favorite_id = book_id, favorite_title = book_title, favorite_cover = book_cover).save()
            context = {
                "form_data": BooksForm(), #continue displaying form
                "favorited_title": book_title,
            }
            return render(request,'books/books.html', context)
        else:
            context = {
                    "form_data": BooksForm(), #display form
            }
            return render(request, 'books/books.html', context)
    else:
        context = {
            "form_data": BooksForm(), #display search bar form
        }
        return render(request, 'books/books.html', context)

def book_view(request, info):
    #replace % signs that were necessary to pass book id in url back to backslashes
    info = info.replace("%", "/")
    book_id = info

    #query for book information
    book_url = 'https://openlibrary.org{}.json'.format(info)
    try:
        book_response = urlopen(book_url)
    except:
        context = {
            "form_data": BooksForm(), #display search bar form
        }
        return render(request, 'books/books.html', context)
    book_json = json.loads(book_response.read()) #store json object from url response

    #check if default cover is needed
    if 'covers' not in book_json:
        book_cover = "no_book"
    else:
        book_cover = "http://covers.openlibrary.org/b/id/"+str(book_json["covers"][0])+"-L.jpg"

    book_title = book_json["title"]
    if 'description' not in book_json:
        book_description = "There is no description available."
    else:
        book_description = book_json["description"]

    #get subjects of book for display
    book_subjects = []
    if 'subjects' in book_json:
        i = 0
        for subject in book_json["subjects"]: #getting the first 4 subjects listed on page
            if i == 4:
                break
            book_subjects.append(subject)
            i = i+1
    else:
        book_subjects = "no_subjects"

    #save form data if a book was just reviewed
    #make sure book doesn't already have review from user, important because the form always saves the first form data even if you come from any page
    if not BookReview.objects.filter(user = request.user) & BookReview.objects.filter(book_id = book_id):
        form = BookReviewForm(request.POST)
        if (form.is_valid()):
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.book_id = book_id
            new_review.star_review = form.cleaned_data['star_review']
            new_review.book_title = book_title
            new_review.book_cover = book_cover
            new_review.save()

    if (request.method == "POST"):
        if ("favorite" in request.POST):
            cur_user = request.user
            book_id = request.POST.get('favorite')
            book_url = 'https://openlibrary.org{}.json'.format(book_id)
            book_response = urlopen(book_url)
            book_json = json.loads(book_response.read()) #query to store title in FavoriteBooks
            book_title = book_json["title"]
            if 'covers' not in book_json:
                book_cover = "no_book" #doesn't exist
            else:
                book_cover = ("http://covers.openlibrary.org/b/id/"+str(book_json["covers"][0])+"-L.jpg")

            if FavoriteBooks.objects.filter(favorite_id = book_id) & FavoriteBooks.objects.filter(user = cur_user):
                return redirect('/books/')
            FavoriteBooks(user = cur_user, favorite_id = book_id, favorite_title = book_title, favorite_cover = book_cover).save()
            context = {
                "form_data": BooksForm(), #continue displaying form
                "favorited_title": book_title,
            }
            return render(request,'books/books.html', context)

    #check for review of current book, need to see if review has book id and current user
    my_text_review = ""
    my_star_review = 0
    my_review = 0

    myreview_query = BookReview.objects.filter(book_id = book_id) & BookReview.objects.filter(user = request.user)
    if myreview_query:
        temp_review = BookReview.objects.filter(book_id = book_id) & BookReview.objects.filter(user = request.user)
        #need to use loop to get the one review because filter returns queryset
        for i in temp_review:
            my_review = i
        #store for display in html
        my_text_review = my_review.text_review
        my_star_review = my_review.star_review
        my_review_exists = 1
    else:
        my_review_exists = 0

    #general reviews for display
    general_reviews = []
    if BookReview.objects.filter(book_id = book_id).exists():
        general_reviews = BookReview.objects.filter(book_id = book_id)
        general_reviews_exists = 1
    else:
        general_reviews_exists = 0

    #people followed reviews for display
    follow_reviews = []
    follow_star_review = []
    follow_text_review = []

    current_follows = Follows.objects.filter(user = request.user)
    #filter reviews for people followed
    for follows in current_follows:
        follow_review_query = BookReview.objects.filter(user = follows.following_user) & BookReview.objects.filter(book_id = book_id)
        if (follow_review_query):
            follow_reviews.append(list(BookReview.objects.filter(user = follows.following_user)))
    #check if list is empty
    if follow_reviews:
        follow_reviews_exist = 1
    else:
        follow_reviews_exist = 0


    #intialize variables for review aggregates
    general_aggregate = 0
    general_counter = 0
    follows_aggregate = 0
    follows_counter = 0
    critic_aggregate = 0
    critic_counter = 0

    #review aggregate for all people that user follows
    user_follows = Follows.objects.filter(user = request.user)
    for cur_user in user_follows:
        temp_follows_reviews = BookReview.objects.filter(book_id = book_id) & BookReview.objects.filter(user = cur_user.following_user)
        #check if the user you are following has a review
        if temp_follows_reviews.first():
            follows_aggregate = follows_aggregate + temp_follows_reviews.first().star_review #can use first to grab from quertyset because users can only leave one review
            follows_counter = follows_counter + 1

    #get average score
    if follows_counter != 0: #protect from divide by zero error
        follows_aggregate = follows_aggregate/follows_counter
        follows_aggregate = str(round(follows_aggregate, 1)) #round to two decimal places

    follows_aggregate = float(follows_aggregate)
    #find which icon to display based on score
    follows_available = 1
    if follows_aggregate == 0.0:
        follows_available = 0

    if follows_aggregate  < 3.0:
        follows_icon = "low"
    elif follows_aggregate < 3.9:
        follows_icon = "mid"
    else:
        follows_icon = "high"

    #review aggregate for all critics
    for object in Critic.objects.all():
        critic_review = BookReview.objects.filter(user = object.user) & BookReview.objects.filter(book_id = book_id)
        if critic_review.first():
            critic_aggregate = critic_aggregate + critic_review.first().star_review
            critic_counter = critic_counter + 1

    #get average critic score
    if critic_counter != 0:
        critic_aggregate = critic_aggregate/critic_counter
        critic_aggregate = str(round(critic_aggregate, 1))

    critic_aggregate = float(critic_aggregate)
    #find which icon to display based on score
    critic_available = 1
    if critic_aggregate == 0.0:
        critic_available = 0

    if critic_aggregate  < 3.0:
        critic_icon = "low"
    elif critic_aggregate < 3.9:
        critic_icon = "mid"
    else:
        critic_icon = "high"


    #review aggregate for all users
    temp_general_reviews = BookReview.objects.filter(book_id = book_id)
    for review in temp_general_reviews:
        general_aggregate = general_aggregate + review.star_review
        general_counter = general_counter + 1

    if general_counter != 0: #protect from divide by zero error
        general_aggregate = general_aggregate/general_counter
        general_aggregate = str(round(general_aggregate, 1)) #round to two decimal places

    general_aggregate = float(general_aggregate)

    general_available = 1
    if general_aggregate == 0.0:
        general_available = 0

    if general_aggregate  < 3.0:
        general_icon = "low"
    elif general_aggregate < 3.9:
        general_icon = "mid"
    else:
        general_icon = "high"


    #getting author json object to get author information
    author_id = book_json["authors"][0]["author"]['key']
    author_url = 'https://openlibrary.org{}.json'.format(author_id)
    author_response = urlopen(author_url)
    author_json = json.loads(author_response.read()) #store json object from url response

    #check if json object has author name
    author_name = "no_author"
    if 'personal_name' in author_json:
        author_name = author_json["personal_name"]

    if 'photos' not in author_json:
        author_image = "no_photo"
    else:
        author_image = "https://covers.openlibrary.org/a/id/" + str(author_json["photos"][0]) + "-L.jpg"

    favorited = False
    try:
        FavoriteBooks.objects.get(favorite_user=request.user, favorite_id=book_id)
        favorited = True
    except:
        favorited = False

    #book information and review information needed for display
    context = {
        "form_data": BooksForm(),
        "book_cover": book_cover,
        "book_title": book_title,
        "book_description": book_description,
        "book_subjects": book_subjects,
        "book_id": book_id,
        "author_name": author_name,
        "author_image": author_image,
        "my_text_review": my_text_review,
        "my_star_review": my_star_review,
        "general_reviews": general_reviews,
        "follow_reviews": follow_reviews,
        "my_review_exists": my_review_exists,
        "follow_reviews_exist": follow_reviews_exist,
        "general_reviews_exists": general_reviews_exists,
        "my_review": my_review,
        "follows_aggregate": follows_aggregate,
        "general_aggregate": general_aggregate,
        "critic_aggregate": critic_aggregate,
        "critic_icon": critic_icon,
        "follows_icon": follows_icon,
        "general_icon": general_icon,
        "general_available": general_available,
        "follows_available": follows_available,
        "critic_available": critic_available,
        "favorited": favorited,
    }
    return render(request, 'books/book_view.html', context)

def book_review(request):
    #review button was clicked
    if("review" in request.POST):
        #passed in book id with review post request
        book_id = request.POST.get("review")

        #query for cover and title display
        book_url = 'https://openlibrary.org{}.json'.format(book_id)
        book_response = urlopen(book_url)
        book_json = json.loads(book_response.read())
        if 'covers' not in book_json:
            book_cover = "no_book"
        else:
            book_cover = "http://covers.openlibrary.org/b/id/"+str(book_json["covers"][0])+"-L.jpg"
        book_title = book_json["title"]

        #get book_id in correct form to pass through url to view book page
        book_id = book_id.replace("/", "%")
        context = {
            "form_data": BookReviewForm(),
            "book_cover": book_cover,
            "book_title": book_title,
            "book_id": book_id,
        }
        return render(request, 'books/book_review.html', context)
    else:
        context = {
            "form_data": BooksForm(), #display search bar form
        }
        return render(request, 'books/books.html', context)
