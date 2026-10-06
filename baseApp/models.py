from django.db import models
import os

RISCO_CHOICES = [
    ('alto', 'Alto'),
    ('medio', 'Médio'),
    ('baixo', 'Baixo'),
]

class Cliente(models.Model):
    """
    Modelo de Paciente / Cliente.
    Não possui login/senha, pois é um cadastro simples de paciente mantido pela clínica.
    """
    nome = models.CharField(max_length=150, verbose_name='Nome Completo')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    risco = models.CharField(
        max_length=10,
        choices=RISCO_CHOICES,
        default='medio',
        verbose_name='Nível de Risco'
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_risco_display()})"


class Atendimento(models.Model):
    """
    Modelo de Atendimento agendado / registrado no cronograma diário.
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='atendimentos',
        verbose_name='Cliente'
    )
    data = models.DateField(verbose_name='Data do Atendimento')
    horario = models.TimeField(verbose_name='Horário do Atendimento')
    descricao = models.TextField(verbose_name='Descrição do Atendimento')
    risco = models.CharField(
        max_length=10,
        choices=RISCO_CHOICES,
        default='medio',
        verbose_name='Categoria/Risco'
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')

    class Meta:
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'
        ordering = ['data', 'horario']

    def __str__(self):
        return f"Atendimento: {self.cliente.nome} em {self.data.strftime('%d/%m/%Y')} às {self.horario.strftime('%H:%M')}"

    @property
    def horario_formatado(self):
        return self.horario.strftime('%H:%M')


def caminho_upload_atendimento(instance, filename):
    return f"atendimentos/{instance.atendimento.id}/{filename}"


class AtendimentoArquivo(models.Model):
    """
    Arquivos (imagens, .pdf, .docx) anexados ao Atendimento para consulta no histórico.
    """
    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name='arquivos',
        verbose_name='Atendimento'
    )
    arquivo = models.FileField(
        upload_to=caminho_upload_atendimento,
        verbose_name='Arquivo'
    )
    nome_original = models.CharField(max_length=255, verbose_name='Nome do Arquivo')
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name='Data de Upload')

    class Meta:
        verbose_name = 'Arquivo de Atendimento'
        verbose_name_plural = 'Arquivos de Atendimento'

    def __str__(self):
        return self.nome_original

    @property
    def extensao(self):
        _, ext = os.path.splitext(self.nome_original)
        return ext.lower()
