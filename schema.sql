-- Estructura de la base de datos

-- Tabla de Clientes
CREATE TABLE Clientes (
    ClienteID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Email VARCHAR(100),
    Telefono VARCHAR(20),
    Direccion VARCHAR(200),
    FechaRegistro DATE
);

-- Tabla de Categorías de Productos
CREATE TABLE CategoriasProductos (
    CategoriaID INT PRIMARY KEY,
    NombreCategoria VARCHAR(50),
    Descripcion VARCHAR(200)
);

-- Tabla de Productos
CREATE TABLE Productos (
    ProductoID INT PRIMARY KEY,
    CategoriaID INT,
    NombreProducto VARCHAR(100),
    Descripcion VARCHAR(200),
    PrecioUnitario DECIMAL(10, 2),
    Stock INT,
    FOREIGN KEY (CategoriaID) REFERENCES CategoriasProductos(CategoriaID)
);

-- Tabla de Facturas
CREATE TABLE Facturas (
    FacturaID INT PRIMARY KEY,
    ClienteID INT,
    FechaEmision DATE,
    FechaVencimiento DATE,
    TotalFactura DECIMAL(10, 2),
    EstadoPago VARCHAR(20),
    FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID)
);

-- Tabla de Detalles de Factura
CREATE TABLE DetallesFactura (
    DetalleID INT PRIMARY KEY,
    FacturaID INT,
    ProductoID INT,
    Cantidad INT,
    PrecioUnitario DECIMAL(10, 2),
    Subtotal DECIMAL(10, 2),
    FOREIGN KEY (FacturaID) REFERENCES Facturas(FacturaID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

-- Tabla de Pagos
CREATE TABLE Pagos (
    PagoID INT PRIMARY KEY,
    FacturaID INT,
    FechaPago DATE,
    MontoPagado DECIMAL(10, 2),
    MetodoPago VARCHAR(50),
    FOREIGN KEY (FacturaID) REFERENCES Facturas(FacturaID)
);

-- Tabla de Métodos de Pago
CREATE TABLE MetodosPago (
    MetodoPagoID INT PRIMARY KEY,
    NombreMetodo VARCHAR(50),
    Descripcion VARCHAR(100)
);

-- Tabla de Consumos (para servicios recurrentes)
CREATE TABLE Consumos (
    ConsumoID INT PRIMARY KEY,
    ClienteID INT,
    ProductoID INT,
    FechaConsumo DATE,
    CantidadConsumida DECIMAL(10, 2),
    FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

-- Tabla de Proveedores
CREATE TABLE Proveedores (
    ProveedorID INT PRIMARY KEY,
    NombreProveedor VARCHAR(100),
    ContactoNombre VARCHAR(100),
    ContactoEmail VARCHAR(100),
    ContactoTelefono VARCHAR(20)
);

-- Tabla de Compras a Proveedores
CREATE TABLE ComprasProveedores (
    CompraID INT PRIMARY KEY,
    ProveedorID INT,
    FechaCompra DATE,
    TotalCompra DECIMAL(10, 2),
    FOREIGN KEY (ProveedorID) REFERENCES Proveedores(ProveedorID)
);

-- Tabla de Detalles de Compra a Proveedores
CREATE TABLE DetallesCompraProveedores (
    DetalleCompraID INT PRIMARY KEY,
    CompraID INT,
    ProductoID INT,
    Cantidad INT,
    PrecioUnitario DECIMAL(10, 2),
    Subtotal DECIMAL(10, 2),
    FOREIGN KEY (CompraID) REFERENCES ComprasProveedores(CompraID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

-- Tabla de Devoluciones
CREATE TABLE Devoluciones (
    DevolucionID INT PRIMARY KEY,
    FacturaID INT,
    FechaDevolucion DATE,
    MotivoDevolucion VARCHAR(200),
    FOREIGN KEY (FacturaID) REFERENCES Facturas(FacturaID)
);

-- Tabla de Detalles de Devolución
CREATE TABLE DetallesDevolucion (
    DetalleDevolucionID INT PRIMARY KEY,
    DevolucionID INT,
    ProductoID INT,
    Cantidad INT,
    PrecioUnitario DECIMAL(10, 2),
    Subtotal DECIMAL(10, 2),
    FOREIGN KEY (DevolucionID) REFERENCES Devoluciones(DevolucionID),
    FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
);

-- Tabla de Descuentos
CREATE TABLE Descuentos (
    DescuentoID INT PRIMARY KEY,
    NombreDescuento VARCHAR(100),
    TipoDescuento VARCHAR(50),
    ValorDescuento DECIMAL(10, 2),
    FechaInicio DATE,
    FechaFin DATE
);

-- Tabla de Impuestos
CREATE TABLE Impuestos (
    ImpuestoID INT PRIMARY KEY,
    NombreImpuesto VARCHAR(50),
    Porcentaje DECIMAL(5, 2)
);

-- Tabla de Empleados
CREATE TABLE Empleados (
    EmpleadoID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Cargo VARCHAR(50),
    FechaContratacion DATE,
    Salario DECIMAL(10, 2)
);

-- Inserción de datos de ejemplo (10 registros por tabla)

-- Insertar datos en Clientes
INSERT INTO Clientes VALUES
(1, 'Juan', 'Pérez', 'juan@email.com', '123-456-7890', 'Calle 123, Ciudad', '2023-01-15'),
(2, 'María', 'González', 'maria@email.com', '234-567-8901', 'Avenida 456, Ciudad', '2023-02-20'),
(3, 'Carlos', 'Rodríguez', 'carlos@email.com', '345-678-9012', 'Plaza 789, Ciudad', '2023-03-25'),
(4, 'Ana', 'Martínez', 'ana@email.com', '456-789-0123', 'Calle 101, Ciudad', '2023-04-30'),
(5, 'Luis', 'Sánchez', 'luis@email.com', '567-890-1234', 'Avenida 202, Ciudad', '2023-05-05'),
(6, 'Laura', 'Fernández', 'laura@email.com', '678-901-2345', 'Plaza 303, Ciudad', '2023-06-10'),
(7, 'Pedro', 'López', 'pedro@email.com', '789-012-3456', 'Calle 404, Ciudad', '2023-07-15'),
(8, 'Sofia', 'Díaz', 'sofia@email.com', '890-123-4567', 'Avenida 505, Ciudad', '2023-08-20'),
(9, 'Miguel', 'Torres', 'miguel@email.com', '901-234-5678', 'Plaza 606, Ciudad', '2023-09-25'),
(10, 'Elena', 'Ruiz', 'elena@email.com', '012-345-6789', 'Calle 707, Ciudad', '2023-10-30');

-- Insertar datos en CategoriasProductos
INSERT INTO CategoriasProductos VALUES
(1, 'Electrónicos', 'Productos electrónicos y gadgets'),
(2, 'Ropa', 'Prendas de vestir y accesorios'),
(3, 'Hogar', 'Artículos para el hogar'),
(4, 'Alimentos', 'Productos alimenticios'),
(5, 'Deportes', 'Equipamiento deportivo'),
(6, 'Libros', 'Libros y material de lectura'),
(7, 'Juguetes', 'Juguetes y juegos'),
(8, 'Belleza', 'Productos de belleza y cuidado personal'),
(9, 'Jardín', 'Artículos de jardinería'),
(10, 'Automotriz', 'Accesorios y repuestos para automóviles');

-- Insertar datos en Productos
INSERT INTO Productos VALUES
(1, 1, 'Smartphone', 'Teléfono inteligente de última generación', 599.99, 100),
(2, 2, 'Camiseta', 'Camiseta de algodón', 19.99, 200),
(3, 3, 'Lámpara', 'Lámpara de mesa decorativa', 39.99, 50),
(4, 4, 'Café', 'Café gourmet', 9.99, 150),
(5, 5, 'Balón de fútbol', 'Balón de fútbol profesional', 29.99, 75),
(6, 6, 'Novela bestseller', 'Novela de ficción más vendida', 14.99, 100),
(7, 7, 'Muñeca', 'Muñeca de colección', 24.99, 60),
(8, 8, 'Crema facial', 'Crema hidratante para el rostro', 34.99, 80),
(9, 9, 'Maceta', 'Maceta decorativa para plantas', 12.99, 120),
(10, 10, 'Aceite de motor', 'Aceite sintético para motor', 44.99, 90);

-- Insertar datos en Facturas
INSERT INTO Facturas VALUES
(1, 1, '2023-11-01', '2023-12-01', 699.99, 'Pagado'),
(2, 2, '2023-11-05', '2023-12-05', 59.97, 'Pendiente'),
(3, 3, '2023-11-10', '2023-12-10', 119.97, 'Pagado'),
(4, 4, '2023-11-15', '2023-12-15', 39.96, 'Pagado'),
(5, 5, '2023-11-20', '2023-12-20', 89.97, 'Pendiente'),
(6, 6, '2023-11-25', '2023-12-25', 74.95, 'Pagado'),
(7, 7, '2023-11-30', '2023-12-30', 49.98, 'Pendiente'),
(8, 8, '2023-12-05', '2024-01-05', 139.96, 'Pagado'),
(9, 9, '2023-12-10', '2024-01-10', 51.96, 'Pendiente'),
(10, 10, '2023-12-15', '2024-01-15', 224.95, 'Pagado');

-- Insertar datos en DetallesFactura
INSERT INTO DetallesFactura VALUES
(1, 1, 1, 1, 599.99, 599.99),
(2, 2, 2, 3, 19.99, 59.97),
(3, 3, 3, 3, 39.99, 119.97),
(4, 4, 4, 4, 9.99, 39.96),
(5, 5, 5, 3, 29.99, 89.97),
(6, 6, 6, 5, 14.99, 74.95),
(7, 7, 7, 2, 24.99, 49.98),
(8, 8, 8, 4, 34.99, 139.96),
(9, 9, 9, 4, 12.99, 51.96),
(10, 10, 10, 5, 44.99, 224.95);

-- Insertar datos en Pagos
INSERT INTO Pagos VALUES
(1, 1, '2023-11-15', 699.99, 'Tarjeta de crédito'),
(2, 3, '2023-11-25', 119.97, 'Transferencia bancaria'),
(3, 4, '2023-11-30', 39.96, 'PayPal'),
(4, 6, '2023-12-10', 74.95, 'Efectivo'),
(5, 8, '2023-12-20', 139.96, 'Tarjeta de débito'),
(6, 10, '2023-12-30', 224.95, 'Cheque'),
(7, 1, '2024-01-05', 50.00, 'Tarjeta de crédito'),
(8, 3, '2024-01-10', 25.00, 'Transferencia bancaria'),
(9, 4, '2024-01-15', 15.00, 'PayPal'),
(10, 6, '2024-01-20', 30.00, 'Efectivo');

-- Insertar datos en MetodosPago
INSERT INTO MetodosPago VALUES
(1, 'Tarjeta de crédito', 'Pago con tarjeta de crédito'),
(2, 'Tarjeta de débito', 'Pago con tarjeta de débito'),
(3, 'Transferencia bancaria', 'Pago por transferencia bancaria'),
(4, 'PayPal', 'Pago a través de PayPal'),
(5, 'Efectivo', 'Pago en efectivo'),
(6, 'Cheque', 'Pago con cheque'),
(7, 'Criptomoneda', 'Pago con criptomonedas'),
(8, 'Móvil', 'Pago a través de aplicación móvil'),
(9, 'Contra reembolso', 'Pago al recibir el producto'),
(10, 'Financiamiento', 'Pago a plazos');

INSERT INTO Consumos VALUES
(1, 1, 4, '2023-11-01', 2),
(2, 2, 4, '2023-11-05', 1),
(3, 3, 4, '2023-11-10', 3),
(4, 4, 4, '2023-11-15', 2),
(5, 5, 4, '2023-11-20', 1),
(6, 6, 4, '2023-11-25', 2),
(7, 7, 4, '2023-11-30', 1),
(8, 8, 4, '2023-12-05', 3),
(9, 9, 4, '2023-12-10', 2),
(10, 10, 4, '2023-12-15', 1);

INSERT INTO Proveedores VALUES
(1, 'TechSupply Inc.', 'John Smith', 'john@techsupply.com', '111-222-3333'),
(2, 'FashionWholesale', 'Emma Johnson', 'emma@fashionwholesale.com', '222-333-4444'),
(3, 'HomeDecor Ltd.', 'Michael Brown', 'michael@homedecor.com', '333-444-5555'),
(4, 'FoodImport Co.', 'Sarah Davis', 'sarah@foodimport.com', '444-555-6666'),
(5, 'SportGear Distributors', 'David Wilson', 'david@sportgear.com', '555-666-7777'),
(6, 'BookMaster Publishing', 'Lisa Anderson', 'lisa@bookmaster.com', '666-777-8888'),
(7, 'ToyWorld Supplies', 'Robert Taylor', 'robert@toyworld.com', '777-888-9999'),
(8, 'BeautyEssentials Co.', 'Jennifer White', 'jennifer@beautyessentials.com', '888-999-0000'),
(9, 'GreenThumb Nursery', 'Thomas Green', 'thomas@greenthumb.com', '999-000-1111'),
(10, 'AutoParts Express', 'Patricia Black', 'patricia@autoparts.com', '000-111-2222');

-- Insertar datos en ComprasProveedores
INSERT INTO ComprasProveedores VALUES
(1, 1, '2023-10-01', 5000.00),
(2, 2, '2023-10-05', 3000.00),
(3, 3, '2023-10-10', 2000.00),
(4, 4, '2023-10-15', 1500.00),
(5, 5, '2023-10-20', 2500.00),
(6, 6, '2023-10-25', 1000.00),
(7, 7, '2023-10-30', 1800.00),
(8, 8, '2023-11-04', 2200.00),
(9, 9, '2023-11-09', 1300.00),
(10, 10, '2023-11-14', 3500.00);

-- Insertar datos en DetallesCompraProveedores
INSERT INTO DetallesCompraProveedores VALUES
(1, 1, 1, 10, 500.00, 5000.00),
(2, 2, 2, 200, 15.00, 3000.00),
(3, 3, 3, 50, 40.00, 2000.00),
(4, 4, 4, 150, 10.00, 1500.00),
(5, 5, 5, 100, 25.00, 2500.00),
(6, 6, 6, 100, 10.00, 1000.00),
(7, 7, 7, 100, 18.00, 1800.00),
(8, 8, 8, 100, 22.00, 2200.00),
(9, 9, 9, 100, 13.00, 1300.00),
(10, 10, 10, 100, 35.00, 3500.00);

-- Insertar datos en Devoluciones
INSERT INTO Devoluciones VALUES
(1, 1, '2023-11-05', 'Producto defectuoso'),
(2, 2, '2023-11-10', 'Talla incorrecta'),
(3, 3, '2023-11-15', 'Color equivocado'),
(4, 4, '2023-11-20', 'Producto dañado en transporte'),
(5, 5, '2023-11-25', 'No cumple expectativas'),
(6, 6, '2023-11-30', 'Libro equivocado'),
(7, 7, '2023-12-05', 'Juguete roto'),
(8, 8, '2023-12-10', 'Alergia al producto'),
(9, 9, '2023-12-15', 'Planta marchita'),
(10, 10, '2023-12-20', 'Pieza incompatible');

-- Insertar datos en DetallesDevolucion
INSERT INTO DetallesDevolucion VALUES
(1, 1, 1, 1, 599.99, 599.99),
(2, 2, 2, 1, 19.99, 19.99),
(3, 3, 3, 1, 39.99, 39.99),
(4, 4, 4, 2, 9.99, 19.98),
(5, 5, 5, 1, 29.99, 29.99),
(6, 6, 6, 1, 14.99, 14.99),
(7, 7, 7, 1, 24.99, 24.99),
(8, 8, 8, 1, 34.99, 34.99),
(9, 9, 9, 2, 12.99, 25.98),
(10, 10, 10, 1, 44.99, 44.99);

-- Insertar datos en Descuentos
INSERT INTO Descuentos VALUES
(1, 'Descuento de verano', 'Porcentaje', 10.00, '2023-06-01', '2023-08-31'),
(2, 'Oferta del mes', 'Monto fijo', 5.00, '2023-11-01', '2023-11-30'),
(3, 'Black Friday', 'Porcentaje', 20.00, '2023-11-24', '2023-11-24'),
(4, 'Navidad', 'Porcentaje', 15.00, '2023-12-15', '2023-12-25'),
(5, 'Año Nuevo', 'Monto fijo', 10.00, '2023-12-31', '2024-01-01'),
(6, 'San Valentín', 'Porcentaje', 5.00, '2024-02-14', '2024-02-14'),
(7, 'Día de la Madre', 'Monto fijo', 8.00, '2024-05-10', '2024-05-10'),
(8, 'Día del Padre', 'Porcentaje', 8.00, '2024-06-16', '2024-06-16'),
(9, 'Vuelta al Cole', 'Porcentaje', 12.00, '2024-08-15', '2024-09-15'),
(10, 'Cyber Monday', 'Porcentaje', 18.00, '2024-11-27', '2024-11-27');

-- Insertar datos en Impuestos
INSERT INTO Impuestos VALUES
(1, 'IVA General', 21.00),
(2, 'IVA Reducido', 10.00),
(3, 'IVA Superreducido', 4.00),
(4, 'Impuesto Especial', 15.00),
(5, 'Impuesto de Lujo', 30.00),
(6, 'Eco-tasa', 5.00),
(7, 'Impuesto Cultural', 2.50),
(8, 'Impuesto Turístico', 7.00),
(9, 'Tasa Municipal', 1.50),
(10, 'Impuesto al Carbono', 3.00);

-- Insertar datos en Empleados
INSERT INTO Empleados VALUES
(1, 'Ana', 'García', 'Gerente de Ventas', '2020-01-15', 4500.00),
(2, 'Pablo', 'Martínez', 'Representante de Servicio al Cliente', '2020-03-20', 2800.00),
(3, 'Lucía', 'Fernández', 'Contadora', '2020-05-10', 3800.00),
(4, 'Diego', 'López', 'Técnico de TI', '2020-07-05', 3500.00),
(5, 'Marta', 'Sánchez', 'Asistente de Marketing', '2020-09-15', 2600.00),
(6, 'Javier', 'Rodríguez', 'Analista de Datos', '2021-01-10', 3200.00),
(7, 'Carmen', 'Pérez', 'Recursos Humanos', '2021-03-22', 3000.00),
(8, 'Alberto', 'Gómez', 'Gerente de Logística', '2021-06-01', 4200.00),
(9, 'Isabel', 'Torres', 'Diseñadora Gráfica', '2021-08-15', 2900.00),
(10, 'Raúl', 'Herrera', 'Analista Financiero', '2021-11-05', 3600.00);