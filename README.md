# Proyectos_ifaco
En este repositorio se encuentran los proyectos soportados en la versión de Odoo 11.0+e-20180925

Versión 11.01.02.84--BETA
======================
Publicada: 25/01/2019

Cambios:

* Agregar columna a ordenes de compra
* Al momento de recibir producto que se indique en odoo quien recibió, que se muestre y especifique en la entrada
* Es necesario que el usuario especifique el almacen/ubicación donde entrará el producto
* Campos obligatorios: - entregar en: - persona que recibe
* Nombre para las solicitudes de compra
* Es necesario saber a que almacén / ubicación va a entrar el producto en la entrada
* Mostrar campos precio de compra y linea de compra, en el menú recibir
* Campos obligatorios plazo de pago
* Fac064 - mostrar el campo folio fiscal solo en menú de pagos de clientes
* Af013 - poliza y plantilla de amortización de seguros
* Roles de usuario contabilidad
* Cxc016 - incluir en el pdf de todos los cfdi's el nodo cfdi relación cuando exista en el xml.
* Tipo de cambio en poliza

Correcciones:

* Sistema crea entradas en pickings encadenados a oc
* Que al cancelar pago, no cambie el folio o no lo sustituya por uno nuevo
* Quitar permisos de creación de contactos
* Restringir menú de entradas
* Leyenda "términos y condiciones en sc y oc
* El domicilio registrado al dar de alta al proveedor no aparece completo en la oc
* Restringir menú facturas de proveedor en compras
* Que solo jefes y gerentes de compras y contador y responsable planeación puedan actualizar la info del producto en el campo categoría interna
* Que solo contabilidad pueda crear y actualizar las categorías internas de productos
* Permiso de creación de contactos
* Quitar permiso crear cuentas y etiquetas analíticas
* Revisar permiso de creación de productos
* Fac063 - mostrar el botón de reintentar cuando una factura se quede en "para cancelar"

Modulos agregados:

* Res_currency_reverse


Versión 11.01.02.84--BETA
======================
Publicada: 15/01/2019

Cambios:

* Campo moneda al registrar factura
* Roles de Usuario Contablidad
* Impresión de cheques
* Mejoras en el monitor
* Al timbrar una factura, que force a que la fecha de la factura sea la del día actual.
* Dias de vencimiento trascurridos en reporte de partidas vivas
* Se agrega la vista de folio fiscal en el menú de pagos
* Se agregaron los Campos de Poliza y Factura
* Organizar Roles Ventas
*   


Correcciones:

* Campo Fecha de pago en PDF de CFDI de pagos aparece vacio
* Se modifica el reporte del xml de Pago10 a pago10


Versión 11.01.01.0--ALPHA
===========================
Publicada: 8/11/18

Versión en producción

Cambios:

* Se actualiza el repositorio de Github con la versión actual de producción de Odoo


[PLANTILLA]
Versión [Versión Odoo].[Versión producción].[Versión pruebas].[Commits]--[Nombre de la versión]
===================
Publicada: [Día]/[Mes]/[Año]

Cambios:

* Cambio 1
* Cambio 2

Correcciones:

* Corrección 1
* Corrección 2

Módulos agregados:

* Módulo 1
* Módulo 2





