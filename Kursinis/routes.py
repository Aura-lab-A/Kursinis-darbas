from flask import Flask, render_template, request, Response, redirect, url_for, session, flash
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
# import secrets
# from PIL import Image
# from flask_mail import Message
from Kursinis import forms, db, app, bcrypt
from Kursinis.models import User, Product, Photo, Size, Color, Cart, OrderedItems, Orders, DeliveryInfo



#Šito gal nereikia?
@app.route('/base')
def base() -> Response:
    return render_template('base.html')

@app.route('/home')
def home() -> Response:    #useriu cookies
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registracija sėkminga! Galite prisijungti.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)          
            next_page = request.args.get('next')  #kas cia?
            return redirect(next_page) if next_page else redirect(url_for('login'))
        else:
            flash('El. paštas arba slaptažodis nėra teisingi.', 'danger')
    return render_template('login.html', form=form)


# Profilis
@app.route('/account')
@login_required
def account():  
    return render_template('account.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# @app.route("/paskyra", methods=['GET', 'POST'])
# @login_required
# def paskyra():
#     form = forms.PaskyrosAtnaujinimoForma()
#     if form.validate_on_submit():
#         if form.nuotrauka.data:
#             nuotrauka = save_picture(form.nuotrauka.data)
#             current_user.nuotrauka = nuotrauka
#         current_user.vardas = form.vardas.data
#         current_user.el_pastas = form.el_pastas.data
#         db.session.commit()
#         flash('Tavo paskyra atnaujinta!', 'success')
#         return redirect(url_for('paskyra'))
#     elif request.method == 'GET':
#         form.vardas.data = current_user.vardas
#         form.el_pastas.data = current_user.el_pastas
#     nuotrauka = url_for('static', filename='profilio_nuotraukos/' + current_user.nuotrauka)
#     return render_template('paskyra.html', title='Account', form=form, nuotrauka=nuotrauka)


# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Slaptažodžio atnaujinimo užklausa',
#                   sender='pythonkursascodeacademy@gmail.com',
#                   recipients=[user.el_pastas])
#     msg.body = f'''Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
#     {url_for('reset_token', token=token, _external=True)}
#     Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
#     '''
#     print(msg.body)
#     # mail.send(msg)

# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = forms.UzklausosAtnaujinimoForma()
#     if form.validate_on_submit():
#         user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
#         send_reset_email(user)
#         flash('Jums išsiųstas el. laiškas su slaptažodžio atnaujinimo instrukcijomis.', 'info')
#         return redirect(url_for('prisijungti'))
#     return render_template('reset_request.html', title='Reset Password', form=form)


# @app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     user = Vartotojas.verify_reset_token(token)
#     if user is None:
#         flash('Užklausa netinkama arba pasibaigusio galiojimo', 'warning')
#         return redirect(url_for('reset_request'))
#     form = forms.SlaptazodzioAtnaujinimoForma()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.slaptazodis.data).decode('utf-8')
#         user.slaptazodis = hashed_password
#         db.session.commit()
#         flash('Tavo slaptažodis buvo atnaujintas! Gali prisijungti', 'success')
#         return redirect(url_for('prisijungti'))
#     return render_template('reset_token.html', title='Reset Password', form=form)



# @app.route('/search', methods=['POST'])
# def search():
#     query = request.form['query']
#     # Perform search and return results
#     return render_template('results.html', query=query, results=results)


@app.route('/printai')
def printai() -> Response:
    db.create_all()
    page = request.args.get('page', 1, type=int)
    all_prints = Product.query.filter_by(category ='print').paginate(page=page, per_page=6)
    print_ids = [print_item.id for print_item in all_prints.items]
    all_photos = Photo.query.filter(Photo.product_id.in_(print_ids)).all()

    print("Products found:", [product.name for product in all_prints.items])
    print("Photos found:", [photo.name for photo in all_photos])

    return render_template('printai.html', all_prints=all_prints, all_photos=all_photos)

@app.route('/zvakes')
def zvakes() -> Response:
    return render_template('zvakes.html')

@app.route('/kazkas')
def kazkas() -> Response:
    return render_template('kazkas.html')

@app.route('/produktas/<int:product_id>', methods=['GET', 'POST'])
def produktas(product_id) -> Response:
    if request.method == 'GET':
        db.create_all()
        produktas = Product.query.get(product_id)
        max_quantity = produktas.quantity
        sizes = produktas.sizes
        colors = produktas.colors
        photos = produktas.photos
        other_products = Product.query.filter(
            Product.category == produktas.category,
            Product.id != produktas.id,
            ).limit(3)
        other_product_ids = [product.id for product in other_products]
        other_photos = Photo.query.filter(Photo.product_id.in_(other_product_ids)).all()
        return render_template('produktas.html', produktas=produktas, sizes=sizes, colors=colors, photos=photos, max_quantity=max_quantity, other_products=other_products, other_photos=other_photos)
    
    else:
    # print(request.form)
    # form = Cart()
    # if form.validate_on_submit():
        db.create_all()
        produktas = Product.query.get(product_id)
        # product_exists = Cart.query.filter_by(Cart.product_id==product_id).first()
        # if product_exists:
        #     try:
        #         product_exists.quantity = product_exists.quantity+int(request.form.get("quantity"))
        #         db.session.commit()
        #         flash(f'{product_exists.product_name} kiekis buvo atnaujintas.')
        #     except Exception as e:
        #         flash(f'{product_exists.product_name} kiekis nebuvo atnaujintas.')
        item_in_cart = Cart(
            product_id = produktas.id,
            product_name = produktas.name,
            size = request.form.get("size"),
            color = request.form.get("color"),
            quantity = int(request.form.get("quantity")),
            price = produktas.price,
            added_at = datetime.now()
            # user
            )
        produktas.quantity -= item_in_cart.quantity     #here or when placing order?
        db.session.add(item_in_cart)
        db.session.commit()
        flash('Produktas perkeltas į krepšelį!', 'success')
        return redirect(url_for('produktas', product_id = product_id))    #peržiūrėti


def updated_cart():
    now = datetime.now()
    time_span = timedelta(minutes=10)
    old_items = Cart.query.filter(Cart.added_at < now - time_span).all()
    for old_item in old_items:
        db.session.delete(old_item)
    db.session.commit()
    items_in_cart = Cart.query.all()
    return items_in_cart


# products = {product.id: product for product in Product.query.all()}
# for old_item in old_items:
#     if old_item.product_id in products:
#         products[old_item.product_id].quantity += old_item.quantity

@app.route('/delete/<int:id>')
def delete_cart_item(id):
    item_in_cart = Cart.query.get(id)      #updated_cart()
    db.session.delete(item_in_cart)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/delete')
def delete_cart_items():
    items_in_cart = Cart.query.all()      #updated_cart()
    for item_in_cart in items_in_cart:
        db.session.delete(item_in_cart)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart', methods=['GET', 'POST'])    #gali b8ti total price per product in cart
def cart() -> Response:
    if request.method == 'GET':
        items_in_cart = updated_cart()      #updated_cart()
        items_in_cart_ids = [item.product_id for item in items_in_cart]
        items_in_cart_photos = Photo.query.filter(Photo.product_id.in_(items_in_cart_ids)).all()
        total_price = 0
        for item in items_in_cart:
            total_price += item.price * item.quantity
        return render_template('cart.html', items_in_cart=items_in_cart, total_price=total_price, items_in_cart_photos=items_in_cart_photos)
    else:
        oder_number = 'WTHI random number'
        items_in_cart = Cart.query.all()
        for item in items_in_cart:
            new_ordered_item = OrderedItems(
                product_id = item.product_id,
                product_name = item.product_name,
                size = item.size,
                color = item.color,
                quantity = int(item.quantity),
                price = item.price,
                oder_no = oder_number
                # user
                )
            db.session.add(new_ordered_item)
            # db.session.commit()    #not needed
        
        total_price = 0
        for item in items_in_cart:
            total_price += item.price * item.quantity
        new_order = Orders(
            order_no = oder_number,
            created_on = datetime.now(),
            total_price = total_price,
            status = 'status',
            # user_id 
            )
        db.session.add(new_order)
        db.session.commit()
        flash('Užsakymas rezervuotas!', 'success')
        return redirect(url_for('delivery', new_ordered_item=new_ordered_item, new_order=new_order, order_id=new_order.id))


@app.route('/delivery/<int:order_id>', methods=['GET', 'POST'])
def delivery(order_id) -> Response:
    order = Orders.query.get(order_id)
    form = forms.DeliveryInfoForm()
    if form.validate_on_submit():
        delivery_info = DeliveryInfo(
            order_no = order.order_no,
            name=form.name.data,
            surname=form.surname.data,             
            email=form.email.data,
            phone_no = form.phone_no.data,
            street=form.street.data,
            street_number=form.street_number.data,
            flat_number=form.flat_number.data,
            city=form.city.data,
            country=form.country.data,
            postal_code=form.postal_code.data,
            payment_method=form.payment_method.data
            #user
            )
        db.session.add(delivery_info)

        cart_items = Cart.query.all()
        for cart_item in cart_items:
            db.session.delete(cart_item)

        db.session.commit()
        flash('Užsakymas pateiktas sėkmingai!', 'success')
        return redirect(url_for('oder_info', delivery_info=delivery_info, order=order, order_id=order_id))
    return render_template('delivery.html', form=form, order_id=order_id)


@app.route('/oder_info/<int:order_id>')
def oder_info(order_id) -> Response:
    order = Orders.query.get(order_id)
    return render_template('order_info.html', order=order)

# Naujas užsakymas:
# @app.route('/new_entry', methods=['GET', 'POST'])
# @login_required
# def new_entry():
#     form = forms.EntryForm()
#     if form.validate_on_submit():
#         income_checked = request.form.get('income')
#         if income_checked:
#             new_entry = Entry(income=True,
#                           sum=form.sum.data, user_id=current_user.id)
#         else:
#             new_entry = Entry(income=False,
#                           sum=form.sum.data, user_id=current_user.id)
#         db.session.add(new_entry)
#         db.session.commit()
#         flash('Entry was created successfully', 'success')
#         return redirect(url_for('entries'))
#     return render_template('new_entry.html', form=form)

# Užsakymai:
# @app.route('/entries')
# @login_required
# def entries():
#     my_entries = Entry.query.filter_by(user_id=current_user.id).all()
#     return render_template('entries.html', all_entries=my_entries, datetime=datetime)




@app.route('/apie_mus')
def apie_mus() -> Response:
    return render_template('apie_mus.html')



#ADMIN !!!
@app.route("/admin")
@login_required
def admin():
    return redirect(url_for(admin))


@app.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = forms.ShopItemsForm()
        if form.validate_on_submit():
            add_product = Product(
                name = form.producy_name.data,
                description = form.description.data,
                price = form.price.data,
                quantity = form.quantity.data,
                category = form.category.data
            )
            db.session.add(add_product)
            db.session.commit()
            flash('Naujas produktas išaugotas sėkmingai!', 'success')
            return render_template('add-shop-items.html', form=form)
        return render_template('add-shop-items.html', form=form)
    return render_template('404.html')   # ar čia geras return?


@app.route('/display-shop-items', methods=['GET', 'POST'])
@login_required
def display_shop_items():
    if current_user.id == 1:
        products = Product.query.all()   #filer by added date maybe
        return render_template('display-shop-items.html', products=products)
    return render_template('404.html')   # ar čia geras return?


# @app.route("/update/<int:id>", methods=['GET', 'POST'])
# def update(id):
#     forma = forms.IrasasForm()
#     irasas = Irasas.query.get(id)
#     if forma.validate_on_submit():
#         irasas.pajamos = forma.pajamos.data
#         irasas.suma = forma.suma.data
#         db.session.commit()
#         return redirect(url_for('records'))
#     return render_template("update.html", form=forma, irasas=irasas)

# def save_picture(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     picture_path = os.path.join(app.root_path, 'static/profilio_nuotraukos', picture_fn)

#     output_size = (125, 125)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)

#     return picture_fn



@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


# @app.errorhandler(403)
# def klaida_403(klaida):
#     return render_template("403.html"), 403


# @app.errorhandler(500)
# def klaida_500(klaida):
#     return render_template("500.html"), 500