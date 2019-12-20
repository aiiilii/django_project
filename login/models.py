from __future__ import unicode_literals
from django.db import models
# from django.db.models import CharField, Model
# from django_mysql.models import ListCharField

import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}')

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        # add keys and values to errors dictionary for each invalid field
        if len(postData["first_name"]) < 2:
            errors["first_name"] = "First name should be at least 2 characters"
        if len(postData["last_name"]) < 2:
            errors["last_name"] = "Last name should be at least 2 characters"
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = ("Invalid email address!")
        if not PASSWORD_REGEX.match(postData["password"]):
            errors["password"] = "Password should be at least 8 characters, with 1 number, 1 uppercase and 1 lowercase."
        if postData["password"] != postData["confirm_password"]:
            errors["password_match"] = "Passwords do not match!"
        return errors

class PostManager(models.Manager):
    def basic_validator(self, postData, categories):
        errors2 = {}
        if len(postData["title"]) < 5:
            errors2["title"] = "Title must be over 5 characters"
        if len(postData["content"]) < 10:
            errors2["content"] = "Post content must be over 10 characters"
        if len(categories) < 1:
            errors2["category"] = "Must have at least 1 category"
        return errors2
    def basic_validator2(self, postData):
        errors2 = {}
        if len(postData["title"]) < 5:
            errors2["title"] = "Title must be over 5 characters"
        if len(postData["content"]) < 10:
            errors2["content"] = "Post content must be over 10 characters"
        return errors2

class CommentManager(models.Manager):
    def basic_validator(self, postData):
        errors3 = {}
        if len(postData["content"]) < 2:
            errors3["content"] = "Comment content must be over 3 characters"
        return errors3

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    #post_uploaded
    #user_comment

    def __unicode__(self):
        return self.name

RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
)

class Relationship(models.Model):
    from_person = models.ForeignKey(User, related_name='from_people', on_delete = models.CASCADE)
    to_person = models.ForeignKey(User, related_name='to_people', on_delete = models.CASCADE)
    status = models.IntegerField(choices = RELATIONSHIP_STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    uploaded_by = models.ForeignKey(User, related_name="post_uploaded", on_delete = models.CASCADE)
    views = models.IntegerField(null=True)
    picture = models.FileField(upload_to='static/uploads/', null=True)
    users_who_like = models.ManyToManyField(User, related_name="liked_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostManager()
    #post_comments
    # class Meta:
    #     ordering=['date']

class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, related_name="post_comments", on_delete = models.CASCADE)
    user = models.ForeignKey(User, related_name="user_comments", on_delete = models.CASCADE)
    users_who_like = models.ManyToManyField(User, related_name="liked_comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CommentManager()

class Category(models.Model):
    title = models.CharField(max_length=255)
    post = models.ManyToManyField(Post, related_name="category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
