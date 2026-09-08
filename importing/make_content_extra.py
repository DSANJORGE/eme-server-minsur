"""Author the extra TestU content for the local eme-server as CSVs the
put_import.py loader understands: a new Ciberseguridad topic + tutorial
(5 sections, 25 MCQs) and a 7th DDHH section (15 MCQs).

Ids continue after the DDHH import (sections 1-6, content 1-367, questions 1-47).
"""
import csv, os

OUT = '/tmp/ddhh2'
DDHH_TUTORIAL = 'AZ_tFsHKimsE6yOlqXpA'
CIBER_TOPIC = 'ciberseguridad'
CIBER_TUTORIAL = 'ciberseguridad-1'

sec_id, content_id, q_id = 6, 367, 47
sections, contents, questions = [], [], []


def section(name, tutorial):
    global sec_id
    sec_id += 1
    sections.append({'id': sec_id, 'name': name, 'ordering': sec_id,
                     'playbackentitymoduleid': 'entitytutorial', 'playbackentityid': tutorial, 'skills': ''})
    return sec_id


def row(sec, order, ctype, role='', content='', qid=''):
    global content_id
    content_id += 1
    contents.append({'id': content_id, 'componenttype': ctype, 'contentrole': role, 'content': content,
                     'componentsectionid': sec, 'questionid': qid, 'ordering': order, 'assetid': ''})


def block(sec, heading, explicacion, q):
    """heading → paragraph → mcq, like the DDHH import."""
    global q_id
    order = sum(1 for c in contents if c['componentsectionid'] == sec)
    row(sec, order + 1, 'heading', 'Heading', heading)
    row(sec, order + 2, 'paragraph', '', explicacion)
    q_id += 1
    text, opts, correct, level, rationale = q
    questions.append({'id': q_id, 'question': text, 'correctoption': correct, 'mcqcognitivelevel': level,
                      'option_a': opts[0], 'option_b': opts[1], 'option_c': opts[2], 'option_d': opts[3],
                      'option_e': '', 'option_f': '', 'rationale': rationale})
    row(sec, order + 3, 'mcq', '', '', q_id)


# ---------------------------------------------------------------- Ciberseguridad
s = section('1. Fundamentos de ciberseguridad en la operación minera', CIBER_TUTORIAL)
block(s, '1.1 Qué protege la ciberseguridad',
      'La ciberseguridad protege la confidencialidad, integridad y disponibilidad de la información y de los sistemas que sostienen la operación: desde el correo corporativo hasta los controles de planta.',
      ('¿Cuáles son las tres propiedades que la ciberseguridad busca proteger?',
       ['Confidencialidad, integridad y disponibilidad', 'Velocidad, ahorro y comodidad', 'Producción, ventas y logística', 'Hardware, software y redes sociales'],
       'A', 'Baja', 'La tríada CIA (confidencialidad, integridad, disponibilidad) es la base de toda política de seguridad de la información.'))
block(s, '1.2 Por qué la minería es un objetivo',
      'Las operaciones mineras dependen de sistemas de control, logística y datos geológicos de alto valor. Un ataque puede detener la producción, poner en riesgo a personas y afectar a las comunidades.',
      ('¿Cuál es el impacto más grave de un ciberataque exitoso a los sistemas de control de una planta concentradora?',
       ['La pérdida de algunos correos', 'Riesgo para la seguridad física de las personas y parada de la operación', 'Un retraso en la nómina', 'Mayor consumo de internet'],
       'B', 'Media', 'En entornos industriales, un ataque a los sistemas de control puede provocar accidentes y detener la producción, no solo perder datos.'))
block(s, '1.3 Responsabilidad compartida',
      'La seguridad no es solo tarea del área de TI. Cada colaborador es una línea de defensa: sus decisiones diarias abren o cierran puertas a los atacantes.',
      ('Un compañero dice: "de la ciberseguridad se encarga TI, yo solo opero la mina". ¿Qué respuesta es correcta?',
       ['Tiene razón, es un tema exclusivamente técnico', 'Cada colaborador es responsable de proteger la información y los sistemas que usa', 'Solo la gerencia es responsable', 'Solo aplica al personal administrativo'],
       'B', 'Baja', 'La mayoría de incidentes empieza por una acción humana; la responsabilidad es de todos.'))
