#!/usr/bin/env python
import csv
import preparaCsv
import validacion
import busqueda


from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
# from flask_moment import Moment
from flask_script import Manager
from forms import LoginForm, SaludarForm, RegistrarForm, ProductForm, ClienteForm

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

# Validacion del archivo csv
nombre_de_archivo = 'farmacia.csv'
validacion.validar(nombre_de_archivo)
registros = preparaCsv.genera_clase(nombre_de_archivo)




# moment = Moment(app)

app.config['SECRET_KEY'] = 'un string que funcione como llave'

@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow())

@app.route('/saludar', methods=['GET', 'POST'])
def saludar():
    formulario = SaludarForm()
    if formulario.validate_on_submit():
        print(formulario.usuario.name)
        return redirect(url_for('saludar_persona', usuario=formulario.usuario.data))
    return render_template('saludar.html', form=formulario)

@app.route('/saludar/<usuario>')
def saludar_persona(usuario):
    return render_template('usuarios.html', nombre=usuario)

@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    flash('Bienvenido')
                    session['username'] = formulario.usuario.data
                    return render_template('ingresado.html')
                registro = next(archivo_csv, None)
            else:
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        if formulario.password.data == formulario.password_check.data:
            with open('usuarios', 'a+') as archivo:
                archivo_csv = csv.writer(archivo)
                registro = [formulario.usuario.data, formulario.password.data]
                archivo_csv.writerow(registro)
            flash('Usuario creado correctamente')
            return redirect(url_for('ingresar'))
        else:
            flash('Las passwords no matchean')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')

@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return redirect(url_for('index'))

####
# Mostrar las últimas ventas
@app.route('/ultimas_ventas', methods=['GET', 'POST'])
def ultimas_ventas():
    if 'username' in session:   
        ultimos = 5
        last_s = []
        last_s=busqueda.listar_ventas(registros, ultimos)
        return render_template('ultimas_ventas.html',last_s=last_s)
    else:
        flash('Para acceder debe estar logueado.')
        return redirect(url_for('ingresar'))

# Productos buscados por cliente
@app.route('/pXclientes', methods=['GET', 'POST'])
def pXclientes():
    if 'username' in session:
        formulario = ClienteForm()
        if formulario.validate_on_submit():
            cliente = formulario.cliente.data.upper()
            if len(cliente) < 3:
                flash('Debe tipear 3 caracteres como mínimo para poder realizar la busqueda')
                return render_template('pXclientes.html', form = formulario)
            else:
                val = busqueda.encontrar_clientes(registros,cliente)#llama a funcion para validar si exiten los clientes
                if len(val) == 0:
                    flash('No seencontraron registros')
                elif len(val) == 1:
                    listar = busqueda.listar_productos_cliente(registros,cliente)
                    return render_template('pXclientes.html', form = formulario, listar = listar, cliente= formulario.cliente.data.upper())
                else:
                    flash('Se encontraron registros, seleccione uno.')
                    return render_template('pXclientes.html', form = formulario, clientes = val)
        return render_template('pXclientes.html', form = formulario)
    else:
        flash('Para poder ingresar debeestar logueado.')
        return redirect(url_for('ingresar'))

# Clientes buscados por productos
@app.route('/clientes_prod', methods=['GET', 'POST'])
def clientes_prod():
    if 'username' in session:
        formulario = ProductForm()
        if formulario.validate_on_submit():
            producto = formulario.producto.data.upper()
            if len(producto) < 3:
                flash('Debe tipear al menos tres caracteres para poder realizar la búsqueda.')
                return render_template('clientes_prod.html', form=formulario)
            else:
                val = busqueda.encontrar_productos(registros, producto)
                if len(val) == 0:
                    flash('No se encontraron registros.')
                elif len(val) == 1:
                    listar = busqueda.listar_clientes_producto(registros,producto)
                    return render_template('clientes_prod.html', form = formulario, listar = listar, producto= formulario.producto.data.upper())
                else:
                    flash('Se encontraron registros, seleccione uno.')
                    return render_template('clientes_prod.html', form = formulario, productos = val)
        return render_template('clientes_prod.html', form=formulario)
    else:
        flash('Para poder acceder debe estar logueado.')
        return redirect(url_for('ingresar'))

# Listado de productos
@app.route('/mas_vendidos', methods=['GET', 'POST'])
def mas_vendidos():
    if 'username' in session:
        producto_res = []
        cantidad = 5
        producto_res = busqueda.mas_vendidos(registros = registros, cantidad=cantidad)
        return render_template('mas_vendidos.html', producto_res = producto_res)
    else:
        flash('Para poder acceder debe estar logueado.')
        return redirect(url_for('ingresar'))

# Clientes que más gastaron en compras
@app.route('/mejoresClientes', methods=['GET', 'POST'])
def mejoresClientes():
    if 'username' in session:
        producto_res = []
        cantidad = 5
        producto_res = busqueda.mas_gastaron(registros = registros, cantidad=cantidad)
        return render_template('mejoresClientes.html', producto_res = producto_res)
    else:
        flash('Para poder acceder debe estar logueado.')
        return redirect(url_for('ingresar'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    manager.run()
