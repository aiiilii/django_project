from django.shortcuts import render, HttpResponse, redirect, render_to_response

from django.contrib import messages

from login.models import User, Post, Comment, Relationship, RELATIONSHIP_FOLLOWING, Category

from django.core.paginator import Paginator

from django.core.files.storage import FileSystemStorage

import bcrypt
import datetime, calendar
import time

import login.urls

# Create your views here.
def index(request):
    posts = Post.objects.all()

    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        "posts": posts,
    }
    return render(request, "home.html", context)

def view_post(request, postid):
    # post = Post.objects.get(id=postid)
    # post.views += 1
    # post.save()
    # comments = Comment.objects.all()
    if "userid" in request.session:
        post = Post.objects.get(id=postid)
        comments = Comment.objects.all()

        if 'viewed' not in request.session:
            request.session["viewed"] = {}
        if str(postid) not in request.session["viewed"]:
            request.session["viewed"][str(postid)] = True
            request.session.modified = True
            post.views += 1
            post.save()

        context = {
            'post': post,
            'comments': comments,
            'user': User.objects.get(id=request.session["userid"]),
        }
        return render(request,'view_post.html', context)
    else:
        post = Post.objects.get(id=postid)
        comments = Comment.objects.all()

        if 'viewed' not in request.session:
            request.session["viewed"] = {}
        if str(postid) not in request.session["viewed"]:
            request.session["viewed"][str(postid)] = True
            request.session.modified = True
            post.views += 1
            post.save()

        context = {
            'post': post,
            'comments': comments,
        }
        return render(request,'view_post.html', context)

def add_post(request):
    if not "userid" in request.session:
        messages.error(request, "Please login to share.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))

    if request.method == "POST":

        print("*" *20)
        print(request.POST)

        categories = request.POST.getlist('category')
        categories = list(filter(None, categories))
        errors2 = Post.objects.basic_validator(request.POST, categories)
        if len(errors2) > 0:
            for key, value in errors2.items():
                messages.error(request, value)
        else:
            print("*" *60)
            print(request.POST.getlist("category"))
            print(request.POST.get("category"))
            # category='\n'.join(request.POST.getlist("category"))
            uploaded_file_url = None
            if 'myfile' in request.FILES:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()
                filename = fs.save("app1/static/uploads/"+ myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
            # 'uploaded_file_url': uploaded_file_url
            print("*********", uploaded_file_url)
            if uploaded_file_url:
                uploaded_file_url = uploaded_file_url[4:]
            p = Post.objects.create(title=request.POST["title"], picture=uploaded_file_url, content=request.POST["content"], views=0, uploaded_by=User.objects.get(id=request.session["userid"]))

            for v in categories:
                print("*" *40)
                print(Category.objects.filter(title=v))
                print(type(Category.objects.filter(title=v)))
                if not Category.objects.filter(title=v).exists():
                    print("*" *20, "in if")
                    c = Category.objects.create(title=v)
                    p.category.add(c)
                    p.save()
                else:
                    print("*" *20, "in else")
                    c = Category.objects.get(title=v)
                    p.category.add(c)
                    p.save()
            messages.success(request, "Successfully shared!")
            return redirect("/")
    context = {
            "user": User.objects.get(id=request.session["userid"]),
    }
    return render(request, "add_post.html", context)

def edit_post(request, postid):
    if not "userid" in request.session:
        messages.error(request, "Please log in to edit.")
        return redirect("/")

    if request.method == "POST":
        errors2 = Post.objects.basic_validator2(request.POST)
        if len(errors2) > 0:
                for key, value in errors2.items():
                    messages.error(request, value)
        else:
            print(request.POST["title"])
            p = Post.objects.get(id=postid)
            p.title = request.POST["title"]
            p.content = request.POST["content"]
            p.save()
            messages.success(request, "Successfully updated!")
            return redirect("/")

    context = {
            "user": User.objects.get(id=request.session["userid"]),
            "post": Post.objects.get(id=postid),
        }
    return render(request, "edit_post.html", context)

def add_comment(request, postid):
    if not "userid" in request.session:
        messages.error(request, "Please login to comment.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    print("*" *40)
    print(request.POST)
    
    errors3 = Comment.objects.basic_validator(request.POST)
    if len(errors3) > 0:
        for key, value in errors3.items():
            messages.error(request, value)
            return redirect("/view/"+str(postid))
    else:
        if request.POST["content"]:
            Comment.objects.create(content=request.POST["content"], post=Post.objects.get(id=request.POST["postid"]), user=User.objects.get(id=request.session["userid"]))
        return redirect("/view/"+str(postid))
    # context = {
    #         "user": User.objects.get(id=request.session["userid"]),
    #         "post": Post.objects.get(id=postid),
    #     }
    # return redirect("/view/"+str(postid))

def like_post(request, postid):
    if not "userid" in request.session:
        messages.error(request, "Please login to like posts.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    p = Post.objects.get(id=postid)
    u = User.objects.get(id=request.session["userid"])
    p.users_who_like.add(u)
    p.save()
    return redirect("/view/"+ str(postid))

def unlike_post(request, postid):
    if not "userid" in request.session:
        messages.error(request, "You are not logged in.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    
    p = Post.objects.get(id=postid)
    u = User.objects.get(id=request.session["userid"])
    p.users_who_like.remove(u)
    p.save()
    return redirect("/view/"+ str(postid))

def like_comment(request, postid, commentid):
    if not "userid" in request.session:
        messages.error(request, "Please login to comments.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    c = Comment.objects.get(id=commentid)
    u = User.objects.get(id=request.session["userid"])
    c.users_who_like.add(u)
    c.save()
    return redirect("/view/"+ str(postid))

def unlike_comment(request, postid, commentid):
    if not "userid" in request.session:
        messages.error(request, "You are not logged in.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    
    c = Comment.objects.get(id=commentid)
    u = User.objects.get(id=request.session["userid"])
    c.users_who_like.remove(u)
    c.save()
    return redirect("/view/"+ str(postid))

def delete_post(request, postid):
    if not "userid" in request.session:
        messages.error(request, "You are not logged in.")
        return redirect("/")
    
    Post.objects.get(id=postid).delete()
    messages.success(request, "Successfully deleted post!")
    return redirect("/")

def delete_comment(request, postid, commentid):
    if not "userid" in request.session:
        messages.error(request, "You are not logged in.")
        return redirect("/")
    
    p = Post.objects.get(id=postid).id
    Comment.objects.get(id=commentid, post_id=p).delete()
    messages.success(request, "Successfully deleted comment!")
    return redirect("/view/"+ str(postid))

def profile(request, userid):
    context = {
            "user": User.objects.get(id=userid),
    }
    return render(request, 'profile.html', context)


def add_relationship(request, userid):
    u = User.objects.get(id=userid)
    m = User.objects.get(id=request.session["userid"])
    relationship = Relationship.objects.create(from_person=m, to_person=u, status=1)
    return redirect("/")

def remove_relationship(request, userid):
    u = User.objects.get(id=userid)
    m = User.objects.get(id=request.session["userid"])
    Relationship.objects.get(from_person=m, to_person=u, status=1).delete()
    return redirect("profile/"+ str(userid))

def get_relationships(status):
    return relationships.filter(to_people__status=status, to_people__from_person=self)

def get_related_to(status):
    return related_to.filter(from_people__status=status, from_people__to_person=self)

def get_following():
    return get_relationships(RELATIONSHIP_FOLLOWING)

def get_followers():
    return get_related_to(RELATIONSHIP_FOLLOWING)