block(s, '1.4 Activos de información',
      'Planos, modelos geológicos, contratos, datos de personal y credenciales son activos de información. Se clasifican según su sensibilidad y se manejan de acuerdo con ella.',
      ('¿Cuál de estos es un activo de información que debe protegerse especialmente?',
       ['El menú del comedor', 'El modelo geológico del yacimiento', 'El horario de los buses', 'El calendario de feriados'],
       'B', 'Baja', 'El modelo geológico es información estratégica cuya filtración afecta el valor de la empresa.'))
block(s, '1.5 Reportar es proteger',
      'Un incidente reportado a tiempo se contiene en minutos; uno oculto puede crecer durante semanas. Reportar nunca es motivo de sanción.',
      ('Abriste un adjunto sospechoso y ahora dudas. ¿Qué debes hacer?',
       ['Apagar el equipo y no decir nada', 'Reportarlo de inmediato al canal de incidentes de seguridad', 'Esperar a ver si pasa algo', 'Reenviarlo a un compañero para que opine'],
       'B', 'Media', 'El reporte inmediato permite contener el incidente; el silencio da tiempo al atacante.'))

s = section('2. Contraseñas, identidad y accesos', CIBER_TUTORIAL)
block(s, '2.1 Contraseñas robustas',
      'Una contraseña robusta es larga (12 o más caracteres), única por servicio y no contiene datos personales. Las frases de paso son fáciles de recordar y difíciles de adivinar.',
      ('¿Cuál de estas contraseñas es la más segura?',
       ['Minsur2024', 'diego1985', 'Cerro-Lluvia-Tambor-47!', '123456789'],
       'C', 'Baja', 'Una frase larga con palabras no relacionadas y símbolos resiste ataques de fuerza bruta y diccionario.'))
block(s, '2.2 Autenticación multifactor (MFA)',
      'La MFA añade un segundo factor (app, token o biometría) además de la contraseña. Aunque roben tu clave, no podrán entrar sin el segundo factor.',
      ('Recibes una notificación de MFA que no solicitaste. ¿Qué haces?',
       ['La apruebo, seguro es el sistema', 'La rechazo y reporto: alguien tiene mi contraseña', 'La ignoro y sigo trabajando', 'Apruebo solo si insiste varias veces'],
       'B', 'Media', 'Una solicitud de MFA no iniciada por ti indica que un tercero conoce tu contraseña; hay que rechazar y reportar.'))
block(s, '2.3 No compartir credenciales',
      'Las credenciales son personales e intransferibles. Compartirlas rompe la trazabilidad: lo que haga otro con tu usuario queda registrado a tu nombre.',
      ('Un supervisor te pide tu usuario y contraseña "para avanzar un reporte urgente". ¿Qué corresponde?',
       ['Dárselos, es mi jefe', 'Negarme con respeto y ofrecer hacer el reporte yo mismo o gestionar un acceso propio', 'Dárselos solo por WhatsApp', 'Dárselos si promete cambiarlos después'],
       'B', 'Media', 'Ninguna jerarquía justifica compartir credenciales; existen vías formales para otorgar accesos.'))
block(s, '2.4 Principio de mínimo privilegio',
      'Cada persona debe tener solo los accesos que necesita para su función. Los accesos sobrantes son puertas abiertas que nadie vigila.',
      ('Cambias de puesto y conservas accesos del rol anterior. ¿Qué debes hacer?',
       ['Conservarlos por si acaso', 'Solicitar que se retiren los accesos que ya no necesitas', 'Prestarlos a quien ocupe el puesto', 'Nada, expiran solos'],
       'B', 'Media', 'El mínimo privilegio reduce el daño si tu cuenta se ve comprometida.'))
