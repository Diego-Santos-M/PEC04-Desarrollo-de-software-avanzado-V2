from django.contrib import admin
from .forms import ProfesorForm
from .models import (
	Asignatura,
	AsignaturaProfesor,
	AusenciaProfesor,
	Grado,
	GradoAsignatura,
	HorarioClase,
	PerfilUsuario,
	Profesor,
	SolicitudCambioProfesor,
	TipoUsuario,
)


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre')
	search_fields = ('nombre',)


@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre')
	search_fields = ('nombre',)


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'tipo_asignatura', 'anio', 'cuatrimestre')
	list_filter = ('tipo_asignatura', 'anio', 'cuatrimestre')
	search_fields = ('nombre', 'tipo_asignatura')


@admin.register(GradoAsignatura)
class GradoAsignaturaAdmin(admin.ModelAdmin):
	list_display = ('id', 'grado', 'asignatura')
	list_select_related = ('grado', 'asignatura')


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
	form = ProfesorForm
	list_display = ('dni', 'nombre', 'contrato_indefinido', 'contrato_hasta')
	search_fields = ('dni', 'nombre')


@admin.register(AsignaturaProfesor)
class AsignaturaProfesorAdmin(admin.ModelAdmin):
	list_display = ('id', 'dni', 'asignatura')
	list_select_related = ('dni', 'asignatura')


@admin.register(AusenciaProfesor)
class AusenciaProfesorAdmin(admin.ModelAdmin):
	list_display = ('id', 'dni', 'dia_de_la_semana', 'hora_inicio', 'hora_fin', 'turno', 'tipo_repeticion', 'activo')
	list_filter = ('dia_de_la_semana', 'turno', 'tipo_repeticion', 'activo')
	search_fields = ('dni__dni', 'dni__nombre', 'turno', 'tipo_repeticion')
	list_select_related = ('dni',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'tipo_usuario', 'profesor')
	list_filter = ('tipo_usuario',)
	search_fields = ('usuario__username', 'profesor__dni', 'profesor__nombre')


@admin.register(HorarioClase)
class HorarioClaseAdmin(admin.ModelAdmin):
	list_display = ('id', 'grado', 'asignatura', 'profesor', 'dia_de_la_semana', 'hora_inicio', 'hora_fin', 'aula', 'activo')
	list_filter = ('grado', 'dia_de_la_semana', 'activo')
	search_fields = ('asignatura__nombre', 'profesor__nombre', 'profesor__dni', 'aula')
	list_select_related = ('grado', 'asignatura', 'profesor')


@admin.register(SolicitudCambioProfesor)
class SolicitudCambioProfesorAdmin(admin.ModelAdmin):
	list_display = ('id', 'profesor', 'horario', 'estado', 'creada_en')
	list_filter = ('estado', 'creada_en')
	search_fields = ('profesor__dni', 'profesor__nombre', 'horario__asignatura__nombre', 'mensaje')
	list_select_related = ('profesor', 'horario', 'horario__asignatura')
