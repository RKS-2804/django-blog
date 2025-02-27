from django.shortcuts import render, HttpResponse, redirect
from home import views
from home.models import Contact
from django.contrib.auth.models import User
from django.contrib.auth  import authenticate,  login, logout
from django.contrib import messages
from Blog.models import Post 
import logging

#configure logging
logger= logging.getLogger("django.auth")

def home(request):
    """Render the home page with top 2 most liked post."""

    logger.info("Home page accesed")
    featured_posts = Post.objects.all().order_by("likes")[:2]
    return render(request, 'home/home.html', {"featured_posts": featured_posts})

def contact(request):
    """
    Handle contact form submissions.
    If the form data is invalid, an error message will pop up.

    """
    if request.method=='POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        content = request.POST['content']

        logger.info("Contact form submited: Name=%s, Email=%s", name, email)
        
        if len(name)<2 or len(email)<3 or len(phone)<10 or len(content)<2:
            messages.error(request, "Please fill the form correctly.")
            logger.warning("Invalid contact form submission.")
            
        else:
            contact = Contact(name=name, email=email, phone=phone, content=content)
            contact.save()
            messages.success(request, "Your message has been sent successfully.")
            logger.info("Contact form successfully saved.")

    return render(request, 'home/contact.html')

def about(request):
    """Render the about page"""
    return render(request, 'home/about.html')

def search(request):
    """
    Perform a search across blog post by tittle, author , or content.
    Return a warning message if no results are found.
    """
    query=request.GET['query']
    logger.info("search initiated: Query=%s", query)

    if len(query)>78:
        allPosts=Post.objects.none()
    else:
        allPostsTitle= Post.objects.filter(title__icontains=query)
        allPostsAuthor= Post.objects.filter(author__username__icontains=query)
        allPostsContent= Post.objects.filter(content__icontains=query)
        allPosts= allPostsTitle.union(allPostsContent, allPostsAuthor)

    if allPosts.count()==0:
        messages.warning(request, "No search results found. Please refine your query.")
        logger.warning("No search result for query: %s", query)
    params={'allPosts': allPosts, 'query': query}

    return render(request, 'home/search.html', params)

def handleSignUp(request):
    """
    Handle user registrataion. Validate inpute before creating a user.
    """
    if request.method=="POST":
        # Get the post parameters
        username=request.POST['username']
        email=request.POST['email']
        fname=request.POST['fname']
        lname=request.POST['lname']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        logger.info("Sign up attepmt: Username=%s, Email=%s", username, email)
        
        # check for errorneous input
        if len(username)>10:
            messages.error(request, " Your user name must be under 10 characters")
            logging.warning("Username too long: %s", username)
            return redirect('home')

        elif not username.isalnum():
            messages.error(request, " Enter the username")
            logger.warning("Invalid Username: %s", username)
            return redirect('home')
        
        elif (pass1!= pass2):
             messages.error(request, " Passwords do not match")
             logger.warning("Password missmatch for user: %s", username)
             return redirect('home')
        
        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name= fname
        myuser.last_name= lname
        myuser.save()
        messages.success(request, " Your EchoThoughts has been successfully created")
        logger.info("User successfully created: %s", username)
        return redirect('home')

    else:
        return HttpResponse("404 - Not found")
    
def handeLogin(request):
    """
    Handle user authentication and login
    """
    if request.method=="POST":
        # Get the post parameters
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']

        logger.info("Login attempt: Username=%s", loginusername)

        user=authenticate(username= loginusername, password= loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            logger.info("User logged in successfully: %s", loginusername)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials! Please try again")
            logging.info("Failed login attempt: %s", loginusername)
            return redirect("home")

    return HttpResponse("404- Not found")

def handelLogout(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, "Successfully logged out")
    logging.info("User logout successfully.")
    return redirect('home')

    
