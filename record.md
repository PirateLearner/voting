1. **Create Virtual Environment**
     virtualenv voting --no-site-packages

2. **Install dependencies**

    ```
    Django==1.6.8
	Django-Select2==4.2.2
    Pillow==2.7.0
	South==1.0.2
	argparse==1.2.1
	beautifulsoup4==4.3.2
	django-ckeditor==4.4.4
	django-classy-tags==0.4
	django-crispy-forms==1.4.0
	django-filer==0.9.5
	django-mptt==0.6.0
	django-polymorphic==0.6.1
	django-reversion==1.8.5
	django-sekizai==0.7
	django-taggit==0.12.2
	djangorestframework==3.1.0
	easy-thumbnails==2.2
	html5lib==1.0b1
	lxml==3.4.1
	pi-blogging==0.1.0b1
	selenium==2.44.0
	six==1.3.0
	wsgiref==0.1.2
    ```

3. **Start project**
	```
	django-admin.py startproject voting_demo
	```

4. **Configure Project settings**
   
   In settings, add a `PROJECT_PATH` setting as:
   
   ```
   PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
   ```

   and, to the `INSTALLED_APPS`, add:
   
   ```
   ...
    'blogging',
    'mptt',
    'sekizai',
    'reversion',
    'django_select2',
    'easy_thumbnails',
    'filer',
    'taggit',
    'crispy_forms',
    'ckeditor',
    'annotations',
    'rest_framework',
    'rest_framework.authtoken'
    ```
   
   and at the end of the file:
   
   ```   
	TEMPLATE_CONTEXT_PROCESSORS = (
	    'django.contrib.auth.context_processors.auth',
	    'django.contrib.messages.context_processors.messages',
	    'django.core.context_processors.i18n',
	    'django.core.context_processors.debug',
	    'django.core.context_processors.request',
	    'django.core.context_processors.media',
	    'django.core.context_processors.csrf',
	    'django.core.context_processors.tz',
	    'sekizai.context_processors.sekizai',
	    'django.core.context_processors.static',
	)
	
	TEMPLATE_DIRS = (
	    os.path.join(PROJECT_PATH, "templates"),
	)
	
	MEDIA_ROOT = PROJECT_PATH+'/media'
	MEDIA_URL = '/media/'
	
	STATICFILES_DIRS = (
	    # Put strings here, like "/home/html/static" or "C:/www/django/static".
	    # Always use forward slashes, even on Windows.
	    # Don't forget to use absolute paths, not relative paths.
	    PROJECT_PATH+"/static",
	)
	
	MPTT_ADMIN_LEVEL_INDENT = 20
	
	
	THUMBNAIL_ALIASES = {
	    '': {
	        'teaser': {'size': (50, 50), 'crop': True},
	    },
	}
	CKEDITOR_UPLOAD_PATH = 'images/'
	CKEDITOR_CONFIGS = {
	    'default': {
	        'toolbar': 'Full',
	        'justifyClasses': [ 'AlignLeft', 'AlignCenter', 'AlignRight', 'AlignJustify' ],
	    },
	}
	
	CRISPY_TEMPLATE_PACK = 'bootstrap3'
	
	FIXTURE_DIRS = (
	                BASE_DIR+'/demo/fixtures',
	                )
	
	REST_FRAMEWORK = {
	    # Use hyperlinked styles by default.
	    # Only used if the `serializer_class` attribute is not set on a view.
		#    'DEFAULT_MODEL_SERIALIZER_CLASS':
		#        'rest_framework.serializers.HyperlinkedModelSerializer',
	
	    # Use Django's standard `django.contrib.auth` permissions,
	    # or allow read-only access for unauthenticated users.
	    'DEFAULT_PERMISSION_CLASSES': [
	        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
	    ]
	}
   ```

5. Start app `voting` : `python manage.py startapp voting`

