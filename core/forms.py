from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from .models import Cidade, Fotografia
import os


            
class CidadeForm(forms.ModelForm):
    class Meta:
        model = Cidade
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar'))    
    

# Renomeando para MediaForm para ser mais genérico        
class MediaForm(forms.ModelForm):
    class Meta:
        model = Fotografia  # Você pode renomear o model para "Media" também
        fields = ['titulo', 'descricao', 'arquivo', 'cidade']  # 'imagem' vira 'arquivo'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Vista panorâmica do centro histórico'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/mp4,video/webm,video/ogg'  # Aceita imagens e vídeos
            }),
            'cidade': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'titulo': 'Título da Mídia',
            'descricao': 'Descrição',
            'arquivo': 'Arquivo (Foto ou Vídeo)',
            'cidade': 'Cidade'    
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordena as cidades alfabeticamente
        self.fields['cidade'].queryset = Cidade.objects.all().order_by('nome')
         
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        
        if arquivo:
            # Verifica o tamanho do arquivo
            # Para vídeos, permitindo até 50MB, para imagens 5MB
            max_size = 50 * 1024 * 1024 if self._is_video_file(arquivo) else 5 * 1024 * 1024
            
            if arquivo.size > max_size:
                size_mb = max_size // (1024 * 1024)
                file_type = "vídeo" if self._is_video_file(arquivo) else "imagem"
                raise ValidationError(f'O arquivo de {file_type} deve ter no máximo {size_mb}MB.')
                
            # Verifica a extensão
            ext = os.path.splitext(arquivo.name)[1].lower()
            valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            valid_video_extensions = ['.mp4', '.webm', '.ogg']
            valid_extensions = valid_image_extensions + valid_video_extensions
            
            if ext not in valid_extensions:
                raise ValidationError(
                    f'Formato não suportado. Use imagens: {", ".join(valid_image_extensions)} '
                    f'ou vídeos: {", ".join(valid_video_extensions)}'
                )
        
        return arquivo
    
    def _is_video_file(self, file):
        """Verifica se o arquivo é um vídeo baseado na extensão"""
        if not file or not hasattr(file, 'name'):
            return False
        ext = os.path.splitext(file.name)[1].lower()
        return ext in ['.mp4', '.webm', '.ogg']

class BuscarFotosForm(forms.Form):
    cidade = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite o nome da cidade (ex: Porto, São Paulo)',
            'autocomplete': 'off',
            'list': 'cidades-datalist'
        }),
        label='',
        required=False
    )                     
    
    def clean_cidade(self):
        cidade = self.cleaned_data.get('cidade', '').strip()
        return cidade