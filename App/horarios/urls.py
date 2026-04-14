from django.urls import path

from .views import (
    AdminPanelView,
    AlumnoHorarioListView,
    AsignaturaProfesorCreateView,
    AsignaturaProfesorDeleteView,
    AsignaturaProfesorListView,
    AsignaturaProfesorUpdateView,
    AppLoginView,
    AppLogoutView,
    AsignaturaCreateView,
    AsignaturaDeleteView,
    AsignaturaListView,
    AsignaturaUpdateView,
    AsignaturasDisponiblesPorGradoView,
    GradoCreateView,
    GradoAsignaturaCreateView,
    GradoAsignaturaDeleteView,
    GradoAsignaturaListView,
    GradoAsignaturaUpdateView,
    GradoListView,
    GradoUpdateView,
    HorarioAdminCreateView,
    HorarioAdminDeleteView,
    HorarioAdminListView,
    HorarioAdminUpdateView,
    InicioView,
    ProfesorCreateView,
    ProfesorDeleteView,
    ProfesorHorarioListView,
    ProfesorListView,
    ProfesorUpdateView,
    RegistroView,
    SolicitudAdminListView,
    SolicitudCambiarEstadoView,
    SolicitudDeleteView,
    SolicitudProfesorCreateView,
)

app_name = 'horarios'

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('login/', AppLoginView.as_view(), name='login'),
    path('logout/', AppLogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),

    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('panel-admin/grados/', GradoListView.as_view(), name='admin_grados'),
    path('panel-admin/grados/nuevo/', GradoCreateView.as_view(), name='admin_grado_nuevo'),
    path('panel-admin/grados/<int:pk>/editar/', GradoUpdateView.as_view(), name='admin_grado_editar'),

    path('panel-admin/asignaturas/', AsignaturaListView.as_view(), name='admin_asignaturas'),
    path('panel-admin/asignaturas/nueva/', AsignaturaCreateView.as_view(), name='admin_asignatura_nueva'),
    path('panel-admin/asignaturas/<int:pk>/editar/', AsignaturaUpdateView.as_view(), name='admin_asignatura_editar'),
    path('panel-admin/asignaturas/<int:pk>/eliminar/', AsignaturaDeleteView.as_view(), name='admin_asignatura_eliminar'),

    path('panel-admin/profesores/', ProfesorListView.as_view(), name='admin_profesores'),
    path('panel-admin/profesores/nuevo/', ProfesorCreateView.as_view(), name='admin_profesor_nuevo'),
    path('panel-admin/profesores/<str:pk>/editar/', ProfesorUpdateView.as_view(), name='admin_profesor_editar'),
    path('panel-admin/profesores/<str:pk>/eliminar/', ProfesorDeleteView.as_view(), name='admin_profesor_eliminar'),

    path('panel-admin/horarios/', HorarioAdminListView.as_view(), name='admin_horarios'),
    path('panel-admin/horarios/nuevo/', HorarioAdminCreateView.as_view(), name='admin_horario_nuevo'),
    path('panel-admin/horarios/<int:pk>/editar/', HorarioAdminUpdateView.as_view(), name='admin_horario_editar'),
    path('panel-admin/horarios/<int:pk>/eliminar/', HorarioAdminDeleteView.as_view(), name='admin_horario_eliminar'),

    path('panel-admin/grado-asignaturas/', GradoAsignaturaListView.as_view(), name='admin_grado_asignaturas'),
    path('panel-admin/grado-asignaturas/nueva/', GradoAsignaturaCreateView.as_view(), name='admin_grado_asignatura_nueva'),
    path('panel-admin/grado-asignaturas/<int:pk>/editar/', GradoAsignaturaUpdateView.as_view(), name='admin_grado_asignatura_editar'),
    path('panel-admin/grado-asignaturas/<int:pk>/eliminar/', GradoAsignaturaDeleteView.as_view(), name='admin_grado_asignatura_eliminar'),
    path('panel-admin/grado-asignaturas/disponibles/<int:grado_id>/', AsignaturasDisponiblesPorGradoView.as_view(), name='admin_grado_asignaturas_disponibles'),

    path('panel-admin/asignatura-profesores/', AsignaturaProfesorListView.as_view(), name='admin_asignatura_profesores'),
    path('panel-admin/asignatura-profesores/nueva/', AsignaturaProfesorCreateView.as_view(), name='admin_asignatura_profesor_nueva'),
    path('panel-admin/asignatura-profesores/<int:pk>/editar/', AsignaturaProfesorUpdateView.as_view(), name='admin_asignatura_profesor_editar'),
    path('panel-admin/asignatura-profesores/<int:pk>/eliminar/', AsignaturaProfesorDeleteView.as_view(), name='admin_asignatura_profesor_eliminar'),

    path('alumno/horarios/', AlumnoHorarioListView.as_view(), name='alumno_horarios'),
    path('profesor/horarios/', ProfesorHorarioListView.as_view(), name='profesor_horarios'),
    path('profesor/horarios/<int:horario_id>/solicitar-cambio/', SolicitudProfesorCreateView.as_view(), name='profesor_solicitar_cambio'),

    path('panel-admin/solicitudes/', SolicitudAdminListView.as_view(), name='admin_solicitudes'),
    path('panel-admin/solicitudes/<int:solicitud_id>/<str:estado>/', SolicitudCambiarEstadoView.as_view(), name='admin_solicitud_estado'),
    path('panel-admin/solicitudes/<int:solicitud_id>/eliminar/', SolicitudDeleteView.as_view(), name='admin_solicitud_eliminar'),
]