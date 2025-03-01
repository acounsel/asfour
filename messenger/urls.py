from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('tags/', include([
        path('', views.TagList.as_view(), name='tag-list'),
        path('add/', views.TagCreate.as_view(), name='tag-create'),
        path('<pk>/', include([
            path('', views.TagDetail.as_view(), name='tag-detail'),
            path('update/', views.TagUpdate.as_view(), name='tag-update'),
            path('delete/', views.TagDelete.as_view(), name='tag-delete'),
        ])),
    ])),
    path('contacts/', include([
        path('', views.ContactList.as_view(), name='contact-list'),
        path('add/', views.ContactCreate.as_view(), name='contact-create'),
        path('import/', views.ContactImport.as_view(), name='contact-import'),
        path('export/', views.ContactExport.as_view(), name='contact-export'),
        path('<pk>/', include([
            path('', views.ContactDetail.as_view(), name='contact-detail'),
            path('update/', views.ContactUpdate.as_view(), name='contact-update'),
            path('delete/', views.ContactDelete.as_view(), name='contact-delete'),
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
            path('delete/', views.MessageDelete.as_view(), name='message-delete'),
        ])),
        path('call/', include([
            path('<pk>/voice-call/save/<msg_id>', 
                views.RecordCall.as_view(), name='record-call'),
            path('<pk>/voice-call/<msg_id>', 
                views.VoiceCall.as_view(), name='voice-call'),
        ])),
    ])),
    path('autoreplies/', include([
        path('', views.AutoreplyList.as_view(), name='autoreply-list'),
        path('add/',views.AutoreplyCreate.as_view(), name='autoreply-create'),
        path('<pk>/', include([
            path('', views.AutoreplyUpdate.as_view(), name='autoreply-update'),
        ])),
    ])),
    path('invoice/', include([
        path('', views.InvoiceList.as_view(), name='invoice-list'),
        path('<uuid>/', views.InvoiceDetail.as_view(), name='invoice-detail'),
    ])),
    path('conference/<session_id>/', views.Conference.as_view(), name='conference-call'),
    # path('chatbot/', views.ChatBot.as_view(), name='chatbot'),
    path('status-callback/<int:pk>', views.StatusCallback.as_view(), name='status-callback'),
    path('response/<medium>/<int:pk>/', views.HarvestResponse.as_view(), name='harvest-response'),
    path('responses/', include([
        path('', views.ResponseList.as_view(), name='response-list'),
        path('export/', views.ResponseExport.as_view(), name='response-export'),
    ])),
    path('organization/', views.OrganizationUpdate.as_view(), name='organization-update'),
    path('user/', views.UserUpdate.as_view(), name='user-update'),
]