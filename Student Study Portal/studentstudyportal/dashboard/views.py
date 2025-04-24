from django import contrib
from django.core.checks import messages
from django.forms.widgets import FileInput
from django.shortcuts import redirect, render
from . forms import *
from django.contrib import messages
from django.views import generic
from youtube_search import YoutubeSearch
import requests
import wikipedia
from .models import Homework, Todo
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject= request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homeworks.save() 
            messages.success(request,f'Homework Added from {request.user.username}!!')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
        "homeworks":homework,
        "homeworks_done":homework_done,
        "form":form
    }
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = YoutubeSearch(text, max_results=10).to_dict()
        result_list = []
        for i in video:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0], 
                'channel': i['channel'],
                'link': f"http://www.youtube.com/watch?v={i['id']}", 
                'views': i['views'],
                'published': '', 
                'description':i.get('description', 'No description available.') 
            }
            result_list.append(result_dict)
        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/youtube.html', context)
    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/youtube.html', context)

@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished 
            )
            todos.save()
            messages.success(request,f'Todo Added from {request.user.username}!!')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,"dashboard/todo.html",context)

@login_required
def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'), 
                'description': answer['items'][i]['volumeInfo'].get('description'), 
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),  
                'categories': answer['items'][i]['volumeInfo'].get('categories'),  
                'rating': answer['items'][i]['volumeInfo'].get('pageRating'), 
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),  
                'preview': answer['items'][i]['volumeInfo'].get('previewLink'),  
            }
            result_list.append(result_dict)
        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)


import requests
from django.shortcuts import render
from .forms import DashboardForm

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        try:
            r = requests.get(url)
            r.raise_for_status()
            answer = r.json()
            print("API Response:", answer)

            if isinstance(answer, dict) and 'message' in answer:
                context = {
                    'form': form,
                    'input': text,
                    'error': answer['message']
                }
                return render(request, "dashboard/dictionary.html", context)
            
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']

            if 'examples' in answer[0]['meanings'][0]['definitions'][0]:
                example = answer[0]['meanings'][0]['definitions'][0]['examples']
            else:
                example = "Example not found." 

            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            context = {
                'form': form,
                'input': '',
                'error': f"API request failed: {e}",
            }
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            context = {
                'form': form,
                'input': '',
                'error': f"API request failed: {e}",
            }
        except (KeyError, ValueError, IndexError) as e:
            print(f"JSON/Data Error: {e}")
            context = {
                'form': form,
                'input': '',
                'error': f"Error processing API response: {e}",
            }
        except Exception as e:
            print(f"Unexpected Error: {e}")
            context = {
                'form': form,
                'input': '',
                'error': f"An unexpected error occurred: {e}",
            }
        return render(request, "dashboard/dictionary.html", context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "dashboard/dictionary.html", context)

def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title': search.title,
            'link': search.url,
            'details': search.summary
        }
        return render(request, "dashboard/wiki.html", context)
    else:
        form = DashboardForm()
        context = {
            'form':form,
        }
    return render(request, "dashboard/wiki.html", context)


def conversion(request):
    answer = None
    measurement_form = None
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if form.is_valid():
            measurement_type = form.cleaned_data['measurement']
            if measurement_type == 'length':
                measurement_form = ConversionLengthForm(request.POST)
                if measurement_form.is_valid():
                    first = measurement_form.cleaned_data['measure1']
                    second = measurement_form.cleaned_data['measure2']
                    input_value = measurement_form.cleaned_data['input']
                    if input_value is not None:
                        if first == 'yard' and second == 'foot':
                            answer = f'{input_value} yard = {input_value * 3} foot'
                        elif first == 'foot' and second == 'yard':
                            answer = f'{input_value} foot = {input_value / 3} yard'
            elif measurement_type == 'mass':
                measurement_form = ConversionMassForm(request.POST)
                if measurement_form.is_valid():
                    first = measurement_form.cleaned_data['measure1']
                    second = measurement_form.cleaned_data['measure2']
                    input_value = measurement_form.cleaned_data['input']
                    if input_value is not None:
                        if first == 'pound' and second == 'kilogram':
                            answer = f'{input_value} pound = {input_value * 0.453592} kilogram'
                        elif first == 'kilogram' and second == 'pound':
                            answer = f'{input_value} kilogram = {input_value * 2.20462} pound'
    else:
        form = ConversionForm()
    context = {
        'form': form,
        'm_form': measurement_form,
        'answer': answer,
    }
    return render(request, "dashboard/conversion.html", context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username} !!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, "dashboard/register.html", context)


@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    homework_done = not homeworks.exists()
    todos_done = not todos.exists()

    print("Homeworks:", homeworks)
    print("Todos:", todos)
    print("Homework Done:", homework_done)
    print("Todos Done:", todos_done)

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done,
    }
    return render(request, "dashboard/profile.html", context)