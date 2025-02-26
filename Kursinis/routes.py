from flask import render_template, request, Response, redirect, url_for, session, flash, make_response, g
import os
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import uuid
import secrets
from PIL import Image
from flask_mail import Message
from Kursinis import forms, db, app, bcrypt, mail
from Kursinis.models import User, Visitor, VisitorInquire, Product, Photo, Size, Color, Cart, OrderedItems, Orders, DeliveryInfo



#BASE

@app.route('/base')
def base() -> Response:
        return render_template('base.html')
 

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = Product.query.filter(or_(
        Product.name.like(f'%{query}%'),
        Product.description.like(f'%{query}%')
        )).all()
    return render_template('search_results.html', query=query, results=results)


#COOKIES

@app.before_request
def set_visitor_cookie():
    cookie_id = request.cookies.get('visitor_cookie')
    if not cookie_id:
        cookie_id = str(uuid.uuid4())
        visitor_cookie = Visitor(cookie_id=cookie_id)
        db.session.add(visitor_cookie)
        db.session.commit()
        response = make_response(redirect(request.path))
        response.set_cookie('visitor_cookie', cookie_id, max_age=30*24*60*60)  # Cookie expires in 30 days
        return response
    session['visitor_cookie_id'] = cookie_id


@app.route('/vistors_count')
def vistors_count(): 
    count = int(request.cookies.get('visitors count', 0)) 
    count = count+1
    output = 'You visited this page for '+str(count) + ' times'
    resp = make_response(output) 
    resp.set_cookie('visitors count', str(count)) 
    return resp 
  

@app.route('/get_vistors_count') 
def get_vistors_count(): 
    count = request.cookies.get('visitors count') 
    return count 


