from django.urls import path
from . import views

app_name = 'weatherco2app'  # アプリケーション名を指定

urlpatterns = [
    path('', views.user_input_view, name='user_input'),  # ユーザー入力フォーム
    path('submit/', views.submit_data, name='submit_data'),  # データ送信後の処理
]
