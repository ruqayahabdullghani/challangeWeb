from django.shortcuts import render, redirect
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from .models import Task
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')
    

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
      if self.request.user.is_authenticated:
        return redirect('tasks')
      return super(RegisterPage, self).get(*args, **kwargs)


    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    

    
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        filter_status = self.request.GET.get('filter-status') or 'all'
        
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)
        
        if filter_status == 'complete':
            context['tasks'] = context['tasks'].filter(complete=True)
        elif filter_status == 'incomplete':
            context['tasks'] = context['tasks'].filter(complete=False)

        context['search_input'] = search_input
        context['filter_status'] = filter_status
        return context
      





class TaskDetail(LoginRequiredMixin,DetailView):
    model = Task
    template_name = 'base/task_detail.html'
    context_object_name = 'task'


class TaskCreate(LoginRequiredMixin,CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title']
    success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin,DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')


def toggle_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.complete = not task.complete
        task.save()
        return JsonResponse({'status': 'success', 'complete': task.complete})
    return JsonResponse({'status': 'error'}, status=400)