#REGISTRACIJA IR PROFILIS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        date_register = datetime.now()
        user = User(name=form.name.data, email=form.email.data, password=hashed_password, date_register=date_register)
        db.session.add(user)
        db.session.commit()
        flash('Registracija sėkminga! Galite prisijungti.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('El. paštas arba slaptažodis nėra teisingi.', 'danger')
    return render_template('login.html', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Slaptažodžio atnaujinimo užklausa',
                  sender='aurelija.kursai@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
    {url_for('reset_token', token=token, _external=True)}
    Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
    '''
    print(msg.body)
    # mail.send(msg)

@app.route("/password_request", methods=['GET', 'POST'])
def password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = forms.ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user.name)
        if user:
            send_reset_email(user)
            flash('Jums išsiųstas el. laiškas su slaptažodžio atnaujinimo instrukcijomis.', 'info')
        else:
            flash('Nerastas naudotojas su tokiu el. paštu.', 'warning')
        return redirect(url_for('login'))
    return render_template('password_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Užklausa netinkama arba pasibaigusio galiojimo', 'warning')
        return redirect(url_for('password_request'))
    form = forms.PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Tavo slaptažodis buvo atnaujintas! Gali prisijungti', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'GET':
        orders = Orders.query.filter(Orders.user_id == current_user.id).all()
        form = forms.AccountUpdateForm()
        return render_template('account.html', orders=orders, form=form)
    else:
        form = forms.AccountUpdateForm()
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Tavo paskyra atnaujinta!', 'success')
            return redirect(url_for('account'))
        

@app.route('/order_details/<int:order_id>')
@login_required
def order_details(order_id):
    order = Orders.query.filter(
        Orders.user_id == current_user.id,
        Orders.id == order_id).first()
    ordered_items = OrderedItems.query.filter_by(order_id = order_id).all()
    return render_template('order_details.html', order=order, ordered_items=ordered_items)



#PREKĖS IR UŽSAKYMAI

@app.route('/home', methods=['GET', 'POST'])
def home() -> Response:
    form = forms.ContactForm()
    if form.validate_on_submit():
        new_inquire = VisitorInquire(
            name = form.name.data,
            surname = form.surname.data,
            email = form.email.data,
            message = form.message.data
            )
        db.session.add(new_inquire)
        db.session.commit()
        flash('Žinutė išsiųsta!', 'success')
        return redirect(url_for('home', form=form))
    return render_template('home.html', form=form)


@app.route('/printai')
def printai() -> Response:
    page = request.args.get('page', 1, type=int)
    all_prints = Product.query.filter_by(category ='print').paginate(page=page, per_page=6)
    print_ids = [print_item.id for print_item in all_prints.items]
    subquery = db.session.query(
        Photo.product_id,
        func.min(Photo.id).label('min_id')
        ).filter(Photo.product_id.in_(print_ids)).group_by(Photo.product_id).subquery()
    all_photos = db.session.query(Photo).join(subquery, Photo.id == subquery.c.min_id).all()
    return render_template('printai.html', all_prints=all_prints, all_photos=all_photos)


@app.route('/zvakes')
def zvakes() -> Response:
    page = request.args.get('page', 1, type=int)
    all_candles = Product.query.filter_by(category ='candle').paginate(page=page, per_page=6)
    candle_ids = [candle_item.id for candle_item in all_candles.items]
    subquery = db.session.query(
        Photo.product_id,
        func.min(Photo.id).label('min_id')
        ).filter(Photo.product_id.in_(candle_ids)).group_by(Photo.product_id).subquery()
    all_photos = db.session.query(Photo).join(subquery, Photo.id == subquery.c.min_id).all()
    return render_template('zvakes.html', all_candles=all_candles, all_photos=all_photos)


@app.route('/kazkas')
def kazkas() -> Response:
    page = request.args.get('page', 1, type=int)
    all_smths = Product.query.filter_by(category ='smth').paginate(page=page, per_page=6)
    smth_ids = [smth_item.id for smth_item in all_smths.items]
    subquery = db.session.query(
        Photo.product_id,
        func.min(Photo.id).label('min_id')
        ).filter(Photo.product_id.in_(smth_ids)).group_by(Photo.product_id).subquery()
    all_photos = db.session.query(Photo).join(subquery, Photo.id == subquery.c.min_id).all()
    return render_template('kazkas.html', all_smths=all_smths, all_photos=all_photos)


@app.route('/produktas/<int:product_id>', methods=['GET', 'POST'])
def produktas(product_id) -> Response:

    if request.method == 'GET':
        produktas = Product.query.get(product_id)
        if not produktas:
            return "Toks produktas nerastas"
        else:
            max_quantity = produktas.quantity
            sizes = produktas.sizes
            colors = produktas.colors
            photos = produktas.photos
            other_products = Product.query.filter(
                Product.category == produktas.category,
                Product.id != produktas.id,
                ).limit(3)
            other_product_ids = [product.id for product in other_products]
            subquery = db.session.query(
                Photo.product_id,
                func.min(Photo.id).label('min_id')
                ).filter(Photo.product_id.in_(other_product_ids)).group_by(Photo.product_id).subquery()
            other_photos = db.session.query(Photo).join(subquery, Photo.id == subquery.c.min_id).all()
            return render_template('produktas.html', produktas=produktas, sizes=sizes, colors=colors, photos=photos, max_quantity=max_quantity, other_products=other_products, other_photos=other_photos)
    
    else:
        cookie_id = session.get('visitor_cookie_id')
        if not cookie_id:
            set_visitor_cookie()
            return redirect(url_for('produktas', product_id=product_id))
        visitor = Visitor.query.filter_by(cookie_id = cookie_id).first()        
        if current_user.is_authenticated:
            produktas = Product.query.get(product_id)
            if not produktas:
                return "Toks produktas nerastas"
            else:
                size = request.form.get("size")
                color = request.form.get("color")
                quantity = request.form.get("quantity")
                if size and color and quantity:
                    item_in_cart = Cart(
                        product_id = produktas.id,
                        product_name = produktas.name,
                        size = request.form.get("size"),
                        color = request.form.get("color"),
                        quantity = int(request.form.get("quantity")),
                        price = produktas.price,
                        sale_price = produktas.sale_price,
                        sale = produktas.sale,
                        added_at = datetime.now(),
                        user_id = current_user.id,
                        visitor_id = visitor.id
                        )
                    db.session.add(item_in_cart)
                    db.session.commit()
                    flash('Produktas perkeltas į krepšelį!', 'success')
                    return redirect(url_for('produktas', product_id = product_id))
                else:
                    flash('Būtina pasirinkti produkto dydį, spalvą ir kiekį!', 'warning')
                    return redirect(url_for('produktas', product_id = product_id))

        else:
            produktas = Product.query.get(product_id)
            if not produktas:
                return "Toks produktas nerastas"
            else:
                size = request.form.get("size")
                color = request.form.get("color")
                quantity = request.form.get("quantity")
                if size and color and quantity:
                    item_in_cart = Cart(
                        product_id = produktas.id,
                        product_name = produktas.name,
                        size = request.form.get("size"),
                        color = request.form.get("color"),
                        quantity = int(request.form.get("quantity")),
                        price = produktas.price,
                        sale_price = produktas.sale_price,
                        sale = produktas.sale,
                        added_at = datetime.now(),
                        visitor_id = visitor.id
                        )
                    db.session.add(item_in_cart)
                    db.session.commit()
                    flash('Produktas perkeltas į krepšelį!', 'success')
                    return redirect(url_for('produktas', product_id = product_id))
                else:
                    flash('Būtina pasirinkti produkto dydį, spalvą ir kiekį!', 'warning')
                    return redirect(url_for('produktas', product_id = product_id))
    

def updated_cart():
    now = datetime.now()
    time_span = timedelta(minutes=2)
    if current_user.is_authenticated:
        old_items = Cart.query.filter(Cart.added_at < now - time_span).all()
        for old_item in old_items:
            db.session.delete(old_item)
        db.session.commit()
        items_in_cart = Cart.query.filter_by(user_id = current_user.id).all()
        return items_in_cart
    else:
        cookie_id = session.get('visitor_cookie_id')
        if not cookie_id:
            set_visitor_cookie()
        old_items = Cart.query.filter(Cart.added_at < now - time_span).all()
        for old_item in old_items:
            db.session.delete(old_item)
        db.session.commit()
        items_in_cart = Cart.query.join(Visitor).filter(Visitor.cookie_id == cookie_id).all()    
        return items_in_cart
    

@app.before_request
def item_count():
    if current_user.is_authenticated:
        g.item_count = Cart.query.filter_by(user_id = current_user.id).count()
    else:
        cookie_id = session.get('visitor_cookie_id')
        if not cookie_id:
            set_visitor_cookie()
        g.item_count = Cart.query.join(Visitor).filter(Visitor.cookie_id == cookie_id).count()

@app.context_processor
def inject_item_count():
    return dict(item_count=g.item_count)


@app.route('/delete/<int:id>')
def delete_cart_item(id):
    if current_user.is_authenticated:   
        item_in_cart = Cart.query.filter_by(user_id = current_user.id).get(id)
        db.session.delete(item_in_cart)
        db.session.commit()
        return redirect(url_for('cart'))
    else:
        cookie_id = session.get('visitor_cookie_id')
        if not cookie_id:
            set_visitor_cookie()
        item_in_cart = Cart.query.join(Visitor).filter(Visitor.cookie_id == cookie_id, Cart.id == id).first()
        db.session.delete(item_in_cart)
        db.session.commit()
        return redirect(url_for('cart'))


@app.route('/delete')
def delete_cart_items():
    items_in_cart = updated_cart()
    for item_in_cart in items_in_cart:
        db.session.delete(item_in_cart)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart', methods=['GET', 'POST'])
def cart() -> Response:
    if request.method == 'GET':
        items_in_cart = updated_cart()
        if not items_in_cart:
            return "Krepšelyje prekių nėra."
        else:
            items_in_cart_ids = [item.product_id for item in items_in_cart]
            subquery = db.session.query(
                Photo.product_id,
                func.min(Photo.id).label('min_id')
                ).filter(Photo.product_id.in_(items_in_cart_ids)).group_by(Photo.product_id).subquery()
            items_in_cart_photos = db.session.query(Photo).join(subquery, Photo.id == subquery.c.min_id).all()
            total_price = sum((item.sale_price if item.sale else item.price) * item.quantity for item in items_in_cart)
            return render_template('cart.html', items_in_cart=items_in_cart, total_price=total_price, items_in_cart_photos=items_in_cart_photos)
    else:
        return redirect(url_for('order'))
    

def new_order_func(order_number, total_price, visitor):
    new_order = Orders(
        order_no = order_number,
        created_on = datetime.now(),
        total_price = total_price,
        status = 'Pateiktas',
        visitor_id = visitor.id
        )
    db.session.add(new_order)
    db.session.commit()
    return new_order


def new_order_func_user(order_number, total_price, current_user, visitor):
    new_order = Orders(
        order_no = order_number,
        created_on = datetime.now(),
        total_price = total_price,
        status = 'Pateiktas',
        user_id = current_user.id,
        visitor_id = visitor.id
        )
    db.session.add(new_order)
    db.session.commit()
    return new_order


def new_ordered_item_func(product_id, product_name, size, color, quantity, price, sale_price, sale, order_number, new_order):
    new_ordered_item = OrderedItems(
        product_id = product_id,
        product_name = product_name,
        size = size,
        color = color,
        quantity = int(quantity),
        price = price,
        sale_price = sale_price,
        sale = sale,
        order_no = order_number,
        order_id = new_order.id
        )
    db.session.add(new_order)
    db.session.commit()
    return new_ordered_item


def delivery_info_func(order_number, new_order):
    delivery_info = DeliveryInfo(
        name=request.form.get('name'),
        surname=request.form.get('surname'),             
        email=request.form.get('email'),
        phone_no = request.form.get('phone_no'),
        street=request.form.get('street'),
        street_number=request.form.get('street_number'),
        flat_number=request.form.get('flat_number'),
        city=request.form.get('city'),
        country=request.form.get('country'),
        postal_code=request.form.get('postal_code'),
        order_no = order_number,
        order_id = new_order.id,
        )
    db.session.add(delivery_info)
    db.session.commit()
    return delivery_info


@app.route('/order', methods=['GET', 'POST'])
def order() -> Response:
    cookie_id = session.get('visitor_cookie_id')
    if not cookie_id:
        return set_visitor_cookie()
    visitor = Visitor.query.filter_by(cookie_id = cookie_id).first()
    if request.method == 'GET':
        items_in_cart = updated_cart()
        if not items_in_cart:
            return "Krepšelyje prekių nėra."
        else:
            total_price = sum((item.sale_price if item.sale else item.price) * item.quantity for item in items_in_cart)
            form = forms.DeliveryInfoForm()
            return render_template('order.html', items_in_cart=items_in_cart, total_price=total_price, form=form)
    else:
        if current_user.is_authenticated:
            items_in_cart = updated_cart()
            if not items_in_cart:
                return "Krepšelyje prekių nėra."
            else:
                order_number = 'E-SHOP-' + str(uuid.uuid4())
                total_price = sum((item.sale_price if item.sale else item.price) * item.quantity for item in items_in_cart)

                new_order = new_order_func_user(order_number, total_price, current_user, visitor)

                for item in items_in_cart:
                    new_ordered_item = new_ordered_item_func(item.product_id, item.product_name, item.size, item.color, item.quantity, item.price, item.sale_price, item.sale, order_number, new_order)
                    db.session.add(new_ordered_item)
                    db.session.commit()
                        
                form = forms.DeliveryInfoForm()
                delivery_info = delivery_info_func(order_number, new_order)
                db.session.add(delivery_info)

                for ordered_item in items_in_cart:
                    product_item = Product.query.filter_by(id = ordered_item.product_id).first()
                    product_item.quantity -= ordered_item.quantity
                    db.session.commit()

                for ordered_item in items_in_cart:
                    db.session.delete(ordered_item)

                db.session.commit()

                flash('Užsakymas pateiktas sėkmingai!', 'success')
                return redirect(url_for('order_info', order_id=new_order.id, form=form))
            
        else:
            items_in_cart = updated_cart()
            if not items_in_cart:
                return "Krepšelyje prekių nėra."
            else:
                order_number = 'E-SHOP-' + str(uuid.uuid4())
                total_price = sum((item.sale_price if item.sale else item.price) * item.quantity for item in items_in_cart)

                new_order = new_order_func(order_number, total_price, visitor)

                for item in items_in_cart:
                    new_ordered_item = new_ordered_item_func(item.product_id, item.product_name, item.size, item.color, item.quantity, item.price, item.sale_price, item.sale, order_number, new_order)
                    db.session.add(new_ordered_item)
                    db.session.commit()
                        
                form = forms.DeliveryInfoForm()
                delivery_info = delivery_info_func(order_number, new_order)

                for ordered_item in items_in_cart:
                    product_item = Product.query.filter_by(id = ordered_item.product_id).first()
                    product_item.quantity -= ordered_item.quantity
                    db.session.commit()

                for ordered_item in items_in_cart:
                    db.session.delete(ordered_item)
                
                db.session.commit()

                flash('Užsakymas pateiktas sėkmingai!', 'success')
                return redirect(url_for('order_info', order_id=new_order.id, form=form))


@app.route('/order_info/<int:order_id>')
def order_info(order_id) -> Response:
    if current_user.is_authenticated:
        order = Orders.query.filter(
            Orders.id == order_id,
            Orders.user_id == current_user.id).first()
        if not order:
            return "Toks užsakymas nerastas."
        return render_template('order_info.html', order=order)
    else:
        cookie_id = session.get('visitor_cookie_id')
        if not cookie_id:
            return set_visitor_cookie()
        visitor = Visitor.query.filter_by(cookie_id = cookie_id).first()
        order = Orders.query.filter(
            Orders.id == order_id,
            Orders.visitor_id == visitor.id).first()
        if not order:
            return "Toks užsakymas nerastas."
        return render_template('order_info.html', order=order)



#APIE MUS

@app.route('/apie_mus')
def apie_mus() -> Response:
    return render_template('apie_mus.html')



#ADMINISTRATORIUS

@app.route('/admin_page')
@login_required
def admin_page():
    return render_template('admin_page.html')


@app.route('/display_shop_items', methods=['GET', 'POST'])
@login_required
def display_shop_items():
    if current_user.name == 'admin':
        products = Product.query.all()
        return render_template('display_shop_items.html', products=products)
    return render_template('404.html')


@app.route('/add_shop_items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.name == 'admin':
        form = forms.ShopItemsForm()
        if form.validate_on_submit():
            add_product = Product(
                name = form.name.data,
                description = form.description.data,
                price = form.price.data,
                sale_price = form.sale_price.data,
                sale = form.sale.data,
                quantity = form.quantity.data,
                category = form.category.data,
                date_added = datetime.now()
            )
            db.session.add(add_product)
            db.session.commit()
            flash('Naujas produktas išaugotas sėkmingai!', 'success')
            return redirect(url_for('add_photo', product_id=add_product.id))
        return render_template('add_shop_items.html', form=form)
    return render_template('404.html')


def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
        i = Image.open(form_picture)
        i.save(picture_path)
        return picture_fn


@app.route('/add_photo/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_photo(product_id):
    if current_user.name == 'admin':
        form = forms.AddPhotoForm()
        if form.validate_on_submit():
            if form.photo1.data:
                photo_filename1 = save_picture(form.photo1.data)
                add_photo1 = Photo(
                    name = photo_filename1,
                    product_id = product_id
                    )
                db.session.add(add_photo1)
            if form.photo2.data:
                photo_filename2 = save_picture(form.photo2.data)
                add_photo2 = Photo(
                    name = photo_filename2,
                    product_id = product_id
                    )
                db.session.add(add_photo2)
            if form.photo3.data:
                photo_filename3 = save_picture(form.photo3.data)
                add_photo3 = Photo(
                    name = photo_filename3,
                    product_id = product_id
                    )
                db.session.add(add_photo3)
            db.session.commit()
            flash('Nuotraukos išaugotos sėkmingai!', 'success')
            return redirect(url_for('add_color_size', product_id=product_id))
        return render_template('add_photo.html', form=form, product_id=product_id)
    return render_template('404.html')


@app.route('/add_color_size/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_color_size(product_id):
    if current_user.name == 'admin':
        product = Product.query.get(product_id)
        if request.method == 'POST':
            color_id = request.form.get('color')
            size_id = request.form.get('size')

            color = Color.query.get(color_id)
            size = Size.query.get(size_id)

            if color and size:
                product.colors.append(color)
                product.sizes.append(size)
                db.session.commit()
                flash('Color and size added successfully!', 'success')
            else:
                flash('Invalid color or size selected.', 'danger')

            return redirect(url_for('add_color_size', product_id=product_id))
                                            
        colors = Color.query.all()
        sizes = Size.query.all()
        return render_template('add_color_size.html', product=product, colors=colors, sizes=sizes)  
    return render_template('404.html')


@app.route("/update_shop_item/<int:product_id>", methods=['GET', 'POST'])
@login_required
def update_shop_item(product_id):
    if current_user.name == 'admin':
        
        form = forms.ShopItemsForm()
        product_to_update = Product.query.get(product_id)

        form.name.render_kw = {'placeholder': product_to_update.name}
        form.description.render_kw = {'placeholder': product_to_update.description}
        form.price.render_kw = {'placeholder': product_to_update.price}
        form.sale_price.render_kw = {'placeholder': product_to_update.sale_price}
        form.sale.render_kw = {'placeholder': product_to_update.sale}
        form.quantity.render_kw = {'placeholder': product_to_update.quantity}
        form.category.render_kw = {'placeholder': product_to_update.category}

        if form.validate_on_submit():
            product_to_update.name = form.name.data
            product_to_update.description = form.description.data
            product_to_update.price = form.price.data
            product_to_update.sale_price = form.sale_price.data
            product_to_update.sale = form.sale.data
            product_to_update.quantity = form.quantity.data
            product_to_update.category = form.category.data
            db.session.commit()
            flash('Produktas atnaujintas sėkmingai!', 'success')
            return redirect(url_for('display_shop_items'))
        return render_template('update_shop_item.html', form=form, product_to_update=product_to_update)
    return render_template('404.html')


@app.route("/delete_shop_item/<int:product_id>", methods=['GET', 'POST'])
@login_required
def delete_shop_item(product_id):
    if current_user.name == 'admin':
        product_to_delete = Product.query.get(product_id)
        db.session.delete(product_to_delete)
        db.session.commit()
        flash('Produktas ištrintas sėkmingai!', 'success')
        return redirect(url_for('display_shop_items'))
    return render_template('404.html')

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if current_user.name == 'admin':
        all_orders = Orders.query.all()
        return render_template('orders.html', all_orders=all_orders)
    return render_template('404.html')

@app.route('/update_order_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order_status(order_id):
    if current_user.name == 'admin':
        order_statuses = ['Pateiktas', 'Paruoštas', 'Išsiųstas', 'Baigtas', 'Problema']
        order = Orders.query.get(order_id)
        if request.method == 'POST':
            order.status = request.form.get("status")
            db.session.commit()
            flash('Statusas pakeistas sėkmingai!', 'success')
            return redirect(url_for('orders'))
        return render_template('update_order_status.html', order=order, order_statuses=order_statuses)
    return render_template('404.html')


@app.route('/display_visitor_inquires', methods=['GET', 'POST'])
@login_required
def display_visitor_inquires():
    if current_user.name == 'admin':
        inquires = VisitorInquire.query.all()
        return render_template('display_visitor_inquires.html', inquires=inquires)
    return render_template('404.html')
           


#KLAIDOS

@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


@app.errorhandler(403)
def error_403(error):
    return render_template("403.html"), 403


@app.errorhandler(500)
def error_500(error):
    return render_template("500.html"), 500