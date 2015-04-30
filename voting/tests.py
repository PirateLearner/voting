from django.test import TestCase

from voting.models import Vote
from blogging.models import BlogContent
from django.test.client import RequestFactory

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
# Create your tests here.

class VotingTests(TestCase):
    
    fixtures = ['fixtures.json',]
    
    def setUp(self, *args, **kwargs):
        #create 2 new users
        #load the blogging post into a variable
        self.factory = RequestFactory()
        self.author = User.objects.get(pk="1")
        self.user1 = User.objects.create_user(username="User1", email="user1@users.com", password="user1")
        self.article = BlogContent.objects.get(pk="1")
        
    
    def tearDown(self):
        self.user1.delete()
        
    def test_vote_model(self):
        vote = Vote()
        vote.object_id = self.article._get_pk_val()
        vote.content_type = ContentType.objects.get_for_model(self.article)
        vote.content_object = ContentType.objects.get_for_model(self.article)
        
        vote.voter = self.user1
        vote.vote = +1
        
        vote.save()
        
        vote_obj = Vote.objects.all()[0]
        self.assertEqual(vote_obj._get_pk_val(), vote._get_pk_val(), "Primary Keys do not match")
        
        
    def test_load_votes(self):
        pass
    
    def test_upvote(self):
        pass
    
    def test_downvote(self):
        pass
    
    def test_vote_on_own_post(self):
        pass
    
    def test_get_votes_by_user(self):
        pass
    
    def test_get_score(self):
        pass
    
    def test_get_upvotes(self):
        pass
    
    def test_get_downvotes(self):
        pass
    
    def test_get_user_vote(self):
        pass
    
    def test_get_top_rated_posts(self):
        pass
    
    def test_get_most_downvoted_posts(self):
        pass
       
    