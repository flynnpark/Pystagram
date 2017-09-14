import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Post, Like
from .forms import PostForm

def post_list(request):
    post_list = Post.objects.prefetch_related('tag_set', 'like_user_set__profile').select_related('author__profile').all()
    paginator = Paginator(post_list, 3)
    page_num = request.GET.get('page')
    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        tag = request.POST.get('tag')
        tag_clean = ''.join(e for e in tag if e.isalnum()) # 특수문자 삭제
        return redirect('post:post_search', tag_clean)
    return render(request, 'post/post_list.html', {
        'posts': posts,
    })

@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_save()
            messages.info(request, '새 글이 등록되었습니다.')
            return redirect('post:post_list')
    else:
        form = PostForm()
    return render(request, 'post/post_form.html', {
        'form': form,
    })

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(requestm, '잘못된 접근입니다.')
        return redirect('post/post_list')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.tag_set.all().delete()
            post.tag_save()
            messages.info(request, '수정 완료')
            return redirect('post:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'post/post_form.html', {
        'form': form,
    })

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.info(request, '잘못된 접근입니다.')
        return redirect('post:post_list')
    else:
        post.delete()
        messages.info(request, '삭제 완료')
        return redirect('post:post_list')

def post_search(request, tag):
    post_list = Post.objects.filter(tag_set__name__iexact=tag).select_related('author__profile').prefetch_related('tag_set')
    return render(request, 'post/post_list.html', {
        'tag': tag,
        'post_list': post_list,
    })


@login_required
@require_POST
def post_like(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    # 중간자 모델 Like를 사용하여, 현재 post와 request.user에 해당하는 Like 인스턴스를 가져온다.
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)
    if not post_like_created:
        post_like.delete()
        message = "좋아요 취소"
    else:
        message = "좋아요"
    context = {'like_count': post.like_count,
                'message': message,
                'nickname': request.user.profile.nickname}
    return HttpResponse(json.dumps(context))
