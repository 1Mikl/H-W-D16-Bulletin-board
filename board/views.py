from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import send_mail

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .filters import PostFilter

from .forms import *
from .models import *


# Create your views here.
class PostsList(ListView):
    model = Post
    ordering = '-time_create'
    template_name = 'ads.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'adsdetal.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        if UserResponse.objects.filter(author_response_id=self.request.user.id).filter(article_id=self.kwargs.get('pk')):
            context['response'] = "Откликнулся"
        elif self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            context['response'] = "Мое_объявление"
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = AddPostForm
    template_name = 'addpost.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'/post/{post.id}')


class PostUpdate(PermissionRequiredMixin, UpdateView):
    model = Post
    permission_required = 'board.change_post'
    form_class = AddPostForm
    template_name = 'addpost.html'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Редактировать объявление может только его автор")

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/post/' + str(self.kwargs.get('pk')))


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('board.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Удалить объявление может только его автор")


class PostAb(ListView):
    model = Post
    template_name = 'abouth.html'
    context_object_name = 'posts'


class Respond(LoginRequiredMixin, CreateView):
    model = UserResponse
    form_class = RespondForm
    template_name = 'respond.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        response = form.save(commit=False)
        response.author_response = User.objects.get(id=self.request.user.id)
        response.article = Post.objects.get(id=self.kwargs.get('pk'))
        response.save()
        send_mail(
            subject=f'MMORPG: новый отклик на объявление!',
            message=f'Доброго дня, {response.article.author}, ! На ваше объявление есть новый отклик!\n'
                    f'Прочитать отклик:\nhttp://127.0.0.1:8000/responses/{response.article.id}',
            from_email='Zela52@yandex.ru',
            recipient_list=[response.article.author.email, ],
        )
        return redirect(f'/post/{self.kwargs.get("pk")}')


title = str("")


class Responses(LoginRequiredMixin, ListView):
    model = UserResponse
    template_name = 'responses.html'
    context_object_name = 'responses'

    def get_context_data(self, *args, **kwargs):
        context = super(Responses, self).get_context_data(**kwargs)
        global title
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            # print(title)
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            article_id = Post.objects.get(title=title)
            context['filter_responses'] = list(UserResponse.objects.filter(article_id=article_id).order_by('-dateCreation'))
            context['response_post_id'] = article_id.id
        else:
            context['filter_responses'] = list(
                UserResponse.objects.filter(article_id__author_id=self.request.user).order_by('-dateCreation'))
            context['myresponses'] = list(UserResponse.objects.filter(author_response=self.request.user).order_by('-dateCreation'))
            return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = UserResponse.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        send_mail(
            subject=f'MMORPG: Ваш отклик принят!',
            message=f'Доброго дня, {response.author_response}, Автор объявления {response.article.title} принял Ваш отклик!\n'
                    f'Посмотреть принятые отклики:\nhttp://127.0.0.1:8000/responses',
            from_email='Zela52@yandex.ru',
            recipient_list=[response.article.author.email, ],
        )
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = UserResponse.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')