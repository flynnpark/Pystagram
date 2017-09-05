from django.shortcuts import render
from .models import Post

def post_list(request):
    post_list = Post.objecs.all()
    return render(request, 'post/post_list.html', {
        'post_list': post_list,
    })
