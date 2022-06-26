

from django.shortcuts import get_object_or_404
from django.views import View
from datetime import datetime
from email.policy import HTTP
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from .models import ArtistProfile ,UserProfile,ArtistProfileBulkUpload,UserProfile
from django.db.models import Sum

from django.contrib.auth import login,authenticate,logout
from .forms import UserProfileForm,ArtistProfileBulkUploadForm,ArtistAliasForm,ArtistAlias,UserProfileUpdateForm,ArtistProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
import os
import csv
from django.conf import settings
import logging
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.template.loader import get_template
from .utils import render_to_pdf
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django.contrib.postgres.search import SearchQuery,SearchVector,SearchRank
# Create your views here.

def signup_view(request):
    if request.method =="POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db() 
            user.userprofile.email = form.cleaned_data.get('email')
            user.userprofile.artist_name = form.cleaned_data.get('artist_name')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            #login(request,user)
            return redirect('login_view')
    else:
        form = UserProfileForm()
    return render(request,'artists/signup.html',{'form':form})
        

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            if user.is_superuser:
                return redirect('admin_page')   
            return redirect('artists_details')
    else:
        form = AuthenticationForm()
    return render(request,'artists/login_view.html',{"form":form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login_view')




#Upload_csv
def save_new_artists_profile_from_csv(file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension =='.csv':
            with open(file_path) as data_stream:
                reader = csv.reader(data_stream, delimiter=",")
                for index, row in enumerate(reader, 1):
                    if index == 1:
                        continue
                    profiles=[
                    ArtistProfile(
                    song = row[0],
                    artist = row[1],
                    price = row[2],
                    downloads = row[3],
                    total_amount = row[4],
                    month =row[5],
                    year =row[6],
                    company =row[7],
                )] 
                    ArtistProfile.objects.bulk_create(profiles)
        elif file_extension =='.xlsx':
            reader1 = pd.read_excel(file_path,sheet_name=None)
            my_list = []
            for key,value in reader1.items() :
                my_list.append(value)
        
            reader = pd.DataFrame(my_list[0])
            for index, row in reader.iterrows():
                if index == 0:
                    continue
                profiles=[
                ArtistProfile(
                    song = row[0],
                    artist = row[1],
                    price = row[2],
                    downloads = row[3],
                    total_amount = row[4],
                    month =row[5],
                    year =row[6],
                    company =row[7],
                    
                )]
                ArtistProfile.objects.bulk_create(profiles)
        
@login_required(login_url='login_view')
def upload_data(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'GET':
        form = ArtistProfileBulkUploadForm()
        return render(request,'artists/artist_profile_upload.html', {'form':form})

    # If not GET method then proceed
    try:
        form = ArtistProfileBulkUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            #csv_file = form.cleaned_data['file']
            try:
                date_upload = ArtistProfileBulkUpload.objects.filter(month=form.cleaned_data.get('month')).filter(year=form.cleaned_data.get('year'))[0]
                if date_upload:
                    messages.error(request, 'Duplicate File')
                    return redirect('upload_data')
            except:
                pass
            doc = form.save()
            
            doc.save()
            file_path = doc.file.url
            full_file_path = str(settings.BASE_DIR)+str(file_path)

            
            # get the path of the file saved in the server
            #full_file_path = os.path.join(settings.BASE_DIR, str(file_path))
            
            
            save_new_artists_profile_from_csv(full_file_path)
            
    except Exception as e:
        logging.getLogger('error_logger').error('Unable to upload file. ' + repr(e))
        messages.error(request, 'Unable to upload file. ' + repr(e))      
    return redirect('admin_page')



@login_required(login_url='login_view')
def artists_details(request):
    try:
        username = UserProfile.objects.filter(artist_name = request.user)[0]
        #title_list_names = username.user_artist.all()
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    #print(alias_list)
    query_search=None
    query_search = request.GET.get("song")
    if query_search is not None:
        vector = SearchVector('song')
        query=SearchQuery(query_search)
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(song__icontains=query_search))
            #song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(song__unaccent__lower__trigram_similar=query_search))
            #song_list.append(ArtistProfile.objects.annotate(search=vector).filter(search=query).filter(artist__icontains=x))
            #song_list.append(ArtistProfile.objects.annotate(rank=SearchRank(vector, query)).order_by('-rank').filter(artist__startswith=x))
            
    
    else:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    
    if query_search is not None:
        songs=[]
        for songs_query in song_list:
            for s in songs_query:
                songs.append(s)
        total_amount = sum(song.total_amount for song in songs)
        total_downloads = sum(song.downloads for song in songs)        
    else:
        songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
        total_amount = sum(song.total_amount for song in songs)
        total_downloads = sum(song.downloads for song in songs)
    
    artist_name = username
    return render(request,'artists/artists_details.html',{'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})

@login_required
def month_detail(request,slug):
    try:
        username = UserProfile.objects.filter(artist_name = request.user)[0]
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    song_list=[]
    for x in alias_list:
        song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(month=slug))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    months = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
    
    total_amount = sum(song.total_amount for song in months)
    total_downloads = sum(song.downloads for song in months)
    
    #months = ArtistProfile.objects.filter(month=slug)

    return render(request,'artists/month_details.html',{"months": months,'total_amount':total_amount,'total_downloads':total_downloads })

@login_required
def song_detail(request,slug):
    song_title=ArtistProfile.objects.filter(song=slug).order_by('-downloads')
    
    total_amount = song_title.aggregate(Sum('total_amount'))['total_amount__sum']
    total_downloads = song_title.aggregate(Sum('downloads'))['downloads__sum']
    

    return render(request,'artists/song_detail.html',{"song_title":song_title ,'total_amount':total_amount,'total_downloads':total_downloads})

@login_required
def company_detail(request,slug):
    try:
        username = UserProfile.objects.filter(artist_name = request.user)[0]
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    song_list=[]
    for x in alias_list:
        song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(company=slug))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    company_name = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
    
    total_amount = sum(song.total_amount for song in company_name)
    total_downloads = sum(song.downloads for song in company_name)
    return render(request,'artists/company_detail.html',{"company_name":company_name ,'total_amount':total_amount,'total_downloads':total_downloads})


@login_required
def add_alias(request):
    if request.method =="POST":
        form = ArtistAliasForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect('add_alias')
    else:
        form = ArtistAliasForm()
    return render(request,'artists/add_alias.html',{'form':form})

@login_required
def caller_tunes_view(request):
    query_search=None
    query_search = request.GET.get("song")
    if query_search is not None:
        song_list=ArtistProfile.objects.filter(song__icontains=query_search).order_by('-downloads')
        #print(song_list)
        paginator = Paginator(song_list,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_amount = song_list.aggregate(Sum('total_amount'))['total_amount__sum']
        total_downloads = song_list.aggregate(Sum('downloads'))['downloads__sum']
    else:   
        song_list=ArtistProfile.objects.all().order_by('-downloads')
        paginator = Paginator(song_list,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_amount = song_list.aggregate(Sum('total_amount'))['total_amount__sum']
        total_downloads = song_list.aggregate(Sum('downloads'))['downloads__sum']
    return render(request,'artists/caller_tunes.html', {'page_obj': page_obj,'total_amount':total_amount,'total_downloads':total_downloads})
@login_required
def export_csv_all(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] ='attachement: filename=Report'+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Artists','Song title','Downloads','Rate','Total','Month','Year','Company'])
    
    profiles = ArtistProfile.objects.all()
    total_amount = profiles.aggregate(Sum('total_amount'))['total_amount__sum']
    total_downloads = profiles.aggregate(Sum('downloads'))['downloads__sum']
    for profile in profiles:
        writer.writerow((profile.artist,profile.song,profile.downloads,profile.price,profile.total_amount,profile.month,profile.year,profile.company))
    writer.writerow(['Artists','Song title',total_downloads,'Rate',total_amount,'Month','Year','Company'])
    return response

@login_required
def export_csv(request):
    
    try:
        username = UserProfile.objects.filter(artist_name = request.user)[0]
        #title_list_names = username.user_artist.all()
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    response = HttpResponse(content_type='text/csv')
    
    response['Content-Disposition'] ='attachement: filename=f"{username}"'+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Artists','Song title','Downloads','Rate','Total','Month','Year','Company'])
    
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    song_list=[]
    for x in alias_list:
        song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
    total_amount = sum(song.total_amount for song in songs)
    total_downloads = sum(song.downloads for song in songs)
    profiles=songs
    for profile in profiles:
        writer.writerow((profile.artist,profile.song,profile.downloads,profile.price,profile.total_amount,profile.month,profile.year,profile.company))
    writer.writerow(['Total','Total',total_downloads,'Total',total_amount,'Total','Total','Total'])
    return response

@login_required
def export_csv_admin(request,pk, *args, **kwargs):
    try:
        username = username = UserProfile.objects.get(pk = pk)
        #title_list_names = username.user_artist.all()
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    
    response = HttpResponse(content_type='text/csv')
    
    response['Content-Disposition'] ='attachement: filename=Report'+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Artists','Song title','Downloads','Rate','Total','Month','Year','Company'])
    
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    song_list=[]
    for x in alias_list:
        song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
    total_amount = sum(song.total_amount for song in songs)
    total_downloads = sum(song.downloads for song in songs)
    artist_name = username
    profiles=songs
    for profile in profiles:
        writer.writerow((profile.artist,profile.song,profile.downloads,profile.price,profile.total_amount,profile.month,profile.year,profile.company))
    writer.writerow(['Total','Total',total_downloads,'Total',total_amount,'Total','Total','Total'])
    return response

@login_required
def export_pdf(request, *args, **kwargs):
    try:
        username = UserProfile.objects.filter(artist_name = request.user)[0]
        #title_list_names = username.user_artist.all()
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    #print(alias_list)
    query_search=None
    query_search = request.GET.get("song")
    if query_search is not None:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(song__icontains=query_search))
    else:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
    total_amount = sum(song.total_amount for song in songs)
    total_downloads = sum(song.downloads for song in songs)
    artist_name = username
    template = get_template('artists/artists_details.html')
    html = template.render({'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})
    pdf = render_to_pdf('artists/artists_report_download.html', {'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Report_%s.pdf" %(artist_name)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def export_pdf_admin(request,pk, *args, **kwargs):
    try:
        username = username = UserProfile.objects.get(pk = pk)
        #title_list_names = username.user_artist.all()
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    #print(alias_list)
    query_search=None
    query_search = request.GET.get("song")
    if query_search is not None:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(song__icontains=query_search))
    else:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
    total_amount = sum(song.total_amount for song in songs)
    total_downloads = sum(song.downloads for song in songs)
    artist_name = username
    template = get_template('artists/artists_details.html')
    html = template.render({'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})
    pdf = render_to_pdf('artists/artists_report_download.html', {'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Report_%s.pdf" %(artist_name)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required(login_url='login_view')
def admin_page(request):
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request,'artists/admin_page.html')

@login_required
def user_s(request):
    if not request.user.is_staff:
        raise PermissionDenied
    query_search=None
    query_search = request.GET.get("user")
    if query_search is not None:
        search_user=UserProfile.objects.filter(artist_name__icontains=query_search)
        #print(song_list)
        paginator = Paginator(search_user,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:   
        all_users=UserProfile.objects.all()
        paginator = Paginator(all_users,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,'artists/users.html', {'page_obj':page_obj})

@login_required
def deleter_user(request,pk):
    if not request.user.is_staff:
        raise PermissionDenied
    use_r = UserProfile.objects.get(pk = pk)
    use_rz = User.objects.get(pk = pk)
    use_r.delete()
    use_rz.delete()
    return redirect('user_s')


class Update_user(UpdateView):
    model = UserProfile
    form_class = UserProfileUpdateForm
    template_name = 'artists/update_user.html'
    success_url="/admin_page/all_users/"

@login_required
def all_aliase(request):
    if not request.user.is_staff:
        raise PermissionDenied
    query_search=None
    query_search = request.GET.get("alias")
    if query_search is not None:
        all_aliase=ArtistAlias.objects.filter(alias__icontains=query_search)
        #print(song_list)
        paginator = Paginator(all_aliase,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:   
        all_aliase=ArtistAlias.objects.all()
        paginator = Paginator(all_aliase,30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,'artists/aliases.html', {'page_obj':page_obj})

@login_required
def deleter_aliase(request,slug):
    if not request.user.is_staff:
        raise PermissionDenied
    aliase = ArtistAlias.objects.filter(alias=slug)
    aliase.delete()
    return redirect('all_aliase')
#if request.POST['action'] == 'Update':


class Edit_artist_profile(UpdateView):
    model = ArtistProfile
    form_class = ArtistProfileForm

    template_name = 'artists/edit_artist_profile.html'
    success_url="/admin_page/caller_tunes/"

@login_required
def deleter_caller_tune(request,pk):
    if not request.user.is_staff:
        raise PermissionDenied
    song = ArtistProfile.objects.get(pk = pk)
    song.delete()
    return redirect('caller_tunes_view')

@login_required
def user_details_admin(request,pk):
    if not request.user.is_staff:
        raise PermissionDenied
    try:
        username = UserProfile.objects.get(pk = pk)
    except:
        messages.error(request, 'Profile Not created')
        return redirect('login_view')
    aliases = ArtistAlias.objects.filter(user_profile=username.id)
    alias_list =[]
    for aliase in aliases:
        alias_list.append(aliase.alias)
    #print(alias_list)
    query_search=None
    query_search = request.GET.get("song")
    if query_search is not None:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x).filter(song__icontains=query_search))
    else:
        song_list=[]
        for x in alias_list:
            song_list.append(ArtistProfile.objects.filter(artist__icontains=x))
    song_list_2=[]
    for t in song_list:
        for x in t:
            song_list_2.append(x)
    songs = sorted(song_list_2, key=lambda x: x.downloads, reverse=True)
        #songs = ArtistProfile.objects.filter(artist__startswith=name).order_by('-downloads')
    total_amount = sum(song.total_amount for song in songs)
    total_downloads = sum(song.downloads for song in songs)
    artist_name = username
   
    
    return render(request,'artists/artists_details.html',{'total_amount':total_amount,'artist_name':artist_name,'songs':songs,'total_downloads':total_downloads})
        