block(s, '2.5 Gestores de contraseñas',
      'Un gestor de contraseñas corporativo genera y guarda claves únicas y complejas. Es más seguro que reutilizar una clave o anotarla en un papel.',
      ('¿Cuál es la práctica recomendada para manejar decenas de contraseñas distintas?',
       ['Usar la misma en todos los servicios', 'Anotarlas en un cuaderno en el escritorio', 'Usar el gestor de contraseñas aprobado por la empresa', 'Guardarlas en un correo a mí mismo'],
       'C', 'Baja', 'El gestor cifra las claves y permite una contraseña distinta por servicio sin memorizarlas.'))

s = section('3. Phishing e ingeniería social', CIBER_TUTORIAL)
block(s, '3.1 Señales de un correo de phishing',
      'Urgencia artificial, remitentes parecidos pero no iguales, enlaces que no coinciden con el texto y adjuntos inesperados son las señales clásicas.',
      ('Un correo de "soporte-minsur@gmai1.com" pide cambiar tu contraseña en 10 minutos. ¿Qué señales de phishing tiene?',
       ['Ninguna, es un aviso normal', 'Dominio falso y urgencia artificial', 'Solo que está en español', 'Que llegó en horario laboral'],
       'B', 'Baja', 'El dominio imitado (gmai1) y la presión de tiempo son señales típicas de phishing.'))
block(s, '3.2 Verificar por otro canal',
      'Ante una solicitud inusual (transferencias, datos, accesos), verifica llamando al número conocido de la persona, nunca respondiendo al mismo mensaje.',
      ('Recibes un correo del "gerente de finanzas" pidiendo una transferencia urgente a un proveedor nuevo. ¿Qué haces primero?',
       ['La ejecuto, es urgente', 'Respondo al correo pidiendo confirmación', 'Llamo al gerente a su número conocido para verificar', 'Se la paso a un compañero'],
       'C', 'Media', 'El fraude del CEO se detiene verificando por un canal distinto al del mensaje sospechoso.'))
block(s, '3.3 Smishing y vishing',
      'El phishing también llega por SMS (smishing) y llamadas (vishing). Nadie legítimo te pedirá códigos de verificación por teléfono.',
      ('Te llaman diciendo ser de TI y piden el código que acabas de recibir por SMS. ¿Qué haces?',
       ['Se lo dicto, es de TI', 'No lo comparto: los códigos son personales, y reporto la llamada', 'Se lo doy si conocen mi nombre', 'Cuelgo y no hago nada más'],
       'B', 'Media', 'Un código de verificación nunca se comparte; la llamada debe reportarse como intento de fraude.'))
block(s, '3.4 Enlaces y adjuntos',
      'Pasa el cursor sobre el enlace para ver el destino real. Los adjuntos con macros o extensiones dobles (factura.pdf.exe) son peligrosos.',
      ('¿Cuál de estos adjuntos es el más sospechoso?',
       ['informe_mensual.xlsx enviado por tu jefa', 'factura.pdf.exe de un remitente desconocido', 'plano.dwg del área de ingeniería', 'acta_reunion.docx del comité'],
       'B', 'Baja', 'La doble extensión oculta un ejecutable; es una técnica clásica para instalar malware.'))
block(s, '3.5 Redes sociales e información pública',
      'Los atacantes estudian perfiles públicos para personalizar sus engaños. Publicar cargos, proyectos o fotos de instalaciones les facilita el trabajo.',
      ('¿Qué publicación en redes sociales aumenta el riesgo de ingeniería social contra la empresa?',
       ['Una foto familiar en la playa', 'Una foto del tablero de control de la planta con etiquetas de equipos', 'Un saludo de cumpleaños', 'Una receta de cocina'],
       'B', 'Media', 'Las imágenes de sistemas internos revelan tecnología y proveedores que un atacante puede explotar.'))

s = section('4. Dispositivos, información y trabajo remoto', CIBER_TUTORIAL)
block(s, '4.1 Bloqueo y actualizaciones',
      'Bloquea el equipo al alejarte (Win+L) y mantén el sistema actualizado. Las actualizaciones cierran vulnerabilidades que los atacantes ya conocen.',
      ('¿Por qué es importante instalar las actualizaciones del sistema cuando TI las libera?',
       ['Para cambiar el diseño de las ventanas', 'Porque corrigen vulnerabilidades que ya están siendo explotadas', 'Para que el equipo sea más lento', 'No es importante'],
       'B', 'Baja', 'La mayoría de ataques aprovecha fallas ya corregidas en equipos sin actualizar.'))
