from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('contacts/', include([
        path('', views.ContactList.as_view(), name='contact-list'),
        path('add/', views.ContactCreate.as_view(), name='contact-create'),
        path('import/', views.ContactImport.as_view(), name='contact-import'),
        # path('export/', views.CommitmentExport.as_view(), name='commitment-export'),
        path('<pk>/', include([
            path('', views.ContactDetail.as_view(), name='contact-detail'),
            path('update/', views.ContactUpdate.as_view(), name='contact-update'),
        ])),
    ])),
    path('messages/', include([
        path('', views.MessageList.as_view(), name='message-list'),
        path('log/',views.MessageLogList.as_view(), name='messagelog-list'),
        path('add/',views.MessageCreate.as_view(), name='message-create'),
        # path('export/', views.CommitmentExport.as_view(), name='commitment-export'),
        path('<pk>/', include([
            path('', views.MessageDetail.as_view(), name='message-detail'),
            path('update/', views.MessageUpdate.as_view(), name='message-update'),
            path('send/', views.MessageSend.as_view(), name='message-send'),
        ])),
    ])),
    path('response/<int:pk>/', views.HarvestResponse.as_view(), name='harvest-response'),
    path('responses/', include([
        path('', views.ResponseList.as_view(), name='response-list'),
    ])),
    path('organization/', views.OrganizationUpdate.as_view(), name='organization-update'),
    path('user/', views.UserUpdate.as_view(), name='user-update'),
]