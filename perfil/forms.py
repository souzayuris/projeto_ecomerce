from django import forms
from django.contrib.auth.models import User
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


# Cria o formulário de Usuário
class UserForm(forms.ModelForm):
    # Cria o campo password

    password = forms.CharField(
        required=False,  # retira a obrigação de preencher o campo Passowrd
        widget=forms.PasswordInput(),
        label='Senha',  # Altera o nome de exibição do campo senha
        help_text='.'
    )

    password2 = forms.CharField(
        required=False,  # retira a obrigação de preencher o campo Passowrd
        widget=forms.PasswordInput(),
        label='Confirmação senha'  # Altera o nome de exibição do campo senha
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        usuario_data = cleaned.get('username')
        print(f'Usuario_data: {usuario_data}')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        email_data = cleaned.get('email')

        usuario_db = User.objects.filter(username=usuario_data).first()
        # print para debugar
        if usuario_db:
            print(f'Usuario_db.username = {usuario_db.username}')
            print(f'Usuario_db = {usuario_db}')
            print(f'email cadastrado: {usuario_db.email}')

        email_db = User.objects.filter(email=email_data).first()
        # print para debugar
        print(f'email no formulario = {email_data}')
        print(f'email_db = {email_db}')
        if email_db:
            print(f'email_db.email = {email_db.email}')

        error_msg_user_exists = 'Usuário já existe'
        error_msg_email_exists = 'E-mail já existe'
        error_msg_password_match = 'As senhas não conferem'
        error_msg_password_short = 'A senha precisa ter no mínimo 6 caracteres'
        error_msg_required_field = 'Este campo é obrigatório'

        # Para Usuários logados: atualizacao
        if self.usuario:
            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msgs['password'] = error_msg_required_field

            if not password2_data:
                validation_error_msgs['password2'] = error_msg_required_field

            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password2'] = error_msg_password_match
                    validation_error_msgs['password'] = error_msg_password_match

                # if len(password_data) < 6:
                #    validation_error_msgs['password'] = error_msg_password_short

        # Usuarios nao logados: cadastro
        else:
            if usuario_db:
                validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                if email_data == email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if password_data != password2_data:
                validation_error_msgs['password2'] = error_msg_password_match
                validation_error_msgs['password'] = error_msg_password_match

            if len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))
