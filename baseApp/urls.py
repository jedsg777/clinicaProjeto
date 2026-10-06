from django.urls import path
from .views import (
    HomeView,
    CadastrarClienteView,
    CadastrarAtendimentoView,
    DetalhesAtendimentoView
)

app_name = 'baseApp'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('cliente/cadastrar/', CadastrarClienteView.as_view(), name='cadastrar_cliente'),
    path('atendimento/cadastrar/', CadastrarAtendimentoView.as_view(), name='cadastrar_atendimento'),
    path('atendimento/<int:pk>/detalhes/', DetalhesAtendimentoView.as_view(), name='detalhes_atendimento'),
]
