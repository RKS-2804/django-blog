import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from Blog.models import Post
from Blog.views import *
from home.models import Contact


@pytest.mark.django_db
class TestHomeViews:
    """Test case suite for the home application views"""

    @pytest.fixture
    def create_user(self):
        """Fixture to create a test user."""
        return User.objects.create_user(username="testuser", email="test@example.com", password="password123")

    @pytest.fixture
    def create_post(self, create_user):
        """Fixture to create a test blog post."""
        return Post.objects.create(title="Sample Post", content="This is a test content.", author=create_user)

    def test_home_view(self, client):
        """Positive test case: Ensure home page loads successfully."""
        response = client.get(reverse("home"))
        assert response.status_code == 200
        assert "featured_posts" in response.context

    def test_contact_form_valid(self, client):
        """Positive test case: Ensure contact form submits successfully."""
        response = client.post(reverse("contact"), {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "content": "Test message"
        })
        assert response.status_code == 200
        assert Contact.objects.count() == 1

    def test_contact_form_invalid(self, client):
        """Negative test case: Ensure form fails on invalid input."""
        response = client.post(reverse("contact"), {
            "name": "",
            "email": "a@b",
            "phone": "123",
            "content": ""
        })
        assert response.status_code == 200
        assert Contact.objects.count() == 0

    def test_search_valid_query(self, client, create_post):
        """Positive test case: Search should return results."""
        response = client.get(reverse("search") + "?query=Sample")
        assert response.status_code == 200
        assert create_post in response.context["allPosts"]

    def test_search_invalid_query(self, client):
        """Negative test case: Search should return no results."""
        response = client.get(reverse("search") + "?query=nonexistent")
        assert response.status_code == 200
        assert response.context["allPosts"].count() == 0

    def test_handle_sign_up(self, client):
        """Positive test case: Ensure user registration works."""
        response = client.post(reverse("handleSignUp"), {
            "username": "newuser",
            "email": "new@example.com",
            "fname": "New",
            "lname": "User",
            "pass1": "password123",
            "pass2": "password123"
        })
        assert response.status_code == 302  # Redirect to home
        assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
class TestBlogViews:
    """Test cases for Blog views"""

    @pytest.fixture
    def create_user(self):
        """Fixture to create a test user."""
        return User.objects.create_user(username="testuser", email="test@example.com", password="password123")

    @pytest.fixture
    def create_post(self, create_user):
        """Fixture to create a test blog post."""
        return Post.objects.create(title="Test Post", content="This is test content.", slug="test-post", author=create_user)

    def test_blog_home_view(self, client, create_post):
        """Ensure blog home page loads successfully."""
        response = client.get(reverse("blogHome"))
        assert response.status_code == 200
        assert "allPosts" in response.context
        assert create_post in response.context["allPosts"]

    def test_blog_home_view_no_posts(self, client):
        """Ensure blog home works when no posts exist."""
        response = client.get(reverse("blogHome"))
        assert response.status_code == 200
        assert len(response.context["allPosts"]) == 0

    def test_blog_post_view(self, client, create_post):
        """Ensure blog post loads successfully."""
        response = client.get(reverse("blogPost", kwargs={"slug": create_post.slug}))
        assert response.status_code == 200
        assert response.context["post"] == create_post

    def test_blog_post_view_invalid_slug(self, client):
        """Ensure 404 error when post slug is invalid."""
        response = client.get(reverse("blogPost", kwargs={"slug": "invalid-slug"}))
        assert response.status_code == 404

    def test_post_comment_authenticated(self, client, create_user, create_post):
        """Ensure an authenticated user can comment."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("postComment"), {
            "comment": "This is a test comment.",
            "postSno": create_post.sno
        })
        assert response.status_code == 302
        assert BlogComment.objects.filter(post=create_post).exists()

    def test_post_comment_unauthenticated(self, client, create_post):
        """Ensure unauthenticated user cannot comment."""
        response = client.post(reverse("postComment"), {
            "comment": "This is a test comment.",
            "postSno": create_post.sno
        })
        assert response.status_code == 302
        assert BlogComment.objects.count() == 0

    def test_post_comment_empty(self, client, create_user, create_post):
        """Ensure comment cannot be empty."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("postComment"), {
            "comment": "",
            "postSno": create_post.sno
        })
        assert response.status_code == 302
        assert BlogComment.objects.count() == 0

    def test_create_post_authenticated(self, client, create_user):
        """Ensure an authenticated user can create a post."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("createPost"), {
            "title": "New Post",
            "content": "Content of the new post",
            "slug": "new-post"
        })
        assert response.status_code == 302
        assert Post.objects.filter(slug="new-post").exists()

    def test_create_post_unauthenticated(self, client):
        """Ensure unauthenticated users cannot create posts."""
        response = client.post(reverse("createPost"), {
            "title": "New Post",
            "content": "Content of the new post",
            "slug": "new-post"
        })
        assert response.status_code == 302
        assert Post.objects.count() == 0

    def test_edit_post_authorized(self, client, create_user, create_post):
        """Ensure post author can edit their post."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("editPost", kwargs={"post_sno": create_post.sno}), {
            "title": "Updated Title",
            "content": "Updated Content"
        })
        assert response.status_code == 302
        create_post.refresh_from_db()
        assert create_post.title == "Updated Title"

    def test_edit_post_unauthorized(self, client, create_post):
        """Ensure unauthorized users cannot edit a post."""
        another_user = User.objects.create_user(username="anotheruser", password="password123")
        client.login(username="anotheruser", password="password123")
        response = client.post(reverse("editPost", kwargs={"post_sno": create_post.sno}), {
            "title": "Updated Title",
            "content": "Updated Content"
        })
        assert response.status_code == 302
        create_post.refresh_from_db()
        assert create_post.title != "Updated Title"

    def test_delete_post_authorized(self, client, create_user, create_post):
        """Ensure post author can delete their post."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("deletePost", kwargs={"post_sno": create_post.sno}))
        assert response.status_code == 302
        assert not Post.objects.filter(sno=create_post.sno).exists()

    def test_delete_post_unauthorized(self, client, create_post):
        """Ensure unauthorized users cannot delete a post."""
        another_user = User.objects.create_user(username="anotheruser", password="password123")
        client.login(username="anotheruser", password="password123")
        response = client.post(reverse("deletePost", kwargs={"post_sno": create_post.sno}))
        assert response.status_code == 302
        assert Post.objects.filter(sno=create_post.sno).exists()

    def test_like_post_authenticated(self, client, create_user, create_post):
        """Ensure authenticated user can like a post."""
        client.login(username="testuser", password="password123")
        response = client.post(reverse("likePost", kwargs={"post_sno": create_post.sno}))
        assert response.status_code == 302
        assert create_user in create_post.likes.all()

    def test_like_post_unauthenticated(self, client, create_post):
        """Ensure unauthenticated users cannot like a post."""
        response = client.post(reverse("likePost", kwargs={"post_sno": create_post.sno}))
        assert response.status_code == 302
        assert create_post.likes.count() == 0
