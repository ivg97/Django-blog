from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    '''
    Обработчик отображения списка статей.
     Получает объекты request в качестве обязательного аргумента.
    Запрашиваем из БД все опубликованные статьи  спомощью нашего
    менеджера published.
    render - формирует шаблон со списком статей. В ответ возвращается
    объект HttpResponse c HTML кодом. Render передает переданную ей
    переменные в контекст шаблона. Поэтому все переменные работают в шаблоне.
    '''
    object_list = Post.published.all().filter(status='published')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        print(tag)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3) # По три статьи на странице
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом ,
        # возвращаем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если страница не является больше, чем общее количество страниц,
        # возвращаем последнюю
        posts = paginator.page(paginator.num_pages)
    # posts = Post.published.all()
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})

def post_detail(request, year, month, day, post):
    '''
    Обработчик страницы статьи.
    Принмает аргументы для вывода статьи по указанным слагу и дате.
    В модели Post, у поля slug указан атрибут unique_for_date.
    Т е ограничение что б slug был уникальным.

    Используем get_object_or_404 для поиска нужной статьи. Она возвращает
    объект подходящий по параметрам или вызывает 404.
    '''

    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,)
    # Список активных комментариев для этой статьи
    # comments is <QuerySet[]>
    comments = post.comments.filter(active=True)
    comment_form = CommentForm()
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил коммент
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохр в БД
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье
            new_comment.post = post
            # Сохр комментрий в БД
            new_comment.save()
        else:
            comment_form = CommentForm()

    # формирование списка похожих статей
    post_list_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_list_ids)\
                        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                        .order_by('-same_tags', '-publish')[:4]

    return  render(request, 'blog/post/detail.html', {'post': post,
                                                      'comments': comments,
                                                      'new_comment': new_comment,
                                                      'comment_form': comment_form,
                                                      'similar_posts': similar_posts})


def post_share(request, post_id):
    '''получение статьи по идентификатору'''
    '''Принимает объект запроса request и post_id'''

    # вызываем get_object_or_404() для получения статьи с указанным
    # идентификатором. Убеждаемся что статьи опубликована
    post = get_object_or_404(Post, id=post_id, status='published')
    # sent  после отправки сообщения устанавливается в True
    # Используем для отображения сообщения об успешной отправке
    # в html шаблоне
    sent = False
    # Используем request для для отображения пустой формы и
    # для обработки введенных данных
    # Заполненная форма отправляется POST запросом
    # Пустая форма отображается методом GET
    print(request.method)
    if request.method == 'POST':
        #print('*' * 70+'\n'+'try - except | ' * 3 +'\n'+ '*'* 70+'\nif 1: POST')
        # request.method - это POST or GET
        # Если пользователь заполнил форму и отправляет POST-запросом.
        # Создаем объект формы, использую полученные из request.POST данные
        # форма была отправлена на сохранение
        # request.POST - это <QueryDict:{['':'']}>
        form = EmailPostForm(request.POST)
        print('#' * 70)
        print(form.is_valid())
        print('#' * 70)
        if form.is_valid():
            try:
                #print('if 2: is_valid() = True')
            # Выполняем проверку введенных данных с пом is_valid()
            # from.is_valid() - это True (без ошибок) или False (есть ошибки)
            # Список полей с ошибками смотрим в form.errors
            # все поля формы прошли валидацию, получаем введенные данные
            # с помощью form.cleaned_data.
            # Если форма не проходит валидащцию, то в cleaned_data попадут только
            # корректные поля
            # from.cleaned_data - это словарь с     {'name':'Name',
            #                  данными из формы      'email': 'Email',
            #                                        'to':' Email',
            #                                        'comments':'Text'}
                cd = form.cleaned_data
            # Отправка электронной почты
            # post.get_abcolute_url() - ecть /blog/2020/3/22/auther-post/
            # request.build_absolute_url(post.get_absolute_url()) -   есть
            # url статьи которой делятся
            # (http://localhost:8000/blog/2020/3/22/auther-post/)
                post_url = request.build_absolute_uri(post.get_absolute_url())
            # cоздаем ссылку на статью
                subject = '{} ({}) recommends you reading "{}"'.format(cd['name'],
                                                               cd['email'],
                                                               post.title)
            # Обращение к читателю в title
            # subject есть (Ваня (...@mail.ru) recommends you reading "Статья")

                message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,
                                                                 post_url,
                                                                 cd['name'],
                                                                 cd['comments'])

                send_mail(subject, message, 'admin@blog.com', [cd['to']])
                sent = True
            except ConnectionRefusedError:
                 print('except ConnectionRefusedError: is_valid() = True')
                # print('Message go to {}'.format(cd['email']))
                 sent = True
                 return render(request,
                             'blog/post/share.html',
                              {'post': post, 'form': form,
                                'sent': sent})
        else:
            # когда обработчик выполняется первый раз с GET-запросом, создаем
            # объект form, который будет отображен в шаблоне как пустая форма
            form = EmailPostForm()
            # print('else 1: is_valid = False')
            return render(request,
                          'blog/post/share.html',
                          {'post': post, 'form': form,
                           'sent': sent})
            # Если форма с ошибками, возвращаем ее с введенными пользователем
            # данными в html шаблон
    else:
        form = EmailPostForm()
        return render(request,
                      'blog/post/share.html',
                      {'post' : post,
                       'form': form,
                       'sent': sent})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector,search_query)
            ).filter(rank__gte=0.3).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form,
                                                         'query': query,
                                                         'results': results})



# Create your views here.
