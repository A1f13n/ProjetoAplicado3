from django.db import models
from django.db import IntegrityError
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from treinamentos.models import Treinamento
from contas.models import Conta
from django.utils.text import slugify
from unidecode import unidecode


class Colaborador(models.Model):
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14)
    data_nascimento = models.DateField()
    email = models.EmailField(unique=True)
    telefone = models.CharField(blank=True, null=True, max_length=15)
    cargo = models.CharField(max_length=100)
    matricula = models.IntegerField(unique=True, null=True, blank=True)
    data_admissao = models.DateField()

    usuario = models.OneToOneField(Conta, on_delete=models.CASCADE, related_name='colaborador', null=True, blank=True)
    treinamentos = models.ManyToManyField(Treinamento, through='TreinamentoColaborador', related_name='colaboradores_inscritos', blank=True)


# Atribui o ID ao campo matricula e cria e-mail com o nome.matricula/id, depois que o objeto for salvo | FAE: pq é feito dessa forma?
    def save(self, *args, **kwargs): 
        is_novo = self.pk is None
        super().save(*args, **kwargs)
        self.refresh_from_db()


        atualizou_algo = False
        
        if is_novo:
            if not self.matricula:
                self.matricula = self.pk
                atualizou_algo = True

            cargo_normalizado = unidecode(self.cargo.lower())
            if cargo_normalizado in ['tecnico', 'gerenciador']:
                self.criar_usuario()

            nome_slug = slugify(self.nome)
            email_gerado = f"{nome_slug}.{self.matricula}@empresa.com"

            if (Colaborador.objects.filter(email=email_gerado).exclude(pk=self.pk).exists() or
                Conta.objects.filter(email=email_gerado).exists()):
                raise IntegrityError(f"O e-mail automático '{email_gerado}' já está em uso.")
            else:    
                self.email = email_gerado
                atualizou_algo = True
        if atualizou_algo:
            super().save(update_fields=['matricula', 'usuario', 'email']) 




    def criar_usuario(self):
        if self.id and self.matricula:
            nome_slug = slugify(self.nome)
            email_usuario = f"{nome_slug}.{self.matricula}@empresa.com"
            if Conta.objects.filter(email=email_usuario).exists() or Colaborador.objects.filter(email=email_usuario).exclude(pk=self.pk).exists():
                raise IntegrityError(f"E-mail gerado automaticamente já está em uso: {email_usuario}")
            else:
                usuario = Conta.objects.create_user(
                    email=email_usuario,
                    password=self.cpf,
                    nome=self.nome
                )
                self.usuario = usuario




            
    def __str__(self):
        return self.nome
 
    def atualizar_email(self):
        if self.usuario:
            nome_slug = slugify(self.nome)
            novo_email = f"{nome_slug}.{self.matricula}@empresa.com"
            self.usuario.email = novo_email
            self.usuario.save()
            self.email = novo_email
            

class TreinamentoColaborador(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    treinamento = models.ForeignKey(Treinamento, on_delete=models.CASCADE)
    data_conclusao = models.DateField(null=True, blank=True)
    data_validade_treinamento = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('valido', 'Válido'),
        ('vencido', 'Vencido'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    def calcular_validade(self):
        if self.data_conclusao:
            prazo_validade = self.treinamento.prazo_validade  # Pega o prazo de validade do treinamento
            return self.data_conclusao + relativedelta(months=prazo_validade)
        return None

    def atualizar_validade_treinamento(self):
        # Verifica se há data de conclusão
        if self.data_conclusao:
            # Calcula a data de validade
            data_final = self.data_conclusao + relativedelta(months=self.treinamento.prazo_validade)
            self.data_validade_treinamento = data_final

            # Atualiza o status dependendo da validade
            if data_final < timezone.now().date():
                self.status = 'vencido'  # Se a validade está no passado
            else:
                self.status = 'valido'  # Se a validade está no futuro
        else:
            # Se não há data de conclusão, o status é "pendente"
            self.status = 'pendente'

        # Salva o objeto para garantir que as mudanças sejam persistidas no banco de dados
        self.save()

    def __str__(self):
        return f"{self.colaborador.nome} - {self.treinamento.nome}"