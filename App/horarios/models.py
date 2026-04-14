from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class TipoUsuario(models.Model):
	nombre = models.CharField(max_length=30, unique=True)

	class Meta:
		db_table = 'Tipos_usuarios'
		verbose_name = 'Tipo de usuario'
		verbose_name_plural = 'Tipos de usuario'

	def __str__(self):
		return self.nombre


class Grado(models.Model):
	nombre = models.CharField(max_length=120)

	class Meta:
		db_table = 'Grados'

	def __str__(self):
		return self.nombre


class Asignatura(models.Model):
	class TiposAsignatura(models.TextChoices):
		BASICA = 'B', 'B'
		OBLIGATORIA = 'OB', 'OB'
		OPTATIVA = 'OP', 'OP'
		TFG = 'TFG', 'TFG'

	class Cuatrimestres(models.TextChoices):
		PRIMERO = '1', '1º'
		SEGUNDO = '2', '2º'

	nombre = models.CharField(max_length=120)
	tipo_asignatura = models.CharField(max_length=3, choices=TiposAsignatura.choices)
	anio = models.PositiveSmallIntegerField(
		default=1,
		db_column='Anio',
		validators=[MinValueValidator(1), MaxValueValidator(5)],
	)
	cuatrimestre = models.CharField(max_length=1, choices=Cuatrimestres.choices, default=Cuatrimestres.PRIMERO, db_column='Cuatrimestre')

	class Meta:
		db_table = 'Asignaturas'

	def __str__(self):
		return self.nombre


class GradoAsignatura(models.Model):
	class Especialidades(models.TextChoices):
		INGENIERIA_SOFTWARE = 'IS', 'Ingeniería del Software'
		TECNOLOGIAS_INFORMACION = 'TI', 'Tecnologías de la Información'

	grado = models.ForeignKey(Grado, on_delete=models.CASCADE, db_column='ID_Grado')
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, db_column='ID_Asignatura')
	especialidad = models.CharField(max_length=2, choices=Especialidades.choices, null=True, blank=True, db_column='Especialidad')

	class Meta:
		db_table = 'Grado_Asignatura'
		unique_together = ('grado', 'asignatura')

	def clean(self):
		es_op = self.asignatura and self.asignatura.tipo_asignatura == Asignatura.TiposAsignatura.OPTATIVA
		es_grado_informatica = self.grado and self.grado.nombre.strip().lower() == 'ingeniería informática'

		if es_op and es_grado_informatica and not self.especialidad:
			raise ValidationError('Para asignaturas OP en Ingeniería Informática debes indicar la especialidad.')

		if not (es_op and es_grado_informatica):
			self.especialidad = None

	def __str__(self):
		return f'{self.grado} - {self.asignatura}'


class Profesor(models.Model):
	dni = models.CharField(max_length=12, primary_key=True, db_column='DNI')
	nombre = models.CharField(max_length=120, db_column='Nombre')
	contrato_hasta = models.DateField(db_column='Contrato_hasta', null=True, blank=True)
	contrato_indefinido = models.BooleanField(default=False, db_column='Contrato_indefinido')

	class Meta:
		db_table = 'profesores'

	def clean(self):
		if self.contrato_indefinido:
			self.contrato_hasta = None
		elif not self.contrato_hasta:
			raise ValidationError('Debes indicar una fecha de contrato o marcar indefinido.')

	def __str__(self):
		return f'{self.nombre} ({self.dni})'


class AsignaturaProfesor(models.Model):
	dni = models.ForeignKey(Profesor, on_delete=models.CASCADE, db_column='Dni')
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, db_column='ID_Asignatura')

	class Meta:
		db_table = 'Asignaturas_Profesor'
		unique_together = ('dni', 'asignatura')

	def clean(self):
		if not self.asignatura_id:
			return

		total_grados = GradoAsignatura.objects.filter(asignatura_id=self.asignatura_id).values('grado_id').distinct().count()
		relaciones = AsignaturaProfesor.objects.filter(asignatura_id=self.asignatura_id)
		if self.pk:
			relaciones = relaciones.exclude(pk=self.pk)

		if total_grados <= 1 and relaciones.exists():
			raise ValidationError('Esta asignatura solo puede tener un profesor porque no pertenece a varios grados.')

	def __str__(self):
		return f'{self.dni} - {self.asignatura}'


