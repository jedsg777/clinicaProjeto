from django.contrib import admin
from .models import Cliente, Atendimento, AtendimentoArquivo

class AtendimentoArquivoInline(admin.TabularInline):
    model = AtendimentoArquivo
    extra = 1

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'risco', 'data_cadastro')
    list_filter = ('risco', 'data_cadastro')
    search_fields = ('nome', 'email', 'telefone', 'cpf')

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'data', 'horario', 'risco', 'data_criacao')
    list_filter = ('data', 'risco')
    search_fields = ('cliente__nome', 'descricao')
    inlines = [AtendimentoArquivoInline]

@admin.register(AtendimentoArquivo)
class AtendimentoArquivoAdmin(admin.ModelAdmin):
    list_display = ('nome_original', 'atendimento', 'data_upload')
