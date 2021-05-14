from django.http import Http404
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateCourseForm, CreateActivityForm, CreateModuleForm
from django.utils.text import slugify
from .models import Course, Module, Content, Activity, Post
from django.urls import path, reverse, reverse_lazy
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import ListView

def inicio(request):
    if request.user.is_authenticated:
        cursos_dono = Course.objects.filter(owner=request.user)
        cursos_dict = {'dono': cursos_dono}
        return render(request, 'inicio.html', cursos_dict)
    else:
        return redirect('/')

def criar(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CreateCourseForm(request.POST)
            if form.is_valid():
                # form.save()
                owner = request.user
                subject = form.cleaned_data.get('subject')
                title = form.cleaned_data.get('title')
                overview = form.cleaned_data.get('overview')
                slug = slugify(form.cleaned_data.get('title'))

                curso = Course(owner=owner, subject=subject, title=title, overview=overview, slug=slug)
                curso.save()
                return redirect('/genus/inicio/')
        else:
            form = CreateCourseForm()
        return render(request, 'createCurso.html', {'form': form})
    else:
        return redirect('/')

def buscar_cursos(request):
    if request.user.is_authenticated:
        cursos = Course.objects.all()
        cursos_paginator = Paginator(cursos, 1)
        num_pagina = request.GET.get('paginas')
        paginas = cursos_paginator.get_page(num_pagina)
        cursos_dict = {
            'cursos': cursos,
            'paginas': paginas,
        }
        
        return render(request, 'buscarCursos.html', cursos_dict)
    else:
        return redirect('/')

def resumo(request, curso_slug):
    if request.user.is_authenticated:
        try:
            c= Course.objects.get(slug=curso_slug)
        except Course.DoesNotExist:
            raise Http404("Encontramos um erro")
        return render(request, 'resumoCurso.html', {'curso':c})
    else:
        return redirect('/')

def curso(request, curso_slug):
    dono=False
    if request.user.is_authenticated:
        try:
            c= Course.objects.get(slug=curso_slug)
        except Course.DoesNotExist:
            raise Http404("Encontramos um erro")
        if(request.user==c.owner):
            dono=True
        return render(request, 'muralCurso.html', {'curso':c, 'dono': dono})
    else:
        return redirect('/')

def modulos(request, curso_slug):
    dono=False
    if request.user.is_authenticated:
        try:
            c= Course.objects.get(slug=curso_slug)
            m= Module.objects.filter(course=c)
            m= m.filter( Q(not_instance_of=Activity) )
            a = Activity.objects.filter(module__in=m)
        except Course.DoesNotExist:
            raise Http404("Encontramos um erro")
        except Module.DoesNotExist:
            m=None
        except Activity.DoesNotExist:
            a=None
        if(request.user==c.owner):
            dono=True
        return render(request, 'modulosCurso.html', {'curso':c, 'dono': dono, 'modulos': m, 'atividades': a})
    else:
        return redirect('/')

def criar_modulo(request, curso_slug):
    dono=False
    try:
        c= Course.objects.get(slug=curso_slug)
    except Course.DoesNotExist:
        raise Http404("Encontramos um erro")
    if(request.user==c.owner):
            dono=True
    if request.user.is_authenticated:
        if dono:
            if request.method == 'POST':
                form = CreateModuleForm(request.POST)
                if form.is_valid():
                    record = form.save(commit=False)
                    record.course=c
                    form.save()
                    # owner = request.user
                    # subject = form.cleaned_data.get('subject')
                    # title = form.cleaned_data.get('title')
                    # overview = form.cleaned_data.get('overview')
                    # slug = slugify(form.cleaned_data.get('title'))

                    # curso = Course(owner=owner, subject=subject, title=title, overview=overview, slug=slug)
                    # curso.save()
                    
                    return redirect('/genus/'+curso_slug+'/modulos/')
            else:

                form = CreateModuleForm()
            return render(request, 'createModule.html', {'form': form})
        else:
            print("opaopa")
            return redirect('/genus/inicio/')
    else:
        return redirect('/')

def exibir_modulo(request, curso_slug, modulo_id):
    if request.user.is_authenticated:
        dono=False

        try:
            c= Course.objects.get(slug=curso_slug)
            m= Module.objects.get(pk=modulo_id)
            ap = Module.objects.filter(Q(Activity___module = m) | Q(Post___module = m))
        except Course.DoesNotExist:
            raise Http404("Ops, esse curso não existe")
        except Course.DoesNotExist:
            raise Http404("Ops, esse módulo não existe")
        
        if request.user==c.owner:
            dono=True
        return render(request, 'modulo.html', {'curso':c, 'dono': dono, 'modulo': m, 'atividades_posts':ap})

    else:
        return redirect('/')

def criar_atividade(request, curso_slug, modulo_id):
    dono=False
    try:
        c= Course.objects.get(slug=curso_slug)
        m= Module.objects.get(pk=modulo_id)
    except Course.DoesNotExist:
        raise Http404("Ops, esse curso não existe")
    except Course.DoesNotExist:
        raise Http404("Ops, esse módulo não existe")
    if(request.user==c.owner):
            dono=True
    if request.user.is_authenticated:
        if dono:
            if request.method == 'POST':
                form = CreateActivityForm(request.POST)
                if form.is_valid():
                    record = form.save(commit=False)
                    record.course=c
                    record.module=m
                    form.save()
                    # owner = request.user
                    # subject = form.cleaned_data.get('subject')
                    # title = form.cleaned_data.get('title')
                    # overview = form.cleaned_data.get('overview')
                    # slug = slugify(form.cleaned_data.get('title'))

                    # curso = Course(owner=owner, subject=subject, title=title, overview=overview, slug=slug)
                    # curso.save()
                    
                    return redirect('/genus/'+curso_slug+'/'+str(modulo_id)+'/')
            else:

                form = CreateActivityForm()
            return render(request, 'createActivity.html', {'form': form})
        else:
            print("opaopa")
            return redirect('/genus/inicio/')
    else:
        return redirect('/')

def criar_post(request, curso_slug, modulo_id):
    dono=False
    try:
        c= Course.objects.get(slug=curso_slug)
        m= Module.objects.get(pk=modulo_id)
    except Course.DoesNotExist:
        raise Http404("Ops, esse curso não existe")
    except Course.DoesNotExist:
        raise Http404("Ops, esse módulo não existe")
    if(request.user==c.owner):
            dono=True
    if request.user.is_authenticated:
        if dono:
            if request.method == 'POST':
                form = CreateActivityForm(request.POST)
                if form.is_valid():
                    record = form.save(commit=False)
                    record.course=c
                    record.module=m
                    form.save()
                    # owner = request.user
                    # subject = form.cleaned_data.get('subject')
                    # title = form.cleaned_data.get('title')
                    # overview = form.cleaned_data.get('overview')
                    # slug = slugify(form.cleaned_data.get('title'))

                    # curso = Course(owner=owner, subject=subject, title=title, overview=overview, slug=slug)
                    # curso.save()
                    
                    return redirect('/genus/'+curso_slug+'/'+str(modulo_id)+'/')
            else:

                form = CreateActivityForm()
            return render(request, 'createPost.html', {'form': form})
        else:
            print("opaopa")
            return redirect('/genus/inicio/')
    else:
        return redirect('/')


# def criar_post(request, curso_slug, modulo_id):
#     if request.user.is_authenticated:
#         dono=False
        
#     else:
#         return redirect('/')


# class ContentCreateUpdateView(TemplateResponseMixin, View):
#     module = None
#     model = None
#     obj = None
#     template_name = 'courses/manage/content/form.html'
    
#     def get_model(self, model_name):
#         if model_name in ['text', 'video', 'image', 'file']:
#             return apps.get_model(app_label='courses',model_name=model_name)
#         return None
    
#     def get_form(self, model, *args, **kwargs):
#         Form = modelform_factory(model, exclude=['owner','order','created','updated'])

#         return Form(*args, **kwargs)
    
#     def dispatch(self, request, module_id, model_name, id=None):
#         self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
#         self.model = self.get_model(model_name)
        
#         if id:
#             self.obj = get_object_or_404(self.model, id=id,owner=request.user)
#         return super(ContentCreateUpdateView,self).dispatch(request, module_id, model_name, id)
    
#     def get(self, request, module_id, model_name, id=None):
#         form = self.get_form(self.model, instance=self.obj)
#         return self.render_to_response({'form': form,'object': self.obj})

#     def post(self, request, module_id, model_name, id=None):
#         form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.owner = request.user
#             obj.save()
#             if not id:
#                 # new content
#                 Content.objects.create(module=self.module,item=obj)
#             return redirect('module_content_list', self.module.id)
#         return self.render_to_response({'form': form, 'object': self.obj})