block(s, '4.2 USB y medios extraíbles',
      'Un USB desconocido puede contener malware que se ejecuta al conectarlo. En entornos industriales, los USB son una vía habitual de infección.',
      ('Encuentras un USB en el estacionamiento de la unidad minera. ¿Qué haces?',
       ['Lo conecto a mi laptop para ver de quién es', 'Lo conecto a un equipo de planta', 'Lo entrego a seguridad o TI sin conectarlo', 'Me lo llevo a casa'],
       'C', 'Baja', 'Los USB "perdidos" son una técnica de ataque; nunca deben conectarse a equipos corporativos.'))
block(s, '4.3 Clasificación y envío de información',
      'La información confidencial se comparte solo por los canales aprobados y con las personas autorizadas. El correo personal y las apps de mensajería no son canales corporativos.',
      ('Necesitas enviar un informe confidencial a un consultor externo. ¿Cuál es la vía correcta?',
       ['Por WhatsApp, es más rápido', 'Desde mi correo personal', 'Por la plataforma corporativa de intercambio seguro, con autorización', 'Subirlo a un enlace público'],
       'C', 'Media', 'Solo los canales corporativos garantizan cifrado, trazabilidad y control de acceso.'))
block(s, '4.4 Trabajo remoto y redes públicas',
      'Fuera de la oficina, usa la VPN corporativa y evita redes wifi públicas para tareas sensibles. Un atacante en la misma red puede interceptar el tráfico.',
      ('Estás en un aeropuerto y debes revisar contratos. ¿Qué es lo correcto?',
       ['Usar el wifi abierto del aeropuerto sin más', 'Conectar la VPN corporativa antes de acceder', 'Pedir la clave del wifi a un desconocido', 'Enviar los contratos a mi correo personal para leerlos después'],
       'B', 'Media', 'La VPN cifra el tráfico y protege la información en redes que no controlamos.'))
block(s, '4.5 Dispositivos personales (BYOD)',
      'Si usas tu teléfono para el correo corporativo, debe cumplir la política: bloqueo, cifrado y posibilidad de borrado remoto en caso de pérdida.',
      ('Pierdes el celular donde tenías el correo corporativo. ¿Qué haces primero?',
       ['Comprar otro y no avisar', 'Reportarlo de inmediato a TI para bloquear el acceso y borrar los datos', 'Esperar unos días por si aparece', 'Publicar en redes que se perdió'],
       'B', 'Baja', 'El reporte inmediato permite revocar sesiones y borrar el dispositivo antes de que se use la información.'))

s = section('5. Tecnología operacional (OT) y respuesta a incidentes', CIBER_TUTORIAL)
block(s, '5.1 TI y OT no son lo mismo',
      'Los sistemas OT (PLC, SCADA, sensores) controlan procesos físicos. Un cambio no autorizado puede dañar equipos o poner en riesgo vidas; por eso se aíslan de la red corporativa.',
      ('¿Por qué los sistemas de control de planta se mantienen separados de la red de oficinas?',
       ['Por costumbre', 'Para que un incidente en la red corporativa no llegue a los equipos que controlan procesos físicos', 'Porque usan otro idioma', 'Para ahorrar cables'],
       'B', 'Media', 'La segmentación evita que malware de oficina alcance controladores que mueven equipos reales.'))
block(s, '5.2 Acceso de contratistas a sistemas de planta',
      'Los proveedores acceden a los sistemas OT solo con autorización, por conexiones supervisadas y durante el tiempo acordado.',
      ('Un técnico de un proveedor pide conectar su laptop directamente al PLC de la chancadora para "un ajuste rápido". ¿Qué corresponde?',
       ['Dejarlo, es especialista', 'Exigir autorización, uso del acceso supervisado y registro de la intervención', 'Prestarle mi usuario', 'Dejarlo si es fuera del turno'],
       'B', 'Alta', 'Los accesos a OT deben ser autorizados, supervisados y trazables; un ajuste no controlado puede detener la planta.'))
