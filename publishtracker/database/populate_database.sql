-- DDL para poblar base de datos PublishTracker con datos de prueba
-- Habilitar foreign keys
PRAGMA foreign_keys = ON;

-- Limpiar datos existentes (orden inverso por FK)
DELETE FROM authors_paperautor;
DELETE FROM authors_rolautor;  
DELETE FROM publications_paper;
DELETE FROM journals_archivorevista;
DELETE FROM journals_edicionrevista;
DELETE FROM authors_autor;
DELETE FROM authors_rol;
DELETE FROM journals_revista;
DELETE FROM journals_editorial;
DELETE FROM journals_ambitorevista;
DELETE FROM journals_categoriarevista;
DELETE FROM journals_tipoarchivorevista;
DELETE FROM catalogs_areaconocimiento;
DELETE FROM catalogs_formatoarchivo;
DELETE FROM catalogs_fuentefinanciamiento;
DELETE FROM catalogs_institucion;
DELETE FROM catalogs_tipocita;
DELETE FROM catalogs_tipoparticipacion;
DELETE FROM core_ejesecithi;
DELETE FROM core_estatuspublicacion;
DELETE FROM core_pais;
DELETE FROM core_programaseciti;

-- TABLAS BASE SIN FK DEPENDENCIES

-- core_pais (requerido por instituciones y revistas)
INSERT INTO core_pais (nombre, codigo_iso) VALUES
('México', 'MEX'),
('Estados Unidos', 'USA');

-- core_estatuspublicacion (requerido por papers)
INSERT INTO core_estatuspublicacion (estatus, descripcion) VALUES
('Publicado', 'Artículo publicado y disponible'),
('En revisión', 'Artículo sometido en proceso de revisión');

-- core_ejesecithi (opcional para papers)
INSERT INTO core_ejesecithi (nombre, descripcion) VALUES
('Tecnología e Innovación', 'Investigación en tecnologías emergentes'),
('Desarrollo Social', 'Investigación orientada al bienestar social');

-- core_programaseciti (opcional para papers)  
INSERT INTO core_programaseciti (nombre, descripcion) VALUES
('Programa Nacional de Posgrados de Calidad', 'PNPC - Formación de recursos humanos especializados'),
('Sistema Nacional de Investigadores', 'SNI - Reconocimiento a la labor investigativa');

-- CATALOGOS

-- catalogs_areaconocimiento 
INSERT INTO catalogs_areaconocimiento (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, codigo_externo, area_padre_id) VALUES
('Ingeniería y Tecnología', 'ING_TEC', 1, 1, 'Área de conocimiento tecnológico', datetime('now'), datetime('now'), 'IT001', NULL),
('Ciencias Sociales', 'SOC', 1, 2, 'Área de ciencias sociales y humanidades', datetime('now'), datetime('now'), 'CS001', NULL);

