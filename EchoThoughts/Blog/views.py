import logging
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from Blog.models import Post, BlogComment
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Configure logging
logger = logging.getLogger(__name__)

# Home: Show all blog posts
def blogHome(request): 
    logger.info("Fetching all blog posts.")
    allPosts = Post.objects.all()
    context = {'allPosts': allPosts}
    return render(request, "blog/bloghome.html", context)

# Show a single blog post
def blogPost(request, slug): 
    logger.info(f"Fetching blog post with slug: {slug}")
    post = get_object_or_404(Post, slug=slug)
    comments = BlogComment.objects.filter(post=post, parent=None)
    replies = BlogComment.objects.filter(post=post).exclude(parent=None)
    
    replyDict = {}
    for reply in replies:
        if reply.parent.sno not in replyDict.keys():
            replyDict[reply.parent.sno] = [reply]
        else:
            replyDict[reply.parent.sno].append(reply)

    context = {'post': post, 'comments': comments, 'user': request.user if request.user.is_authenticated else None, 'replyDict': replyDict}
    return render(request, "blog/blogPost.html", context)

# Handle user comments
def postComment(request):
    if request.method == "POST":
        logger.info("Processing new comment.")
        comment_text = request.POST.get('comment', '').strip()
        user = request.user
        post_sno = request.POST.get('postSno')
        parent_sno = request.POST.get('parentSno', '')

        post = Post.objects.filter(sno=post_sno).first()
        if not post:
            logger.warning(f"Invalid post reference: {post_sno}")
            messages.error(request, "Invalid post.")
            return redirect("/blog/")

        if not comment_text:
            logger.warning("User attempted to post an empty comment.")
            messages.error(request, "Please write a comment before posting.")
            return redirect(f"/blog/{post.slug}")

        if parent_sno:
            parent_comment = BlogComment.objects.filter(sno=parent_sno).first()
            if parent_comment:
                comment = BlogComment(comment=comment_text, user=user, post=post, parent=parent_comment)
                logger.info(f"Reply added to comment ID: {parent_sno}")
                messages.success(request, "Your reply has been posted successfully.")
            else:
                logger.warning(f"Invalid parent comment reference: {parent_sno}")
                messages.error(request, "Invalid parent comment.")
                return redirect(f"/blog/{post.slug}")
        else:
            comment = BlogComment(comment=comment_text, user=user, post=post)
            logger.info("New comment added.")
            messages.success(request, "Your comment has been posted successfully.")

        comment.save()
    
    return redirect(f"/blog/{post.slug}")

# Create a new post
@login_required
def createPost(request):
    if request.method == "POST":
        logger.info("Processing new post creation.")
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        slug = request.POST.get("slug", "").strip()

        if not title or not content or not slug:
            logger.warning("User attempted to create a post with missing fields.")
            messages.error(request, "All fields are required.")
            return redirect("createPost")

        if Post.objects.filter(slug=slug).exists():
            logger.warning(f"Duplicate slug detected: {slug}")
            messages.error(request, "Slug already exists. Choose a different one.")
            return redirect("createPost")

        post = Post(title=title, content=content, slug=slug, author=request.user)
        post.save()
        logger.info(f"Post created successfully with slug: {slug}")
        messages.success(request, "Your post has been created successfully.")
        return redirect("blogHome")

    return render(request, "blog/create_post.html")

# Edit an existing post
@login_required
def editPost(request, post_sno):
    logger.info("Enter in edit function.")
    post = get_object_or_404(Post, sno=post_sno)

    if request.user != post.author:
        logger.warning(f"Unauthorized edit attempt by user: {request.user.username}")
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("blogHome")

    if request.method == "POST":
        logger.info(f"Processing edit for post ID: {post_sno}")
        post.title = request.POST.get("title", "").strip()
        post.content = request.POST.get("content", "").strip()

        if not post.title or not post.content:
            logger.warning(f"User attempted to edit post ID: {post_sno} with empty fields.")
            messages.error(request, "Title and content cannot be empty.")
            return redirect("editPost", post_id=post.sno)

        post.save()
        logger.info(f"Post ID: {post_sno} updated successfully.")
        messages.success(request, "Your post has been updated successfully.")
        return redirect("blogPost", slug=post.slug)

    context = {"post": post}
    return render(request, "blog/edit_post.html", context)

# Delete a post
@login_required
def deletePost(request, post_sno):
    logger.info("11111111111111")

    
    post = get_object_or_404(Post, sno=post_sno)

    if request.user != post.author:
        logger.warning(f"Unauthorized delete attempt by user: {request.user.username}")
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("blogHome")

    logger.info(f"Deleting post ID: {post_sno}")
    post.delete()
    messages.success(request, "Your post has been deleted successfully.")
    return redirect("blogHome")

def deleteComment(request, comment_sno):
    comment = get_object_or_404(BlogComment, sno=comment_sno)  # Use sno instead of id

    if request.user != comment.user:
        logger.warning(f"Unauthorized delete attempt by user: {request.user.username}")
        messages.error(request, "You are not authorized to delete this comment.")
        return redirect("blogHome")

    logger.info(f"Deleting comment SNO: {comment_sno}")
    post_slug = comment.post.slug  # Store slug before deleting
    comment.delete()
    messages.success(request, "Your comment has been deleted successfully.")
    return redirect("blogPost", slug=post_slug)

@login_required
def likePost(request, post_sno):
    post = get_object_or_404(Post, sno=post_sno)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.success(request, "You unliked this post.")
    else:
        post.likes.add(request.user)
        messages.success(request, "You liked this post.")

    return redirect("blogPost", slug=post.slug)