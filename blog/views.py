import logging
from django.shortcuts import render, get_object_or_404,redirect
from blog.forms import CommentForm
from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject
from django.utils import timezone
from blog.models import Post
from django.urls import reverse
logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    posts = (
        Post.objects.filter(published_at__lte=timezone.now())
        .select_related("author")
        .defer("created_at", "modified_at","title")
    )
    logger.debug("Got %d posts", len(posts))
    return render(request, "blog/index.html", {"posts": posts})


def post_detail(request, slug):
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    post = get_object_or_404(Post, slug=slug)
    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                logger.info(
    "Created comment on Post %d for user %s", post.pk, request.user
)

                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None

    return render(
        request, "blog/post-detail.html", {"post": post, "comment_form": comment_form}
    )

def get_ip(request):
  from django.http import HttpResponse
  return HttpResponse(request.META['REMOTE_ADDR'])

def post_table(request):
    return render(
        request, "blog/post-table.html", {"post_list_url": reverse("post-list")}
    )