-- catalogs_formatoarchivo
INSERT INTO catalogs_formatoarchivo (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, extension, mime_type, tamaño_maximo_mb) VALUES
('PDF', 'PDF', 1, 1, 'Formato de documento portátil', datetime('now'), datetime('now'), 'pdf', 'application/pdf', 50),
('Word', 'DOCX', 1, 2, 'Documento de Microsoft Word', datetime('now'), datetime('now'), 'docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 25);

-- catalogs_fuentefinanciamiento
INSERT INTO catalogs_fuentefinanciamiento (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, tipo_fuente, monto_maximo, vigente) VALUES
('CONACYT', 'CONACYT', 1, 1, 'Consejo Nacional de Ciencia y Tecnología', datetime('now'), datetime('now'), 'PUBLICO', 500000.00, 1),
('Fondos Institucionales', 'INST', 1, 2, 'Financiamiento institucional interno', datetime('now'), datetime('now'), 'INSTITUCIONAL', 100000.00, 1);

-- catalogs_institucion
INSERT INTO catalogs_institucion (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, tipo_institucion, sitio_web, pais_id) VALUES
('Universidad Tecnológica de la Mixteca', 'UTM', 1, 1, 'Universidad pública tecnológica', datetime('now'), datetime('now'), 'PUBLICA', 'https://www.utm.mx', 1),
('Massachusetts Institute of Technology', 'MIT', 1, 2, 'Instituto tecnológico privado', datetime('now'), datetime('now'), 'PRIVADA', 'https://www.mit.edu', 2);

-- catalogs_tipocita
INSERT INTO catalogs_tipocita (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, color_interfaz, peso_metrico) VALUES
('Cita Directa', 'DIRECTA', 1, 1, 'Cita textual del trabajo', datetime('now'), datetime('now'), '#28a745', 1.0),
('Cita de Referencia', 'REFERENCIA', 1, 2, 'Referencia al trabajo en bibliografía', datetime('now'), datetime('now'), '#007bff', 0.8);

-- catalogs_tipoparticipacion  
INSERT INTO catalogs_tipoparticipacion (nombre, clave, activo, orden, descripcion, fecha_creacion, fecha_modificacion, requiere_justificacion) VALUES
('Autor Principal', 'PRINCIPAL', 1, 1, 'Liderazgo de la investigación', datetime('now'), datetime('now'), 0),
('Coautor', 'COAUTOR', 1, 2, 'Participación como coautor', datetime('now'), datetime('now'), 1);

-- REVISTAS Y EDITORIALES

-- journals_ambitorevista
INSERT INTO journals_ambitorevista (nombre, descripcion) VALUES
('Internacional', 'Revista con alcance internacional'),
('Nacional', 'Revista con alcance nacional');

-- journals_categoriarevista  
INSERT INTO journals_categoriarevista (nombre, descripcion) VALUES
('Q1', 'Primer cuartil - Alto impacto'),
('Q2', 'Segundo cuartil - Impacto medio-alto');

-- journals_editorial
INSERT INTO journals_editorial (nombre, direccion, pais_id) VALUES
('Springer Nature', '1 New York Plaza, Suite 4600, New York, NY 10004, USA', 2),
('Editorial UTM', 'Carretera a Acatlima Km. 2.5, Huajuapan de León, Oaxaca', 1);

-- journals_revista
INSERT INTO journals_revista (nombre, issn_impreso, issn_electronico, factor_impacto, url, dirigido_cuerpo_academico, ambito_id, categoria_id, editorial_id, pais_publicacion_id) VALUES
('Journal of Computer Science and Technology', '1000-9000', '1860-4749', 2.456, 'https://link.springer.com/journal/11390', 1, 1, 1, 1, 2),
('Revista Tecnológica UTM', '2007-1620', '2683-2895', 0.125, 'https://revista.utm.mx', 0, 2, 2, 2, 1);

-- journals_tipoarchivorevista
INSERT INTO journals_tipoarchivorevista (tipo, descripcion) VALUES
('Artículo Completo', 'Archivo PDF del artículo completo'),
('Material Suplementario', 'Archivos adicionales del artículo');

-- journals_edicionrevista (FK a revista)
INSERT INTO journals_edicionrevista (anio, volumen, numero, indice_revista, revista_id) VALUES
(2024, '35', '2', 'Vol.35 No.2 (2024)', 1),
(2023, '18', '1', 'Vol.18 No.1 (2023)', 2);

-- AUTORES Y ROLES

-- authors_autor
INSERT INTO authors_autor (nombre, orcid) VALUES
('Juan Pérez García', '0000-0002-1825-0097'),
('María Elena Rodríguez', '0000-0003-4567-8901');

-- authors_rol  
INSERT INTO authors_rol (nombre_rol, descripcion) VALUES
('Investigador Principal', 'Responsable principal de la investigación'),
('Investigador Colaborador', 'Colabora en aspectos específicos de la investigación');

-- authors_rolautor (FK a autor y rol)
INSERT INTO authors_rolautor (fecha_asignacion, autor_id, rol_id) VALUES
(datetime('now', '-30 days'), 1, 1),
(datetime('now', '-15 days'), 2, 2);

-- PAPERS (FK múltiples)
INSERT INTO publications_paper (
    doi, titulo, anio_publicacion, recibio_apoyo_seciti, rol_participacion,
    objetivo, descripcion, abstract, url_cita, total_citas,
    pagina_inicio, pagina_fin, referencia_apa, fecha_creacion, fecha_actualizacion,
    edicion_id, eje_secithi_id, estatus_publicacion_id, programa_id
) VALUES
(
    '10.1007/s11390-024-3847-x',
    'Machine Learning Approaches for Natural Language Processing in Educational Systems',
    2024, 1, 'Autor Principal',
    'Desarrollar modelos de ML para procesamiento de lenguaje natural en sistemas educativos',
    'Investigación sobre aplicación de técnicas de machine learning en el procesamiento automático de texto educativo',
    'This paper presents novel machine learning approaches for natural language processing specifically designed for educational systems...',
    'https://scholar.google.com/citations?view_op=view_citation&hl=es&user=example&citation_for_view=example:abc123',
    15, 125, 142,
    'Pérez García, J. (2024). Machine Learning Approaches for Natural Language Processing in Educational Systems. Journal of Computer Science and Technology, 35(2), 125-142.',
    datetime('now', '-60 days'), datetime('now', '-5 days'),
    1, 1, 1, 1
),
(
    '10.33881/revista-utm.v18i1.2023.456',
    'Análisis de Sistemas de Información Gerencial en Empresas Regionales',
    2023, 0, 'Coautora',
    'Analizar el impacto de los sistemas de información gerencial en la toma de decisiones empresariales',
    'Estudio de caso sobre implementación de sistemas de información en empresas de la región',
    'Este trabajo presenta un análisis exhaustivo de los sistemas de información gerencial implementados en empresas regionales...',
    'https://revista.utm.mx/index.php/revista/article/view/456',
    3, 78, 95,
    'Rodríguez, M. E. (2023). Análisis de Sistemas de Información Gerencial en Empresas Regionales. Revista Tecnológica UTM, 18(1), 78-95.',
    datetime('now', '-120 days'), datetime('now', '-30 days'),
    2, 2, 1, 2
);

-- authors_paperautor (FK a papel, autor y rolautor - tabla intermedia M2M)
INSERT INTO authors_paperautor (orden_autor, autor_id, paper_id, rol_autor_id) VALUES
(1, 1, 1, 1), -- Juan como primer autor del primer paper
(1, 2, 2, 2); -- María como primera autora del segundo paper

-- ARCHIVOS DE REVISTA (FK a edicion y tipo_archivo)
INSERT INTO journals_archivorevista (nombre_archivo, archivo, fecha_subida, edicion_id, tipo_archivo_id) VALUES
('jcst_vol35_no2_2024.pdf', 'archivos/revistas/2024/jcst_35_2.pdf', datetime('now', '-30 days'), 1, 1),
('revista_utm_vol18_no1_2023.pdf', 'archivos/revistas/2023/utm_18_1.pdf', datetime('now', '-90 days'), 2, 1);

-- Verificar integridad de datos
SELECT 'Verificación completada: ' || COUNT(*) || ' papers insertados' FROM publications_paper;
SELECT 'Verificación completada: ' || COUNT(*) || ' autores insertados' FROM authors_autor;
SELECT 'Verificación completada: ' || COUNT(*) || ' relaciones autor-paper insertadas' FROM authors_paperautor;

-- Consulta de prueba para verificar las relaciones
SELECT 
    p.titulo,
    p.anio_publicacion,
    a.nombre as autor,
    pa.orden_autor,
    r.nombre_rol,
    er.volumen,
    er.numero,
    rev.nombre as revista,
    ep.estatus
FROM publications_paper p
JOIN authors_paperautor pa ON p.id = pa.paper_id  
JOIN authors_autor a ON pa.autor_id = a.id
JOIN authors_rolautor ra ON pa.rol_autor_id = ra.id
JOIN authors_rol r ON ra.rol_id = r.id
JOIN journals_edicionrevista er ON p.edicion_id = er.id
JOIN journals_revista rev ON er.revista_id = rev.id  
JOIN core_estatuspublicacion ep ON p.estatus_publicacion_id = ep.id
ORDER BY p.anio_publicacion DESC, pa.orden_autor;
