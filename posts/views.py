from urllib import quote_plus
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse , HttpResponseRedirect , Http404
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.utils import timezone
from comments.models import Comment
from .forms import PostForm
from comments.forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (
	PostListSerializer,
	PostDetailSerializer,
	PostCreateUpdateSerializer,
	)
# Create your views here.
def posts_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404

	if not request.user.is_authenticated():
		raise Http404

	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		messages.success(request,"Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		'title':'Updtae Post',
		'form':form
	}
	return render(request,'post_form.html',context)


def posts_detail(request,slug=None):
	instance = get_object_or_404(Post,slug=slug)
	#print instance.publish , timezone.now().date()
	if instance.draft or instance.publish > timezone.now().date():
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	initial_data = {
		"content_type":instance.get_content_type,
		"object_id": instance.id,
	}
	form = CommentForm(request.POST or None, initial=initial_data)
	if form.is_valid() and request.user.is_authenticated():
		c_type = form.cleaned_data.get("content_type")
		content_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get("object_id")
		content_data = form.cleaned_data.get("conent")
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None
		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists() and parent_qs.count()==1:
				parent_obj = parent_qs.first()

		new_comment,created = Comment.objects.get_or_create(
					user=request.user,
					content_type = content_type,
					object_id = obj_id,
					conent = content_data,
					parent = parent_obj,
			)
		return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

	share_string = quote_plus(instance.content)
	comments = instance.comments #Comment.objects.filter_by_instance(instance)
	context = {
	'title':instance.title,
	'instance':instance,
	"share_string":share_string,
	"comments":comments,
	"comment_form":form,
	}
	return render(request,'post_detail.html',context)

def posts_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.active()#.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		queryset_list = Post.objects.all()
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(Q(title__icontains=query)|
				Q(content__icontains=query)|
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query)
				).distinct()
	paginator = Paginator(queryset_list, 5) # Show 5 posts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
	    queryset = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    queryset = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    queryset = paginator.page(paginator.num_pages)
	context = {
		'object_list':queryset,
		'title':'List',
		'page_request_var':page_request_var,
		'today':today
	}
	return render(request,'index.html',context)



def posts_update(request,slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post,slug=slug)
	form = PostForm(request.POST or None, request.FILES or None,instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request,"<a href='#'>Item</a> Saved",extra_tags="html_safe")
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
	'title':instance.title,
	'instance':instance,
	'form':form
	}
	return render(request,'post_form.html',context)



def posts_delete(request,slug=None):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post,slug=slug)
	instance.delete()
	messages.success(request,"Successfully Deleted")
	return redirect("posts:lists")

class PostList(APIView):
	def get(self,request):
		queryset = Post.objects.all()
		serializers = PostListSerializer
		print serializers.data
		return Response(serializers.data)
	# queryset = Post.objects.all()
	# serializer_class = PostListSerializer
