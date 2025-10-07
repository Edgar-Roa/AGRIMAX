CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Cliente', 'Proveedor','admin')),
    tipo_productos VARCHAR(100),
    fecha_nacimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE usuarios ADD COLUMN edad VARCHAR(15);
alter table usuarios drop column empresa;
select * from usuarios;
delete from usuarios where id=5;
ALTER TABLE usuarios ADD COLUMN apellido VARCHAR(255);
ALTER TABLE perfiles ADD COLUMN notificaciones_email BOOLEAN DEFAULT FALSE;
ALTER TABLE perfiles ADD COLUMN notificaciones_sms BOOLEAN DEFAULT FALSE;



CREATE TABLE perfiles (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    foto VARCHAR(255),
    biografia TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
select * from perfiles;
ALTER TABLE perfiles ADD COLUMN cursor_size VARCHAR(20) DEFAULT 'default';
ALTER TABLE perfiles ADD COLUMN modo_lector VARCHAR(10) DEFAULT 'off';
SELECT foto FROM perfiles WHERE usuario_id = ID_DEL_USUARIO;


CREATE TABLE direcciones (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Envío', 'Facturación')),
    direccion TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);


CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);
select * from categorias;
INSERT INTO categorias (nombre) VALUES
('Frutas'),
('Verduras'),
('Granos');
UPDATE categorias
SET nombre = 'legumbres'
WHERE id = 3;


CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL,
    categoria_id INT REFERENCES categorias(id) ON DELETE SET NULL,
    proveedor_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select*from productos;


CREATE TABLE imagenes_productos (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
    ruta_imagen VARCHAR(255) NOT NULL
);
select * from imagenes_productos;
SELECT producto_id, ruta_imagen FROM imagenes_productos WHERE producto_id IN (SELECT producto_id FROM notificaciones);

CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'Pendiente'
);

CREATE TABLE detalles_pedidos (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL
);
select*from detalles_pedidos

ALTER TABLE detalles_pedidos ADD COLUMN estado VARCHAR(50) DEFAULT 'Pendiente';
INSERT INTO detalles_pedidos (estado) VALUES
('Proceso'),
('Entregado');

CREATE TABLE metodos_pago (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    detalles TEXT
);


CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id) ON DELETE CASCADE,
    metodo_pago_id INT REFERENCES metodos_pago(id) ON DELETE SET NULL,
    monto NUMERIC(10, 2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) DEFAULT 'Pendiente'
);

CREATE TABLE mensajes (
    id SERIAL PRIMARY KEY,
    remitente_id INT NOT NULL,
    destinatario_id INT NOT NULL,
    contenido TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (remitente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (destinatario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE estadisticas_ventas (
    id SERIAL PRIMARY KEY,
    proveedor_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    productos_vendidos INT DEFAULT 0,
    total_ingresos NUMERIC(10, 2) DEFAULT 0.00,
    pedidos_recibidos INT DEFAULT 0,
    ventas_esperadas INT DEFAULT 0
);

CREATE TABLE notificaciones (
    id SERIAL PRIMARY KEY,
    proveedor_id INT NOT NULL,
    cliente_id INT NOT NULL,
    producto_id INT NOT NULL,
    mensaje TEXT NOT NULL,
    leido BOOLEAN DEFAULT FALSE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES usuarios (id),
    FOREIGN KEY (cliente_id) REFERENCES usuarios (id),
    FOREIGN KEY (producto_id) REFERENCES productos (id)
);
ALTER TABLE notificaciones ADD COLUMN estado VARCHAR(50) DEFAULT 'Pendiente';