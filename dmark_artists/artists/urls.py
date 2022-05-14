from unicodedata import name
from django.urls import path
from .views import artists_details,company_detail,signup_view,login_view,month_detail,song_detail,add_alias,company_detail,upload_data,caller_tunes_view,export_csv,export_pdf,admin_page
from .views import user_s,deleter_user,Update_user,all_aliase,deleter_aliase,Edit_artist_profile,deleter_caller_tune,user_details_admin,export_pdf_admin
from django.contrib.auth import views as auth_views

urlpatterns =[
    path('details/',artists_details,name="artists_details"),
    path('signup/',signup_view,name="sign_up"),
    path('login/',login_view,name="login_view"),
    path('logout/',login_view,name="logout"),
    path('upload/',upload_data,name="upload_data"),
    path('month/',month_detail,name='month_detail'),
    path("download/", export_pdf,name='export_pdf'),
    path("download_pdf/report/", export_csv,name='export_csv'),
    path("admin_page/download_report/<int:pk>/", export_pdf_admin,name='export_pdf_admin'),
    
    path("admin_page/", admin_page,name='admin_page'),
    path("admin_page/all_users/", user_s,name='user_s'),
    path("admin_page/all_users/<int:pk>/", user_details_admin,name='user_details_admin'),
    path("admin_page/all_users/delete/<int:pk>/", deleter_user,name='deleter_user'),
    path("admin_page/all_users/update/<int:pk>/", Update_user.as_view(),name='update_user'),
    path("admin_page/all_aliase/", all_aliase,name='all_aliase'),
    path("admin_page/all_aliase/add_alias/", add_alias,name='add_alias'),
    path("admin_page/all_aliase/delete/<str:slug>/", deleter_aliase,name='deleter_aliase'),
    path("admin_page/caller_tunes/", caller_tunes_view,name='caller_tunes_view'),
    path("admin_page/caller_tunes/edit/<int:pk>/",Edit_artist_profile.as_view(),name='edit_artist_profile'),
    path("admin_page/caller_tunes/delete/<int:pk>/", deleter_caller_tune,name='deleter_caller_tune'),
    


    
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='artists/password_reset.html'),name="reset_password"),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name='artists/password_reset_sent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='artists/password_reset_form.html'),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='artists/password_reset_done.html'),name="password_reset_complete"),
    
    path("<str:slug>/", month_detail,name='month_detail'),
    path("songdetail/<str:slug>/", song_detail,name='song_detail'),
    path("company/<str:slug>/", company_detail,name='company_detail'),
]