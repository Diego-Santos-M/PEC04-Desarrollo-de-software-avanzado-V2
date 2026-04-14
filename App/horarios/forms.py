from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Asignatura, AsignaturaProfesor, GradoAsignatura, Profesor, SolicitudCambioProfesor, TipoUsuario


class RegistroUsuarioForm(UserCreationForm):
    tipo_usuario = forms.ModelChoiceField(queryset=TipoUsuario.objects.all())
    profesor = forms.ModelChoiceField(queryset=Profesor.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre_tipo in ['admin', 'profesor', 'alumno']:
            TipoUsuario.objects.get_or_create(nombre=nombre_tipo)
        self.fields['tipo_usuario'].queryset = TipoUsuario.objects.all().order_by('nombre')
        self.fields['profesor'].queryset = Profesor.objects.all().order_by('nombre')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'tipo_usuario', 'profesor')

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        profesor = cleaned_data.get('profesor')

        if tipo_usuario and tipo_usuario.nombre.lower() == 'profesor' and not profesor:
            self.add_error('profesor', 'Debes vincular un profesor para este tipo de usuario.')

        return cleaned_data


class SolicitudCambioProfesorForm(forms.ModelForm):
    class Meta:
        model = SolicitudCambioProfesor
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4}),
        }


class AsignaturaForm(forms.ModelForm):
    anio = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)])
    tipo_asignatura = forms.ChoiceField(choices=[('B', 'B'), ('OB', 'OB'), ('OP', 'OP'), ('TFG', 'TFG')])
    cuatrimestre = forms.ChoiceField(choices=[('1', '1º'), ('2', '2º')])

    class Meta:
        model = Asignatura
        fields = ['nombre', 'tipo_asignatura', 'anio', 'cuatrimestre']


class ProfesorForm(forms.ModelForm):
    contrato_indefinido = forms.BooleanField(required=False)
    contrato_hasta = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
        required=False,
    )

    class Meta:
        model = Profesor
        fields = ['dni', 'nombre', 'contrato_indefinido', 'contrato_hasta']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrato_indefinido'].label = 'Indefinido'
        self.fields['contrato_hasta'].help_text = 'Formato: dd/mm/aaaa. Déjalo vacío si es indefinido.'

    def clean(self):
        cleaned_data = super().clean()
        contrato_indefinido = cleaned_data.get('contrato_indefinido')
        contrato_hasta = cleaned_data.get('contrato_hasta')

        if contrato_indefinido:
            cleaned_data['contrato_hasta'] = None
        elif not contrato_hasta:
            self.add_error('contrato_hasta', 'Debes indicar una fecha en formato dd/mm/aaaa o marcar indefinido.')

        return cleaned_data

    def save(self, commit=True):
        profesor = super().save(commit=False)
        profesor.contrato_indefinido = self.cleaned_data.get('contrato_indefinido', False)
        profesor.contrato_hasta = self.cleaned_data.get('contrato_hasta')
        if commit:
            profesor.save()
        return profesor


class GradoAsignaturaForm(forms.ModelForm):
    class Meta:
        model = GradoAsignatura
        fields = ['grado', 'asignatura', 'especialidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['asignatura'].queryset = Asignatura.objects.none()
        self.fields['especialidad'].required = False

        grado_id = self.data.get('grado')
        if grado_id:
            usadas = GradoAsignatura.objects.filter(grado_id=grado_id).values_list('asignatura_id', flat=True)
            queryset = Asignatura.objects.exclude(id__in=usadas)
            if self.instance and self.instance.pk and str(self.instance.grado_id) == str(grado_id):
                queryset = Asignatura.objects.filter(id=self.instance.asignatura_id) | queryset
            self.fields['asignatura'].queryset = queryset.distinct().order_by('nombre')
        elif self.instance and self.instance.pk:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(id=self.instance.asignatura_id)

    def clean(self):
        cleaned_data = super().clean()
        grado = cleaned_data.get('grado')
        asignatura = cleaned_data.get('asignatura')
        if not grado or not asignatura:
            return cleaned_data

        existe = GradoAsignatura.objects.filter(grado=grado, asignatura=asignatura)
        if self.instance and self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            self.add_error('asignatura', 'Esa asignatura ya está asociada al grado seleccionado.')

        es_op = asignatura.tipo_asignatura == Asignatura.TiposAsignatura.OPTATIVA
        es_grado_informatica = grado.nombre.strip().lower() == 'ingeniería informática'
        especialidad = cleaned_data.get('especialidad')

        if es_op and es_grado_informatica and not especialidad:
            self.add_error('especialidad', 'Debes elegir especialidad para asignaturas OP en Ingeniería Informática.')

        if not (es_op and es_grado_informatica):
            cleaned_data['especialidad'] = None

        return cleaned_data


class AsignaturaProfesorForm(forms.ModelForm):
    class Meta:
        model = AsignaturaProfesor
        fields = ['dni', 'asignatura']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        asignaturas_disponibles_ids = []
        for asignatura in Asignatura.objects.all().order_by('nombre'):
            total_grados = GradoAsignatura.objects.filter(asignatura=asignatura).values('grado').distinct().count()
            relaciones = AsignaturaProfesor.objects.filter(asignatura=asignatura)

            if self.instance and self.instance.pk:
                relaciones = relaciones.exclude(pk=self.instance.pk)

            permite_varios_profesores = total_grados > 1
            sin_profesor_asignado = not relaciones.exists()

            if permite_varios_profesores or sin_profesor_asignado:
                asignaturas_disponibles_ids.append(asignatura.id)

        queryset = Asignatura.objects.filter(id__in=asignaturas_disponibles_ids).order_by('nombre')

        if self.instance and self.instance.pk:
            queryset = (Asignatura.objects.filter(pk=self.instance.asignatura_id) | queryset).distinct().order_by('nombre')

        self.fields['asignatura'].queryset = queryset
