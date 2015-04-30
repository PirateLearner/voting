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
   