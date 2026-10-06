from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from baseApp.models import Cliente, Atendimento, AtendimentoArquivo
from django.core.files.uploadedfile import SimpleUploadedFile

class ClinicaProjetoTestCase(TestCase):
    def setUp(self):
        self.client_obj = Cliente.objects.create(
            nome='João da Silva',
            email='joao@email.com',
            telefone='11999998888',
            risco='alto',
            observacoes='Paciente com histórico importante.'
        )

        self.atendimento_obj = Atendimento.objects.create(
            cliente=self.client_obj,
            data=date.today(),
            horario=time(9, 30),
            descricao='Consulta médica de rotina.',
            risco='alto'
        )

    def test_cliente_sem_senha(self):
        """Verifica que o cliente não tem campo de senha e é um cadastro simples"""
        self.assertEqual(self.client_obj.nome, 'João da Silva')
        self.assertFalse(hasattr(self.client_obj, 'password'))

    def test_home_view(self):
        """Verifica o carregamento da HomeView com CBV"""
        url = reverse('baseApp:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cronograma diário (24h)')
        self.assertContains(response, 'João da Silva')

    def test_cadastrar_cliente_cbv(self):
        """Verifica o endpoint de cadastro de cliente"""
        url = reverse('baseApp:cadastrar_cliente')
        data = {
            'nome': 'Maria Souza',
            'email': 'maria@email.com',
            'telefone': '11977776666',
            'risco': 'medio',
            'observacoes': 'Nova paciente'
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Cliente.objects.filter(nome='Maria Souza').exists())

    def test_cadastrar_atendimento_cbv(self):
        """Verifica o endpoint de cadastro de atendimento com upload de arquivo"""
        url = reverse('baseApp:cadastrar_atendimento')
        dummy_file = SimpleUploadedFile("exemplo_laudo.pdf", b"Conteudo do laudo PDF", content_type="application/pdf")
        data = {
            'cliente_id': self.client_obj.id,
            'data': date.today().strftime('%Y-%m-%d'),
            'horario': '14:00',
            'descricao': 'Atendimento com entrega de exames.',
            'risco': 'alto',
            'arquivos': [dummy_file]
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        atendimento = Atendimento.objects.get(horario=time(14, 0))
        self.assertEqual(atendimento.cliente, self.client_obj)
        self.assertEqual(atendimento.arquivos.count(), 1)
        self.assertEqual(atendimento.arquivos.first().nome_original, 'exemplo_laudo.pdf')

    def test_detalhes_atendimento_cbv(self):
        """Verifica o endpoint de detalhes do atendimento"""
        url = reverse('baseApp:detalhes_atendimento', kwargs={'pk': self.atendimento_obj.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['cliente'], 'João da Silva')
        self.assertEqual(json_data['horario'], '09:30')
