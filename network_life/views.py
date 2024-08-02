import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from taggit.models import Tag

from .forms import PostForm, CreateUserForm, ImageForm, ProfilePageForm
from .models import ProfilePage, Post, Image, Followers
from .tokens import account_activation_token

LOGIN_PAGE_URL = 'network_life:login'
HOME_PAGE_URL = 'network_life:home'


@login_required(login_url=LOGIN_PAGE_URL)
def home(request):
    posts = Post.objects.all()[::-1]
    avatar = ProfilePage.objects.get(pk=request.user.id)
    tags = Tag.objects.all()

    context = {'posts': posts, 'avatar': avatar.avatar, 'tags': tags}
    return render(request, 'home.html', context)


@login_required(login_url=LOGIN_PAGE_URL)
def like_unlike_post(request, post_id):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            post = get_object_or_404(Post, id=post_id)

            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True

            posts = Post.objects.filter(id=request.POST.get('post_id'), user=request.user)
            for el in posts:
                data = {
                    'value': liked,
                    'amount_likes': el.likes.count()
                }
                return JsonResponse(data)

    return redirect(HOME_PAGE_URL)


@login_required(login_url=LOGIN_PAGE_URL)
def post(request, id):
    product = Post.objects.get(id=id)
    images = Image.objects.filter(post=product)
    post = Post.objects.get(id=id)

    avatar = ProfilePage.objects.get(pk=request.user.id)

    tags = Tag.objects.all()

    context = {'post': post, 'images': images, 'main_image': product.main_image, 'avatar': avatar.avatar, 'tags': tags}
    return render(request, 'post.html', context)


@login_required(login_url=LOGIN_PAGE_URL)
def create_post(request):
    post_form = PostForm()
    image_form = ImageForm()

    if request.method == 'POST':
        files = request.FILES.getlist('images')

        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.name = request.user.username
            post.preview = post.main_image
            post.date_published = datetime.datetime.now()
            post.save()
            post_form.save_m2m()
            messages.success(request, 'Post created successfully')

            for file in files:
                Image.objects.create(post=post, images=file)

            return redirect(HOME_PAGE_URL)

    avatar = ProfilePage.objects.get(pk=request.user.id)
    context = {'p_form': post_form, 'i_form': image_form, 'avatar': avatar.avatar}
    return render(request, 'create.html', context)


def register_page(request):
    if request.user.is_authenticated:
        return redirect(HOME_PAGE_URL)
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # save form in the memory not in database
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Sending e-mail to mail
            current_site = get_current_site(request)  # get current site
            mail_subject = 'Activate your user account'
            message = render_to_string('registration/acc_activate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')  # get email address on what send confirmation letter
            email = EmailMultiAlternatives(mail_subject, message, to=[to_email])
            email.attach_alternative(message, 'text/html')
            email.send()
            messages.info(request, f'Please confirm your email address to complete the registration')
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = CreateUserForm()
    return render(request, 'registration/register.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect(HOME_PAGE_URL)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(HOME_PAGE_URL)
            else:
                messages.info(request, 'Username or password is incorrect!')

        return render(request, 'registration/login.html')


def login_via_accounts(request):
    try:
        ProfilePage.objects.get(pk=request.user.id)
        return redirect(HOME_PAGE_URL)

    except ProfilePage.DoesNotExist:
        new_prof = ProfilePage.objects.create(username=str(request.user))
        new_prof.save()
        return redirect(HOME_PAGE_URL)


def logout_user(request):
    logout(request)
    return redirect(LOGIN_PAGE_URL)


# activate account via link
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f'You have successfully registered. Sign In to your account.')
        return redirect(HOME_PAGE_URL)
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url=LOGIN_PAGE_URL)
def profile(request, username):
    # get all posts
    posts = Post.objects.filter(name=username).all()[::-1]
    # get some data from ProfilePage Table
    data = ProfilePage.objects.get(username=username)

    # get data from Follower Table by a username
    if Followers.objects.filter(user=request.user, follow_to=username, username=request.user.username).first():
        text = 'Unfollow'
    else:
        text = 'Follow'

    followers_amount = len(Followers.objects.filter(username=username))
    following_amount = len(Followers.objects.filter(follow_to=username))

    context = {
        'posts': posts,
        'avatar': data.avatar,
        'username': data.username,
        'amount_posts': len(posts),
        'button_text': text,
        'followers_amount': followers_amount,
        'following_amount': following_amount,
    }
    return render(request, 'profile.html', context)


@login_required(login_url=LOGIN_PAGE_URL)
def update_profile(request):
    username = request.GET.get('user')
    obj = ProfilePage.objects.get(username=username)
    if request.method == 'POST':
        form = ProfilePageForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect(f'/profile/{username}')
    else:
        form = ProfilePageForm(instance=obj)

    avatar = ProfilePage.objects.get(pk=request.user.id)
    context = {'form': form, 'avatar': avatar.avatar, 'current_user': username}
    return render(request, 'update_profile.html', context)


@login_required(login_url=LOGIN_PAGE_URL)
def follow(request, follower, user):
    if request.method == 'POST':
        # if you already FOLLOW and want more,-> then delete
        if Followers.objects.filter(user=request.user, follow_to=follower, username=user).first():
            delete_follower = Followers.objects.get(user=request.user, follow_to=follower, username=user)
            delete_follower.delete()
            messages.success(request, f'You have just unfollowed from {follower}')
            return redirect(f'/profile/{follower}')

        # if for the first time
        else:
            new_follower = Followers.objects.create(user=request.user, follow_to=follower, username=user)
            new_follower.save()
            messages.success(request, f'You have just followed with {follower}')
            return redirect(f'/profile/{follower}')
    else:
        return redirect(HOME_PAGE_URL)


@login_required(login_url=LOGIN_PAGE_URL)
def following_accounts(request, username):
    data = ProfilePage.objects.get(username=username)
    following = Followers.objects.filter(username=username).all()
    context = {
        'following': following,
        'avatar': data.avatar,
    }
    return render(request, 'following_accounts.html', context)


@login_required(login_url=LOGIN_PAGE_URL)
def followers_accounts(request, username):
    data = ProfilePage.objects.get(username=username)
    followers = Followers.objects.filter(follow_to=username).all()
    context = {
        'followers': followers,
        'avatar': data.avatar,
    }
    return render(request, 'followers_accounts.html', context)
