from django.urls import path, include

from .views import cdr, config

app_name = 'fs'

urlpatterns = [
    # config
    # cdr
    path('', config.ConfigViews.as_view()),
    path('api/', include('cloud.fs.views.api', namespace='api')),
    path('cdr', cdr.CdrViews.as_view()),
]
