from django.shortcuts import render, HttpResponse, redirect
from Blog.models import Post, BlogComment
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def blogHome(request): 
    allPosts= Post.objects.all()
    context={'allPosts': allPosts}
    return render(request, "blog/bloghome.html", context)

def blogPost(request, slug): 
    post=Post.objects.filter(slug=slug).first()
    comments= BlogComment.objects.filter(post=post, parent=None)
    replies= BlogComment.objects.filter(post=post).exclude(parent=None)
    replyDict={}
    for reply in replies:
        if reply.parent.sno not in replyDict.keys():
            replyDict[reply.parent.sno]=[reply]
        else:
            replyDict[reply.parent.sno].append(reply)

    context={'post':post, 'comments': comments, 'user': request.user, 'replyDict': replyDict}
    return render(request, "blog/blogPost.html", context)

def postComment(request):
    if request.method == "POST":
        comment_text = request.POST.get('comment', '').strip()  # Avoid NoneType errors
        user = request.user
        post_sno = request.POST.get('postSno')
        parent_sno = request.POST.get('parentSno', '')

        # Ensure post exists
        post = Post.objects.filter(sno=post_sno).first()
        if not post:
            messages.error(request, "Invalid post.")
            return redirect("/blog/")

        # Check if comment is empty
        if not comment_text:
            messages.error(request, "Please write a comment before posting.")
            return redirect(f"/blog/{post.slug}")

        # Check if it's a parent comment or a reply
        if parent_sno:
            parent_comment = BlogComment.objects.filter(sno=parent_sno).first()
            if parent_comment:
                comment = BlogComment(comment=comment_text, user=user, post=post, parent=parent_comment)
                messages.success(request, "Your reply has been posted successfully.")
            else:
                messages.error(request, "Invalid parent comment.")
                return redirect(f"/blog/{post.slug}")
        else:
            comment = BlogComment(comment=comment_text, user=user, post=post)
            messages.success(request, "Your comment has been posted successfully.")

        comment.save()
    
    return redirect(f"/blog/{post.slug}")