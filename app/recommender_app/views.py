from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Post, MoviesRead, get_mediafile, get_s3_mediafile
from .forms import MoviesForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .accessories import user_movies, user_movies_s3
from .validators import validate_file_extension2, validate_file_s3
import boto3
from io import BytesIO
import inspect
import cProfile
from time import sleep, time

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

def home_view(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, "recommender_app/movies_home.html", context)
    # return HttpResponse('<h1>Blog Home</h1>')

def health(request):
    return HttpResponse("Healthcheck OK", content_type="text/plain")

class PostListView(ListView):
    model = MoviesRead
    template_name = 'recommender_app/movies_home.html'  # to replace the default <app>/<model>_<viewtype>.html
    context_object_name = 'posts'  # this is already a list as opposed to  home_view
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = MoviesRead
    template_name = 'recommender_app/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post  # this will just be referred in the template as object

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about_view(request):
    context = {
        'title': 'About'
    }
    return render(request, "recommender_app/about.html", context)
    # return HttpResponse('<h1>Blog About</h1>')

def movieserror_view(request):
    context = {
        'title': 'Movies Error'
    }
    return render(request, "recommender_app/movies_error.html", context)

def movies_result_view(request):
    return render(request, "recommender_app/movies_result.html")
    # return HttpResponse('<h1>Blog Home</h1>')

def movies_prepare(request):
    return render(request, "recommender_app/movies_prepare_input.html")

def movies_s3_view(request):
    # print("october******** hello from ****{}**************".format(inspect.stack()[0][3]))
    movies_data, file_name = get_s3_mediafile()
    if request.method == 'POST':
        movies_form = MoviesForm(request.POST, request.FILES)
        if movies_form.is_valid():
            obj = MoviesRead()
            title = movies_form.cleaned_data['title']
            print("*** {} from ***{}".format(file_name, inspect.stack()[0][3]))
            obj.title = title
            obj.file_name = file_name
            obj.author = request.user
            if request.FILES.get('file_name'):
                try:
                    file_name = request.FILES.get('file_name')
                    print("**PATH1*  {} from ***{}".format(file_name, inspect.stack()[0][3]))
                    obj.file_name = file_name
                    assert validate_file_s3(file_name)
                except Exception as err:
                    print(err)
                    messages.error(request, ('Oops! S3 FILES.get file extension is not .csv'))
                    return redirect('movieserror')  # replace about with an error page with a button to send user back to movies_upload
            obj.save()
            file_path = 'static/' + obj.file_name.name  # 'static/csv_files/user_ratings.csv' #obj.file_name #this only works aftr the above save()
            print("**PATH2* {} from ***{}".format(file_path, inspect.stack()[0][3]))
            if request.FILES.get('file_name'):
                file_name = 'static/' + obj.file_name.name
            if not validate_file_s3(file_name):
                messages.error(request, ('Oops! Your S3 file extension is not .csv'))
                return redirect('movieserror')

            try:
                movies = user_movies_s3(file_name)
            except Exception as err:
                print(err)
                messages.error(request, ('Oops! Inconsistent input'))
                return redirect('movieserror')
        print("*** {} from ***{}".format(file_name, inspect.stack()[0][3]))
        messages.success(request, ('Recommendation applied, based on you csv!'))
        context = {'title': 'Summary of movies data', 'movies': movies}
        return render(request, 'recommender_app/movies_result.html', context)
    movies_form = MoviesForm(initial={'file_name': get_s3_mediafile})
    context = {'title': 'Read csv data', 'movies_form': movies_form}
    # return render(request, 'recommender_app/movies_read_form.html')
    return render(request, 'recommender_app/movies_read_form.html', context)

def movies_view(request):
    if request.method == 'POST':
        movies_form = MoviesForm(request.POST, request.FILES)
        if movies_form.is_valid():
            obj = MoviesRead()
            title = movies_form.cleaned_data['title']
            file_name = movies_form.cleaned_data['file_name']
            obj.title = title
            obj.file_name = file_name
            obj.author = request.user
            obj.save()
            file_path = obj.file_name.path  # this only works aftr the above save()
            if not validate_file_extension2(file_path):
                messages.error(request, ('Oops! Your file extension is not .csv'))
                return redirect('movieserror')  # replace about with an error page with a button to send user back to movies_upload
            try:
                movies = user_movies(file_path)
            except Exception as err:
                print(err)
                messages.error(request, ('Oops! Inconsistent input'))
                return redirect('movieserror')
        # print("********summarised_movies****{}**************".format(summarised_movies))
        messages.success(request, ('xxxxxx Your movies file has been added!'))
        # return redirect('movies_result')
        context = {'title': 'Summary of  movies', 'movies': movies}
        return render(request, 'recommender_app/movies_result.html', context)
    movies_form = MoviesForm(initial={'file_name': get_mediafile()})
    context = {'title': 'Read movies data', 'movies_form': movies_form}
    # return render(request, 'recommender_app/movies_read_form.html')
    return render(request, 'recommender_app/movies_read_form.html', context)