block(s, '5.3 Señales de un incidente',
      'Equipos lentos, ventanas emergentes, archivos con extensiones extrañas, sensores con lecturas imposibles o cuentas bloqueadas sin razón pueden indicar un ataque.',
      ('Varios archivos de tu carpeta compartida cambiaron a la extensión .locked y aparece una nota pidiendo dinero. ¿Qué es y qué haces?',
       ['Un error del disco; reinicio', 'Ransomware; desconecto el equipo de la red y reporto de inmediato', 'Un virus menor; borro la nota', 'Pago para recuperar los archivos'],
       'B', 'Media', 'Ante ransomware, aislar el equipo y reportar evita que cifre la red; nunca se paga por cuenta propia.'))
block(s, '5.4 Qué NO hacer durante un incidente',
      'No apagues el equipo (se pierden evidencias), no intentes "limpiarlo" por tu cuenta y no comentes el incidente por canales no autorizados.',
      ('Durante un incidente de seguridad, ¿cuál de estas acciones es incorrecta?',
       ['Desconectar el equipo de la red', 'Avisar al canal de incidentes', 'Apagar el equipo y formatearlo para "resolverlo"', 'Anotar la hora y lo que observaste'],
       'C', 'Media', 'Formatear destruye la evidencia que el equipo de respuesta necesita para entender y contener el ataque.'))
block(s, '5.5 Continuidad y aprendizaje',
      'Después de un incidente se analizan causas y se ajustan controles. Las lecciones aprendidas se comparten para que no se repita.',
      ('¿Cuál es el objetivo del análisis posterior a un incidente?',
       ['Encontrar un culpable para sancionarlo', 'Entender la causa, corregir controles y compartir lo aprendido', 'Cerrar el caso lo antes posible', 'Ocultarlo a la gerencia'],
       'B', 'Baja', 'La cultura justa busca aprender y mejorar, no castigar a quien reportó.'))

# ---------------------------------------------------------------- DDHH, sección 7
s = section('7. Casos adicionales: comunidades, contratistas y seguridad', DDHH_TUTORIAL)
block(s, '7.1 Consulta y participación de comunidades',
      'Las comunidades vecinas tienen derecho a ser informadas y a participar en las decisiones que las afectan. La consulta es un proceso continuo, no un trámite.',
      ('Una comunidad cercana pide información sobre un nuevo depósito de relaves. ¿Cuál es la actuación alineada con los DDHH?',
       ['Negar la información por ser técnica', 'Entregar información clara y oportuna y abrir espacios de diálogo', 'Esperar a que el proyecto esté construido', 'Responder solo si hay una protesta'],
       'B', 'Media', 'El acceso a la información y la participación son parte del respeto a los derechos de las comunidades.'))
block(s, '7.2 Uso del agua',
      'El derecho humano al agua obliga a gestionar el recurso sin afectar el acceso de las comunidades ni la calidad de sus fuentes.',
      ('El monitoreo muestra un cambio en la calidad del agua aguas abajo de la operación. ¿Qué corresponde?',
       ['Esperar al siguiente monitoreo', 'Investigar de inmediato, informar a las autoridades y comunidades, y actuar sobre la causa', 'Ajustar los reportes', 'Culpar a otras actividades de la zona'],
       'B', 'Alta', 'La debida diligencia exige actuar con rapidez y transparencia ante un posible impacto en el agua.'))
block(s, '7.3 Contratistas y condiciones laborales',
      'La empresa es responsable de que sus contratistas respeten los derechos laborales: jornada, salario, seguridad y libertad sindical.',
      ('Detectas que una contratista hace trabajar a su personal 14 horas diarias sin descanso. ¿Qué haces?',
       ['Nada, no son empleados de Minsur', 'Reportarlo por el canal correspondiente para que se corrija', 'Felicitar la productividad', 'Pedir que lo hagan fuera de la vista'],
       'B', 'Media', 'Los impactos en la cadena de valor son responsabilidad de la empresa según los Principios Rectores.'))
