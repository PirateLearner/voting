'''
Created on 01-May-2015

@author: craft
'''
from rest_framework import serializers

from voting.models import Vote, UPVOTE, DOWNVOTE

from blogging.models import BlogContent
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType


from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
import json

ZERO_VOTES_ALLOWED = getattr(settings, 'VOTING_ZERO_VOTES_ALLOWED', False)

class UserSerializer(serializers.ModelSerializer):
    
    voted = serializers.PrimaryKeyRelatedField(many=True, queryset=Vote.objects.all())
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'voted',)
        
        
class AnonymousUserSerializer(serializers.Serializer):
    username = serializers.CharField();


class BlogContentSerializer(serializers.ModelSerializer):
    #Tell BlogContent that it has a relation on Annotations    
    vote = serializers.SerializerMethodField()
    uservote = serializers.SerializerMethodField()
    #annotation = SerializeAnnotationsField()
    
    class Meta:
        model = BlogContent
        fields =('id', 'title', 'create_date', 'data', 'url_path', 
                 'author_id', 'published_flag', 'section', 'content_type',
                 'vote', 'uservote',)
     
    def get_vote(self, obj):
        vote = Vote.objects.get_score(obj)
        if vote is not None:
            return vote        
        else:
            return None 
        
    def get_uservote(self, obj):        
        user = self.context['request'].user
        vote = Vote.objects.get_for_user(obj, user)
        #uservote = {'user': UserSerializer(user),
        #            'vote': json.dumps(Vote.objects.get_for_user(obj, user))
        #            }
        return (VoteSerializer(vote).data)
               

class VoteSerializer(serializers.ModelSerializer):
    
    voter = UserSerializer(read_only=True)
    
    class Meta:
        model = Vote
        fields = (
                  'id', 'voter', 'vote', 'vote_modified', 'content_type', 'object_id',
                  )
    
    def create(self, validated_data):        
        vote = Vote()
        vote.voter = validated_data.get('voter')
        vote.vote = validated_data.get('vote')
        vote.content_type = validated_data.get('content_type')
        vote.object_id = validated_data.get('object_id')
        
        #Get row from contentType which has content_type
        content_object = ContentType.objects.get_for_id(vote.content_type.id)
        
        vote.content_object = content_object.model_class().objects.get(id=vote.object_id)
                        
        """
        Record a user's vote on a given object. Only allows a given user
        to vote once, though that vote may be changed.
        
        A zero vote indicates that any existing vote should be removed.
        """
        if vote.vote not in (+1, 0, -1):
            raise ValueError('Invalid vote (must be +1/0/-1)')
        
        # First, try to fetch the instance of this row from DB
        # If that does not exist, then it is the first time we're creating it
        # If it does, then just update the previous one
        try:
            vote_obj = Vote.objects.get(voter=vote.voter, content_type=vote.content_type, object_id=vote.object_id)
            if vote == 0 and not ZERO_VOTES_ALLOWED:
                vote_obj.delete()
            else:
                vote_obj.vote = vote
                vote_obj.save()
                
        except ObjectDoesNotExist:
            #This is the first time we're creating it
            try:
                if not ZERO_VOTES_ALLOWED and vote == 0:
                    # This shouldn't be happening actually
                    return
                vote_obj = Vote.objects.create(voter=vote.voter, content_type=vote.content_type, object_id=vote.object_id, vote=vote.vote)                        
            except:
                print '{file}: something went wrong in creating a vote object at {line}'.format(file=str('__FILE__'), line=str('__LINE__'))
                raise ObjectDoesNotExist    
        
        return vote_obj
    
    def update(self, instance, validated_data):
        vote = instance
                
        vote.voter = validated_data.get('voter', vote.voter)
        
        vote.vote += validated_data.get('vote', vote.vote)
          
        vote.content_type = validated_data.get('content_type',vote.content_type)
        vote.object_id = validated_data.get('object_id',vote.object_id)

        if vote.vote is not 0:
            vote.vote = vote.vote/abs(vote.vote)
        vote.save()
                
        return vote