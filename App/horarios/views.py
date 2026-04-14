from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

from .forms import AsignaturaForm, AsignaturaProfesorForm, GradoAsignaturaForm, ProfesorForm, RegistroUsuarioForm, SolicitudCambioProfesorForm
from .models import (
    Asignatura,
    AsignaturaProfesor,
    Grado,
    GradoAsignatura,
    HorarioClase,
    PerfilUsuario,
    Profesor,
    SolicitudCambioProfesor,
)


def obtener_rol(usuario):
    if usuario.is_superuser:
        return 'admin'
    try:
        return usuario.perfilusuario.tipo_usuario.nombre.lower()
    except PerfilUsuario.DoesNotExist:
        return None


class RolRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    rol_requerido = None

    def test_func(self):
        if self.request.user.is_superuser and self.rol_requerido == 'admin':
            return True
        return obtener_rol(self.request.user) == self.rol_requerido


class RegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'horarios/registro.html'
    success_url = reverse_lazy('horarios:inicio')

    def form_valid(self, form):
        usuario = form.save()
        PerfilUsuario.objects.create(
            usuario=usuario,
            tipo_usuario=form.cleaned_data['tipo_usuario'],
            profesor=form.cleaned_data.get('profesor'),
        )
        login(self.request, usuario)
        return redirect('horarios:inicio')


class InicioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        rol = obtener_rol(request.user)
        if rol == 'admin':
            return redirect('horarios:admin_panel')
        if rol == 'profesor':
            return redirect('horarios:profesor_horarios')
        if rol == 'alumno':
            return redirect('horarios:alumno_horarios')
        return redirect('horarios:login')


class AppLoginView(LoginView):
    template_name = 'horarios/login.html'


class AppLogoutView(LogoutView):
    next_page = reverse_lazy('horarios:login')


class AdminPanelView(RolRequiredMixin, TemplateView):
    rol_requerido = 'admin'
    template_name = 'horarios/admin_panel.html'


class GradoListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = Grado
    template_name = 'horarios/grado_lista.html'
    context_object_name = 'grados'


class GradoCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = Grado
    fields = ['nombre']
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_grados')


class GradoUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = Grado
    fields = ['nombre']
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_grados')


class AsignaturaListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = Asignatura
    template_name = 'horarios/asignatura_lista.html'
    context_object_name = 'asignaturas'


class AsignaturaCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = Asignatura
    form_class = AsignaturaForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_asignaturas')


class AsignaturaUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = Asignatura
    form_class = AsignaturaForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_asignaturas')


class AsignaturaDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, pk):
        asignatura = get_object_or_404(Asignatura, pk=pk)
        asignatura.delete()
        return redirect('horarios:admin_asignaturas')


class ProfesorListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = Profesor
    template_name = 'horarios/profesor_lista.html'
    context_object_name = 'profesores'


class ProfesorCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = Profesor
    form_class = ProfesorForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_profesores')


class ProfesorUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = Profesor
    form_class = ProfesorForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_profesores')


class ProfesorDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, pk):
        profesor = get_object_or_404(Profesor, pk=pk)
        profesor.delete()
        return redirect('horarios:admin_profesores')


class HorarioAdminListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = HorarioClase
    template_name = 'horarios/horario_admin_lista.html'
    context_object_name = 'horarios'


class HorarioAdminCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = HorarioClase
    fields = ['grado', 'asignatura', 'profesor', 'dia_de_la_semana', 'hora_inicio', 'hora_fin', 'aula', 'activo']
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_horarios')


class HorarioAdminUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = HorarioClase
    fields = ['grado', 'asignatura', 'profesor', 'dia_de_la_semana', 'hora_inicio', 'hora_fin', 'aula', 'activo']
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_horarios')


class HorarioAdminDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, pk):
        horario = get_object_or_404(HorarioClase, pk=pk)
        horario.delete()
        return redirect('horarios:admin_horarios')


class GradoAsignaturaListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = GradoAsignatura
    template_name = 'horarios/grado_asignatura_lista.html'
    context_object_name = 'relaciones'

    def get_queryset(self):
        return GradoAsignatura.objects.select_related('grado', 'asignatura')


class GradoAsignaturaCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = GradoAsignatura
    form_class = GradoAsignaturaForm
    template_name = 'horarios/grado_asignatura_formulario.html'
    success_url = reverse_lazy('horarios:admin_grado_asignaturas')


class GradoAsignaturaUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = GradoAsignatura
    form_class = GradoAsignaturaForm
    template_name = 'horarios/grado_asignatura_formulario.html'
    success_url = reverse_lazy('horarios:admin_grado_asignaturas')


class AsignaturasDisponiblesPorGradoView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def get(self, request, grado_id):
        asignatura_actual_id = request.GET.get('actual')
        usadas = GradoAsignatura.objects.filter(grado_id=grado_id).values_list('asignatura_id', flat=True)
        queryset = Asignatura.objects.exclude(id__in=usadas)
        if asignatura_actual_id:
            queryset = (Asignatura.objects.filter(id=asignatura_actual_id) | queryset).distinct()

        data = [
            {
                'id': asignatura.id,
                'nombre': asignatura.nombre,
                'tipo_asignatura': asignatura.tipo_asignatura,
            }
            for asignatura in queryset.order_by('nombre')
        ]
        return JsonResponse({'asignaturas': data})


class GradoAsignaturaDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, pk):
        relacion = get_object_or_404(GradoAsignatura, pk=pk)
        relacion.delete()
        return redirect('horarios:admin_grado_asignaturas')


class AsignaturaProfesorListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = AsignaturaProfesor
    template_name = 'horarios/asignatura_profesor_lista.html'
    context_object_name = 'relaciones'

    def get_queryset(self):
        return AsignaturaProfesor.objects.select_related('dni', 'asignatura')


class AsignaturaProfesorCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'admin'
    model = AsignaturaProfesor
    form_class = AsignaturaProfesorForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_asignatura_profesores')


class AsignaturaProfesorUpdateView(RolRequiredMixin, UpdateView):
    rol_requerido = 'admin'
    model = AsignaturaProfesor
    form_class = AsignaturaProfesorForm
    template_name = 'horarios/formulario_generico.html'
    success_url = reverse_lazy('horarios:admin_asignatura_profesores')


class AsignaturaProfesorDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, pk):
        relacion = get_object_or_404(AsignaturaProfesor, pk=pk)
        relacion.delete()
        return redirect('horarios:admin_asignatura_profesores')


class AlumnoHorarioListView(RolRequiredMixin, ListView):
    rol_requerido = 'alumno'
    model = HorarioClase
    template_name = 'horarios/alumno_horarios.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        return HorarioClase.objects.filter(activo=True).select_related('grado', 'asignatura', 'profesor')


class ProfesorHorarioListView(RolRequiredMixin, ListView):
    rol_requerido = 'profesor'
    model = HorarioClase
    template_name = 'horarios/profesor_horarios.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        perfil = self.request.user.perfilusuario
        if perfil.profesor:
            return HorarioClase.objects.filter(profesor=perfil.profesor, activo=True).select_related('grado', 'asignatura', 'profesor')
        return HorarioClase.objects.none()


class SolicitudProfesorCreateView(RolRequiredMixin, CreateView):
    rol_requerido = 'profesor'
    form_class = SolicitudCambioProfesorForm
    template_name = 'horarios/solicitud_formulario.html'
    success_url = reverse_lazy('horarios:profesor_horarios')

    def dispatch(self, request, *args, **kwargs):
        self.horario = get_object_or_404(HorarioClase, pk=kwargs['horario_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        perfil = self.request.user.perfilusuario
        if not perfil.profesor:
            form.add_error(None, 'Tu usuario no está vinculado a un profesor.')
            return self.form_invalid(form)
        solicitud = form.save(commit=False)
        solicitud.profesor = perfil.profesor
        solicitud.horario = self.horario
        solicitud.save()
        self.object = solicitud
        return redirect(self.success_url)


class SolicitudAdminListView(RolRequiredMixin, ListView):
    rol_requerido = 'admin'
    model = SolicitudCambioProfesor
    template_name = 'horarios/solicitudes_admin.html'
    context_object_name = 'solicitudes'


class SolicitudCambiarEstadoView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, solicitud_id, estado):
        solicitud = get_object_or_404(SolicitudCambioProfesor, pk=solicitud_id)
        if estado in ['APROBADA', 'RECHAZADA']:
            solicitud.estado = estado
            solicitud.save(update_fields=['estado'])
        return redirect('horarios:admin_solicitudes')


class SolicitudDeleteView(RolRequiredMixin, View):
    rol_requerido = 'admin'

    def post(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudCambioProfesor, pk=solicitud_id)
        solicitud.delete()
        return redirect('horarios:admin_solicitudes')