block(s, '7.4 Trabajo infantil y forzoso',
      'La prohibición del trabajo infantil y del trabajo forzoso es absoluta, también en proveedores y contratistas.',
      ('Un proveedor de alimentos entrega productos elaborados con trabajo de menores. ¿Cuál es la respuesta correcta?',
       ['Seguir comprando por el precio', 'Suspender la relación hasta que se corrija y exigir un plan de remediación', 'Ignorarlo porque es un tema del proveedor', 'Pedir un descuento'],
       'B', 'Media', 'La empresa no puede contribuir a violaciones graves de DDHH a través de sus proveedores.'))
block(s, '7.5 Seguridad privada y uso de la fuerza',
      'El personal de seguridad debe actuar conforme a los Principios Voluntarios: uso de la fuerza proporcional y solo cuando sea estrictamente necesario.',
      ('Durante una protesta pacífica en la vía de acceso, el personal de seguridad propone dispersar a la fuerza. ¿Qué corresponde?',
       ['Autorizar el uso de la fuerza', 'Priorizar el diálogo, respetar la protesta pacífica y escalar a las autoridades competentes', 'Contratar más guardias', 'Grabar a los manifestantes para denunciarlos'],
       'B', 'Alta', 'La protesta pacífica es un derecho; la fuerza solo cabe ante un riesgo real y de forma proporcional.'))
block(s, '7.6 Discriminación y acoso',
      'Toda persona tiene derecho a un ambiente laboral libre de discriminación y acoso, sin importar género, origen, religión u orientación.',
      ('Un colaborador hace bromas reiteradas sobre el origen étnico de una compañera. ¿Qué es esto y qué haces?',
       ['Humor inofensivo; nada', 'Discriminación; intervengo con respeto y lo reporto por el canal de integridad', 'Un asunto privado entre ellos', 'La animo a cambiar de área'],
       'B', 'Media', 'Las bromas reiteradas sobre el origen étnico son discriminación y deben reportarse.'))
block(s, '7.7 Pueblos indígenas',
      'Los pueblos indígenas tienen derechos colectivos sobre sus tierras, cultura y decisiones. El consentimiento libre, previo e informado orienta la relación.',
      ('¿Qué significa consentimiento libre, previo e informado?',
       ['Firmar un acta el día de la obra', 'Un acuerdo tomado sin presión, antes de decidir y con información completa', 'Un permiso de la autoridad municipal', 'Un aviso por radio'],
       'B', 'Baja', 'El CLPI exige ausencia de coerción, anticipación y comprensión plena de los impactos.'))
block(s, '7.8 Reasentamiento',
      'Cuando una operación requiere reasentar familias, debe restituir o mejorar sus condiciones de vida, con participación y compensación justa.',
      ('Una familia reasentada recibe una vivienda pero pierde el acceso a sus tierras de cultivo. ¿Qué principio se incumple?',
       ['Ninguno, ya tiene casa', 'El de restituir o mejorar los medios de vida', 'El de rapidez del proyecto', 'El de confidencialidad'],
       'B', 'Media', 'El reasentamiento debe mantener o mejorar los medios de subsistencia, no solo la vivienda.'))
block(s, '7.9 Defensores de derechos humanos',
      'Las personas que defienden derechos humanos y el ambiente no deben ser intimidadas ni estigmatizadas por la empresa ni por terceros vinculados.',
      ('Un líder comunitario critica públicamente la operación. ¿Cuál es la actuación correcta?',
       ['Investigarlo para desacreditarlo', 'Escuchar sus preocupaciones y responder por los canales de diálogo, sin represalias', 'Restringirle el acceso a la zona', 'Pedir a la policía que lo vigile'],
       'B', 'Alta', 'La política de DDHH protege a los defensores; las represalias son una violación grave.'))
block(s, '7.10 Privacidad de datos del personal',
      'Los datos personales de colaboradores (salud, biometría, ubicación) se recogen solo con fines legítimos y se protegen contra usos indebidos.',
      ('El área de seguridad quiere publicar en el comedor la lista de colaboradores con enfermedades ocupacionales. ¿Es correcto?',
       ['Sí, es transparencia', 'No: los datos de salud son sensibles y su difusión viola la privacidad', 'Sí, si es con nombres abreviados', 'Sí, si lo aprueba el sindicato'],
       'B', 'Media', 'Los datos de salud tienen protección especial; difundirlos vulnera la privacidad y la dignidad.'))
