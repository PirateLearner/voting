from django.test import TestCase

from voting.models import Vote
from blogging.models import BlogContent

# Create your tests here.

class VotingTests(TestCase):
    
    fixtures = ['fixtures.json',]
    
    def setUp(self, *args, **kwargs):
        pass
    
    def tearDown(self):
        pass
    
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
       
    