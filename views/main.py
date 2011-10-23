from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from wiki.models.courses import Course
from wiki.models.history import HistoryItem

def index(request):
	if request.user.is_authenticated():
		# Get the courses the user is watching
		courses = Course.objects.all()
		watched_courses = []
		history_items = []
		# Oh god terrible find a way to use querysets to do this
		for course in courses:
			if course.has_watcher(request.user):
				watched_courses.append(course)
		# Get all the history items whose courses the user is watchin
		items = HistoryItem.objects.all()
		# omg
		for item in items:
			if request.user in item.course.watchers.all():
				history_items.append(item)

		# Now get things the user has done
		your_actions = HistoryItem.objects.filter(user=request.user).order_by('-timestamp')

		# Show the user's dashboard
		data = {
			'watched_courses': watched_courses,
			'your_actions': your_actions,
			'history_items': history_items[::-1],
		}
		return render(request, 'main/dashboard.html', data)
	else:
		# Show the main page for logged-out users
		return render(request, 'main/index.html')

# POSTed to by the login form; should never be accessed by itself
def login_logout(request):
	# Check if the user is already logged in and is trying to log out
	if request.user.is_authenticated():
		if request.POST['logout']:
			logout(request)
	else:
		if request.POST['login']:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)

	# Redirect to the index page etc
	return index(request)

# Recent changes
def recent(request, num_days=1, show_all=False):
	data = {
		'history': HistoryItem.objects.get_since_x_days(num_days, show_all),
		'num_days': num_days,
		'base_url': '/recent/all' if show_all else '/recent', # better way of doing this?
		'show_all': show_all
	}
	return render(request, 'main/recent.html', data)