class AusenciaProfesor(models.Model):
	class DiasSemana(models.TextChoices):
		LUNES = 'LUNES', 'Lunes'
		MARTES = 'MARTES', 'Martes'
		MIERCOLES = 'MIERCOLES', 'Miércoles'
		JUEVES = 'JUEVES', 'Jueves'
		VIERNES = 'VIERNES', 'Viernes'
		SABADO = 'SABADO', 'Sábado'
		DOMINGO = 'DOMINGO', 'Domingo'

	dni = models.ForeignKey(Profesor, on_delete=models.CASCADE, db_column='DNI')
	dia_de_la_semana = models.CharField(max_length=10, choices=DiasSemana.choices, db_column='Dia_de_la_semana')
	hora_inicio = models.TimeField(db_column='Hora_inicio')
	hora_fin = models.TimeField(db_column='Hora_fin')
	turno = models.CharField(max_length=50, db_column='Turno')
	tipo_repeticion = models.CharField(max_length=50, db_column='Tipo_repeticion')
	activo = models.BooleanField(default=True, db_column='Activo')

	class Meta:
		db_table = 'Ausencia_profesor'
		ordering = ['dia_de_la_semana', 'hora_inicio']

	def clean(self):
		if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
			raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

	def __str__(self):
		return f'{self.dni} - {self.get_dia_de_la_semana_display()} {self.hora_inicio}-{self.hora_fin}'


class PerfilUsuario(models.Model):
	usuario = models.OneToOneField(User, on_delete=models.CASCADE)
	tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT)
	profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		db_table = 'Perfil_usuario'

	def __str__(self):
		return f'{self.usuario.username} - {self.tipo_usuario.nombre}'


class HorarioClase(models.Model):
	class DiasSemana(models.TextChoices):
		LUNES = 'LUNES', 'Lunes'
		MARTES = 'MARTES', 'Martes'
		MIERCOLES = 'MIERCOLES', 'Miércoles'
		JUEVES = 'JUEVES', 'Jueves'
		VIERNES = 'VIERNES', 'Viernes'
		SABADO = 'SABADO', 'Sábado'
		DOMINGO = 'DOMINGO', 'Domingo'

	grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
	asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
	profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
	dia_de_la_semana = models.CharField(max_length=10, choices=DiasSemana.choices)
	hora_inicio = models.TimeField()
	hora_fin = models.TimeField()
	aula = models.CharField(max_length=80, blank=True)
	activo = models.BooleanField(default=True)

	class Meta:
		db_table = 'Horarios'
		ordering = ['dia_de_la_semana', 'hora_inicio']

	def clean(self):
		if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
			raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

	def __str__(self):
		return f'{self.asignatura.nombre} - {self.grado.nombre} ({self.get_dia_de_la_semana_display()})'


class SolicitudCambioProfesor(models.Model):
	class EstadoSolicitud(models.TextChoices):
		PENDIENTE = 'PENDIENTE', 'Pendiente'
		APROBADA = 'APROBADA', 'Aprobada'
		RECHAZADA = 'RECHAZADA', 'Rechazada'

	profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
	horario = models.ForeignKey(HorarioClase, on_delete=models.CASCADE)
	mensaje = models.TextField()
	estado = models.CharField(max_length=10, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE)
	creada_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'Solicitud_cambio_profesor'
		ordering = ['-creada_en']

	def __str__(self):
		return f'{self.profesor.dni} - {self.horario.id} - {self.estado}'