block(s, '7.11 Mecanismos de reclamación accesibles',
      'Un mecanismo de reclamación eficaz es conocido, accesible, predecible y equitativo; también para quien no sabe leer o no habla castellano.',
      ('Una comunidad quechuahablante no usa el buzón de reclamos porque los formularios están solo en castellano. ¿Qué falla?',
       ['Nada, deben aprender', 'La accesibilidad del mecanismo', 'La confidencialidad', 'La rapidez'],
       'B', 'Media', 'Los Principios Rectores exigen mecanismos accesibles en lengua y formato adecuados.'))
block(s, '7.12 Remediación',
      'Cuando la empresa causa o contribuye a un impacto, debe repararlo: disculpa, restitución, compensación o garantías de no repetición.',
      ('Un derrame afecta el pastizal de una familia. ¿Cuál es una remediación adecuada?',
       ['Un comunicado de prensa', 'Limpieza, compensación por las pérdidas y medidas para que no se repita', 'Una visita de cortesía', 'Esperar la sentencia judicial'],
       'B', 'Media', 'La remediación debe ser proporcional al daño y prevenir su repetición.'))
block(s, '7.13 Salud y seguridad como derecho',
      'El derecho a la vida y a la integridad se concreta en condiciones seguras de trabajo. Detener una tarea insegura es un derecho y un deber.',
      ('Un operador detiene una tarea porque el equipo no tiene la guarda de seguridad. Su supervisor lo presiona para continuar. ¿Quién actúa correctamente?',
       ['El supervisor: la producción es prioridad', 'El operador: tiene derecho a negarse a un trabajo inseguro', 'Ninguno', 'Ambos'],
       'B', 'Baja', 'El derecho a negarse a un trabajo inseguro está reconocido y protegido.'))
block(s, '7.14 Igualdad de género',
      'La igualdad de oportunidades incluye acceso a puestos, salario equitativo, instalaciones adecuadas y protección frente al acoso.',
      ('En la unidad no hay vestuarios para mujeres y se les asignan solo tareas administrativas. ¿Qué derecho se afecta?',
       ['Ninguno', 'La igualdad de oportunidades y de trato', 'La libertad sindical', 'La privacidad'],
       'B', 'Baja', 'La falta de instalaciones y la limitación de tareas por género son discriminación.'))
block(s, '7.15 Rendición de cuentas',
      'La empresa informa públicamente cómo identifica y gestiona sus impactos en DDHH. La transparencia permite la confianza y la mejora.',
      ('¿Qué demuestra una empresa que publica anualmente sus impactos y medidas en DDHH?',
       ['Que tiene muchos problemas', 'Rendición de cuentas y compromiso con la mejora continua', 'Que quiere evitar auditorías', 'Que busca publicidad'],
       'B', 'Baja', 'Reportar es parte del "conocer y mostrar" de los Principios Rectores.'))

# ---------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
def write(name, rows, fields):
    with open(f'{OUT}/{name}.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

write('entitytopic', [{'id': CIBER_TOPIC, 'name': 'Ciberseguridad',
                       'longcaption': 'Buenas prácticas de ciberseguridad para colaboradores y operación minera (Minsur · TestU)', 'primarymedia': ''}],
      ['id', 'name', 'longcaption', 'primarymedia'])
write('entitytutorial', [{'id': CIBER_TUTORIAL, 'name': 'Ciberseguridad', 'entitytopic': CIBER_TOPIC, 'primarymedia': ''}],
      ['id', 'name', 'entitytopic', 'primarymedia'])
write('componentsection', sections, ['id', 'name', 'ordering', 'playbackentitymoduleid', 'playbackentityid', 'skills'])
write('componentcontent', contents, ['id', 'componenttype', 'contentrole', 'content', 'componentsectionid', 'questionid', 'ordering', 'assetid'])
write('entityquestion', questions, ['id', 'question', 'correctoption', 'mcqcognitivelevel', 'option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f', 'rationale'])
print(f'sections {len(sections)} contents {len(contents)} questions {len(questions)}')