6. Models Design: What would we like?
	
	* User can upvote a post
	* User can downvote a post
	* User may revert back from upvote to no-vote (and consequently to downvote also)
	* User can see all the posts he's voted on
	* User can see total number of upvotes and downvotes on the post
	* User can sort posts based on their score, in ascending or descending order
	
	At the center of this all, there is a user, and there is a record of whether the user upvoted or downvoted on an object (post)
	Since the object could be anything, a blogpost, a question, a comment, or an annotation, a status update, a bookmark or any other kind
	of media that can be rated, there cannot be a close coupling between votes and the other kind of content object.
	
	Hence, we will employ Django's `generic foreign keys` for the purpose. A simple model which stores this relationship of
	
	a. User
	b. Content Object
	c. Rating (Upvote or Downvote)
	
	can be as follows:
	
	```
	class Vote(models.Model):
    
	    #The ID of the object on which vote was cast
	    content_type = models.ForeignKey(ContentType, verbose_name="Content Type", related_name="content_type_set_for_voting")
	    object_id = models.TextField(_("object ID"))
	    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")
	    
	    #Vote made by User
	    voter = models.ForeignKey(User, related_name="Voter")
	
	    #Vote value
	    vote = models.SmallIntegerField(choices=SCORES)
	    
	    vote_date = models.DateTimeField(auto_now_add=True)
	    vote_modified = models.DateTimeField(auto_now=True)
	  	    
	    def __unicode__(self):
	        return "Voting Statistics"
	    
	    def __str__(self):
	        return "Voting Statistics"
	    
	    class Meta:
	    	app_label = "voting"
	    	
	```
	
	### A note about this particular choice of data model:
	When I started to build this app (deciding to discard the Django-Voting app), I thought of the following theoretical data models:
	
	a. A table to store the overall statistics of votes on an object. So, it would contain a generic foreign key for the Content Object, and a field containing the
	total number of upvotes and downvotes on that field.
	
	So, it would have looked like:
	
	```
	class Vote(models.Model):
    
	    #The ID of the object on which vote was cast
	    content_type = models.ForeignKey(ContentType, verbose_name="Content Type", related_name="content_type_set_for_voting")
	    object_id = models.TextField(_("object ID"))
	    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")
	    
	    #Vote made by User
	    voter = models.ManyToManyField(User, through="vote_user_map", null=False, blank=False)
	
	    #Vote value
	    upvotes = models.PositiveIntegerField(default=0)
	    downvotes = models.PositiveIntegerField(default=0)
	```
	    
	The relationship between the users and the posts is a many to many field because a user may vote on many objects and many users may vote on a particular object.
	
	`through` table is required because we need to store what the user voted, upvote or downvote, so that we may forbid them from upvoting or downvoting more than once, 
	and keeping other ancilliary statistics like when did they first vote on it and when did they last modify it.
	
	A through table would have looked like:
	
	```
	class vote_user_map(models.Model):
		user = models.ForeignKey(User, related_name="Voter")
		vote= models.ForeignKey(Vote)
		
		vote_value = models.SmallIntegerField(choices=SCORES)
		
		vote_date = models.DateTimeField(auto_now_add=True)
	    vote_modified = models.DateTimeField(auto_now=True)
	```
	
	But then, I realized that this would be a wrong approach. Why? Because I am keeping statistical data in the DB, something that DB can calculate on its own when given a
	query. My bias stems from my affection for analytics which I've been trying to get my handles on in a self-made manner. However, I was able to correct myself with certain doubts. First was,
	do I really need an extra table *IN* this app? Or I could have a inclusive Analytics and Statistics app which uses data from all these apps and crunches the numbers? There's a general practice
	that I've learned to follow in all these years, _do not distribute until the consolidated method threatens to become inefficient_. 
	 
	The rule of the thumb is, as explained [here](http://programmers.stackexchange.com/questions/171024/never-do-in-code-what-you-can-get-the-sql-server-to-do-well-for-you-is-this):
	
	> “Never do in code what you can get the SQL server to do well for you”
	
	So, I fell back on to `django-voting` models (for they are more or less apt). What I would want though is, to not use Django Templates as a part of evolving methodology,
	but integrate `Django-Rest-Framework` with it. And continuing with the tradition that I am trying to make, Unit tests should accompany what we do.  

7. Load the `blogging` app fixtures and prepare the demo site (using the blogging demo as base). We will build upon it.

8. Let us try to create our first vote, in the unit test.
	
	So far, we've just written the models and nothing else. So, models and their methods are the first thing that we would like to test, before we write any view or serializers 
	for Django Rest Framework.
	
	### What would we want to test from current models and their manager?
	
	* User can _upvote_ or _downvote_ on a post
	* Fetch the total number of upvotes and downvotes on the post
	* Fetch the total number of votes on the post
	* Fetch the posts on which the user has voted on
	
	First, let us write a few methods that we want supported:
	
	* get_upvotes: 
		
		Get the number of Upvotes on an object (if any)
		```
		def get_upvotes(self, obj):
        
	        content_type = ContentType.objects.get_for_model(obj)
	               
	        votes = self.filter(content_type=content_type, object_id=obj._get_pk_val(), vote__exact=UPVOTE).aggregate(upvotes=Sum('vote'))
	        
	        #print votes
	        
	        if votes['upvotes'] is None:
	            votes['upvotes'] = 0
	
	        return votes['upvotes']
		```
		
	* get_downvotes
	
		Get the number of downvotes on an object (if any)
		```
		def get_downvotes(self, obj):

	        content_type = ContentType.objects.get_for_model(obj)
	        
	        votes = self.filter(content_type=content_type, object_id=obj._get_pk_val(), vote__exact=DOWNVOTE).aggregate(downvotes=Sum('vote'))
	        
	        if votes['downvotes'] is None:
	            votes['downvotes'] = 0
	            
	        return -votes['downvotes']
		```
		
	* get_score
	
		Get the total aggregate score and total number of votes made on an object
		
		```
		def get_score(self, obj):
	        
	        content_type = ContentType.objects.get_for_model(obj)
	        result = self.filter(content_type=content_type,
	                             object_id=obj._get_pk_val()).aggregate(
	                                                                    score=Sum('vote'),
	                                                                    num_votes=Count('vote'))
	        #It may happen that there has been no voting on this object so far.
	        if result\['score'\] is None:
	            result\['score'\] = 0
	        
	        return result
		```
		
	* record_vote
	
		A user must be able to vote only once. If they vote again, the previous value must be updated.
		
		```
		def record_vote(self, obj, vote, user):
	        
	        if vote not in (+1, 0, -1):
	            raise ValueError('Invalid vote (must be +1/0/-1)')
	        content_type = ContentType.objects.get_for_model(obj)
	        # First, try to fetch the instance of this row from DB
	        # If that does not exist, then it is the first time we're creating it
	        # If it does, then just update the previous one
	        try:
	            vote_obj = self.get(voter=user, content_type=content_type, object_id=obj._get_pk_val())
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
	                vote_obj = self.create(voter=user, content_type=content_type, object_id=obj._get_pk_val(), vote=vote)                        
	            except:
	                print '{file}: something went wrong in creating a vote object at {line}'.format(file=str('__FILE__'), line=str('__LINE__'))
	                raise ObjectDoesNotExist    
	        
	        return vote_obj
		```
		
	* get_top
	
		Get the top rated posts based on their scores
		
		```
		def get_top(self, model, limit=10, inverted=False):
	        
	        content_type= ContentType.objects.get_for_model(model)
	        
	        #Get a queryset of all the objects of the model. Get their scores
	        results = self.filter(content_type=content_type).values('object_id').annotate(score=Sum('vote'))
	        if inverted:
	            results = results.order_by('score')
	        else:
	            results = results.order_by('-score')
	        
	        #We have a iterable list of objects of the requested model and their respective scores
	        # Use in_bulk() to avoid O(limit) db hits.
	        objects = model.objects.in_bulk([item['object_id'] for item in results[:limit]])
	
	        # Yield each object, score pair. Because of the lazy nature of generic
	        # relations, missing objects are silently ignored.
	        for item in results[:limit]:
	            id, score = item['object_id'], item['score']
	            if not score:
	                continue
	            if id in objects:
	                yield objects[id], int(score)
		```
		
	* get_bottom
	
		Get the least rated posts based on their scores
		
		```
		def get_bottom(self, model, limit):
        
        return self.get_top(model=model, limit=limit, reversed=True)
		```
		
	* get_for_user
	
		Get the score by the user on the post
		
		```
		def get_for_user(self, obj, user):
	        
	        if not user.is_authenticated():
	            return None
	        content_object = ContentType.objects.get_for_model(obj)
	        try:
	            vote = self.get(voter=user, content_object=content_object, object_id=obj._get_pk_val())
	      
	        except ObjectDoesNotExist:
	            print 'No vote by {user} on {object}'.format(user=user, object=obj)
	            vote = None
	            
	        return vote
		```
		
	* get_for_user_in_bulk
		
		Get all the objects on which the user has voted on
		```
		def get_for_user_in_bulk(self, user):
	        
	        return self.filter(user=user)
		```
	
	So, as a `setUp` pre-processing, we would like to have 3 users. One is the author and other two are voters. Also, we'd want an instance of the post
	we are voting on as object (since right now we are testing models).
	
	Here's a `setUp` method:
	
	```
	fixtures = ['fixtures.json',]
    
    def setUp(self, *args, **kwargs):
        #create 2 new users
        #load the blogging post into a variable
        self.factory = RequestFactory()
        self.author = User.objects.get(pk="1")
        self.user1 = User.objects.create_user(username="User1", email="user1@users.com", password="user1")
        self.user2 = User.objects.create_user(username="User2", email="user2@users.com", password="user2")
        self.article = BlogContent.objects.get(pk="1")
	```
	
	Now, let us **vote** on the post:
	
	```
	from voting.models import Vote, UPVOTE, DOWNVOTE
	...
	
	def test_vote_model(self):
        vote = Vote()
        vote.object_id = self.article._get_pk_val()
        vote.content_type = ContentType.objects.get_for_model(self.article)
        vote.content_object = ContentType.objects.get_for_model(self.article)
        
        vote.voter = self.user1
        vote.vote = UPVOTE
        
        vote.save()
        
        vote_obj = Vote.objects.all()[0]
        self.assertEqual(vote_obj._get_pk_val(), vote._get_pk_val(), "Primary Keys do not match")
        self.assertEqual(vote.vote, vote_obj.vote, "Vote value does not match")
	```
	
	The object creation can be shortened as:
	
	```
	vote = Vote.objects.create(object_id=self.article._get_pk_val(),
                           content_type = ContentType.objects.get_for_model(self.article),
                           content_object = ContentType.objects.get_for_model(self.article),
                           voter = self.user1,
                           vote = UPVOTE
                           )
	```
	
	We're testing that what is saved in the DB is what we wanted to
	Running the test shows that it is ok.
	
	We would now like to test if our Vote Manager methods are working fine?
	
	For starters, I'd make two upvotes on the article and hope that the `get_upvotes` method returns the same value
		
	```
	def test_get_upvotes(self):
        self._create_votes((UPVOTE, UPVOTE))
        
        vote = Vote.objects.get_upvotes(self.article)
        print 'upvotes: {upvotes}'.format(upvotes=vote)
        
        self.assertEqual(vote, 2)
	```
	
	Running the tests `python manager.py test` yields:
	
	```
	AttributeError: 'VoteManager' object has no attribute 'objects'
	```	
   
   Yes, we used `self.objects.filter`, that is wrong, it is just `self.filter`. We already have an object instance and are not calling into
   the Class.
   
   Now:
   
   ```
   Cannot resolve keyword 'votes' into field. Choices are: content_type, id, object_id, vote, vote_date, vote_modified, voter
   ```
   
   In our manager method we wrote, ...`.aggregate(upvotes=Sum('votes'))`. Change that `votes` to `vote` and be more careful next time 
   when we write such methods. The names must correspond to the ones declared in the models.
  
 * `def get_top(self, model, limit=10, inverted=False):`
 	
 	```
 	class_name = content_type.model_class()
    objects = class_name.objects.in_bulk([item['object_id'] for item in results[:limit]])
    ```
    
    `in_bulk` can be used only with the manager, which means that we cannot use it from the model instance, but from its class name. Hence, we first get its Class
    using `model_class()` method and then fetch from that.
    
    
    Now, a test for get_top(), even though it is supposed to yield a single entry for now:
    
    ```
    def test_get_top(self):
        self._create_votes((UPVOTE, UPVOTE))
        
        values = Vote.objects.get_top(model=self.article)
        #print 'upvotes: {upvotes}'.format(upvotes=vote)
        for obj,value in values:
            print obj, value
            self.assertEqual(obj, self.article._get_pk_val(), "Article ID is not correct")
            self.assertEqual(value, 2, "Score is not 2")
    ```
    This isn't working. It just passes the test. But it doesn't print anything.
    
    A look into the code reveals that the problem is in the assignment of `id`, which should be an integer, but is being returned as unicode, and hence, 
    comparison is not returning true. This shouldn't be happening though, python should have taken care of that. Anyhow, we modify the code as:
    
    ```
    for item in results[:limit]:
    id, score = item['object_id'], item['score']
                
    if not score:
        continue
    
    if int(id) in objects:
        yield objects[int(id)], int(score)
    ```
   
   ```
   def test_get_for_user(self):
        self._create_votes((UPVOTE, UPVOTE))
        
        self._require_login('user1', 'user1')
        vote = Vote.objects.get_for_user(self.article, self.user1)
        self.assertEqual(vote.vote, UPVOTE, "We upvoted it, but got {vote} instead".format(vote=vote.vote))
        self._logout()
        
        self._require_login('craft', 'craft')
        vote = Vote.objects.get_for_user(self.article, self.author)
        self.assertIsNone(vote,"Did not expect an instance")
        self._logout()
        
        vote = Vote.objects.get_for_user(self.article, self.user2)
        print vote
        self.assertIsNone(vote,"Did not expect an instance. Did not login")
   ```
   
   This one fails, the user is not supposed to be logged in, but the method still returns vote statistics for user2. 
   That is because we are explicitly passing the User2 instance.
   
   Now, we get on to devicing serializers to serve our REST requests:
   
   The vote serializer is much like the one we made for annotations:
   
   ```
   class VoteSerializer(serializers.ModelSerializer):
    
    voter = UserSerializer(read_only=True)
    
    class Meta:
        model = Vote
        fields = (
                  'id', 'voter', 'vote', 'vote_modified', 'content_type', 'object_id',
                  )
    
    def create(self, validated_data):
        print "In create"
        print validated_data
        vote = Vote()
        vote.voter = validated_data.get('voter')
        vote.vote = validated_data.get('vote')
        vote.content_type = validated_data.get('content_type')
        vote.object_id = validated_data.get('object_id')
        
        #Get row from contentType which has content_type
        content_object = ContentType.objects.get_for_id(vote.content_type.id)
        
        vote.content_object = content_object.model_class().objects.get(id=vote.object_id)
        
        print vote.content_object  
                
        Vote.objects.record_vote(vote.content_object, vote=vote.vote, user=vote.voter)
        
        return vote
    
    def update(self, instance, validated_data):
        print "In update"
        vote = instance
        vote.voter = validated_data.get('voter', vote.voter)
        vote.vote = validated_data.get('vote', vote.body)
        vote.content_type = validated_data.get('content_type',vote.content_type)
        vote.object_id = validated_data.get('object_id',vote.object_id)

        #Get row from contentType which has content_type
        content_object = ContentType.objects.get_for_id(vote.content_type.id)        
        vote.content_object = content_object.model_class().objects.get(id=vote.object_id)        
        
        print vote.content_object     
                
        Vote.objects.record_vote(vote.content_object, vote=vote.vote, user=vote.voter)
        
        return vote
   ```
   
   The BlogContent is also fairly the same, except that now we want votes instead of annotations:
   
   ```   
	class BlogContentSerializer(serializers.ModelSerializer):
	    #Tell BlogContent that it has a relation on Annotations    
	    vote = serializers.SerializerMethodField()
	    #annotation = SerializeAnnotationsField()
	    
	    class Meta:
	        model = BlogContent
	        fields =('id', 'title', 'create_date', 'data', 'url_path', 
	                 'author_id', 'published_flag', 'section', 'content_type',
	                 'annotation',)
	     
	    def get_vote(self, obj):
	        content_object = ContentType.objects.get_for_model(obj)
	        print "In BlogContentSerializer"
	        print obj
	        vote =  Vote.objects.filter(content_type=content_object.id, object_id=obj.id)
	        if len(vote) is not 0:
	            print VoteSerializer(vote, many=True).data
	            return (VoteSerializer(vote, many=True).data)
	        else:
	            return None      
   ```
   
   Most views too are the same, this one, for vote is like the annotation viewset:
   
   ```   
	class VoteViewSet(viewsets.ModelViewSet):
	    
	    queryset = Vote.objects.all()
	    serializer_class = VoteSerializer
	    permission_classes = (permissions.IsAuthenticatedOrReadOnly, 
	                          AnnotationIsOwnerOrReadOnly,)
	
	    def perform_create(self, serializer):
	        serializer.save(voter=self.request.user)
   ```
   
   
   URLs too are pretty much the same to begin with:
   
   ```
   vote_list = VoteViewSet.as_view({
	    'get': 'list',
	    'post': 'create'
	    })
	vote_detail = VoteViewSet.as_view({
	    'get': 'retrieve',
	    'put': 'update',
	    'patch': 'partial_update',
	    'delete': 'destroy'
	    })
   ```
   
   Let us get to tests:
   
   First, a simple serializer:
   ```
   def test_create_serializer_class(self):
        vote = Vote.objects.record_vote(self.article, UPVOTE, self.user1)
        obj = VoteSerializer(vote)
        #print(obj.data)
        
        json_value = JSONRenderer().render(obj.data)
        print '\n', json_value, '\n'
   ```
   
   Now, lets create a vote using POST too:
   
   ```
   def test_create_vote(self, content=None):
        #use test client to POST a request
        self._require_login('craft1','craft1')
        #print(self.user.is_authenticated()) # returns True
        string_data = {
                    'content_type': '9',
                    'object_id':'1',
                    'vote':'1',
                    }
        json_data = json.dumps(string_data)
        response =  self.client.post(
            '/voting/vote/',
            content_type='application/json',
            data = json_data,
         )
        
        print response.content.decode()
   ```
   Running this test says:
   
   ```
   <h1>Not Found</h1><p>The requested URL /voting/vote/ was not found on this server.</p>
   ```
   
   Hmm, we missed an 's' in post URL:
   Fixing the 'vote' to 'votes' and now we have:
   
   ```
   {"detail":"Authentication credentials were not provided."}
   ```
   Now, here's the funny thing:
   If I uncomment the print statement after my _require_login call, my message changes (it moves forward). I don't know why, but it works.
   
   
   The `record_vote` method is wrong, for it is not a Table related operation, but a database field related operation.

> Managers are accessible only via model classes, rather than from model instances, to enforce a separation between "table-level" operations and "record-level" operations.

So, and it is basically a save operation, so we will override that instead in the Model Class.

	Also, it does not deserve a `save` override either. This is because in save, we already HAVE an instance, 
	and what we would be doing is getting another instance of the same class and either using the new one, or the old one.
	This functionality belongs to the views.

	So, we'll move it into our serialzer's create method.
	
	```
	def create(self, validated_data):
        print "In create"
        print validated_data
        vote = Vote()
        vote.voter = validated_data.get('voter')
        vote.vote = validated_data.get('vote')
        vote.content_type = validated_data.get('content_type')
        vote.object_id = validated_data.get('object_id')
        
        #Get row from contentType which has content_type
        content_object = ContentType.objects.get_for_id(vote.content_type.id)
        
        vote.content_object = content_object.model_class().objects.get(id=vote.object_id)
        
        print vote.content_object  
                
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
	```    
	
	This passes the test.
	
	Note that we don't need to fill in the content_object field if we are filling the content_type and object_id fields. It will only cause problems and solve nothing.
	
	
	
* In order to ensure that the one who created the post is not able to vote on it, we need to write a custom view rather than using the readymade viewsets.
	