import os
import traceback

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678987654321'
basedir = os.path.abspath(os.path.dirname(__file__))

# Setting app configuration data
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)

# Created an instance of the database and called it db
db = SQLAlchemy(app)


# Database classes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # represent a class's objects as a string
    def __repr__(self):
        return f'<User {self.name}>'


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Sign Up')

# Product/treatment table
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description1 = db.Column(db.String(1024))
    description2 = db.Column(db.String(1024))

    # represent a class's objects as a string
    def __repr__(self):
        return f'<Product {self.name}>'

# Cart item table (id, quantity, product)
class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship(
        'Product', backref=db.backref('cart_items', lazy=True))

    # represent a class's objects as a string
    def __repr__(self):
        return f"CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})"

# Customer (id, first_name, last_name, cell_phone, email, orders)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    cell_phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

# Order (id, customer_id)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

# orderItem (id, order_id, product_id, quantity)
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Forms Classes 
# checkoutForm (first_name, last_name, cell_phone, email)
class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    cell_phone = StringField('Cell Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')


# Templates routes
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')

    print('product_id: ', product_id, ' quantity: ', quantity)
    product = db.session.query(Product).filter_by(product_id=1).first()
    # Create the form instance with the request form data
    add_to_cart_form = AddToCartForm(request.form)

    if product and add_to_cart_form.validate_on_submit():
        quantity = add_to_cart_form.quantity.data
        print('product_id: ', product_id, ' quantity: ', quantity)

        # Add the product to the cart
        cart_item = CartItem(product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
        db.session.commit()

        flash(f'{product.name} added to cart!', 'success')
    else:
        # Form validation failed
        print("Form validation failed")
        print("Form errors:", add_to_cart_form.errors)

        flash('Product not found or invalid quantity!', 'danger')

    return redirect('appointment.html')

# Checkout route
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Clear the cart after successful checkout
        CartItem.query.delete()
        db.session.commit()

        flash('Checkout successful! Thank you for your purchase!', 'success')
        return redirect(url_for('index'))

    return render_template('checkout.html')

# index function route
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SignupForm()
    add_to_cart_form = AddToCartForm()

    return render_template('landing.html', form=form, add_to_cart_form=add_to_cart_form)

# musculoskeletal route
@app.route('/musculokeletal.html')
def musculokeletal():
    return render_template('musculokeletal.html')

# neurotherpay route
@app.route('/neurotherapy.html')
def neurotherapy():
    return render_template('neurotherapy.html')

# Contact route
@app.route('/contact.html')
def contact():
    return render_template('contact.html')

# Appointment route
@app.route('/appointment.html')
def appointment():
    add_to_cart_form = AddToCartForm()

    return render_template('appointment.html', add_to_cart_form=add_to_cart_form)

# Cart route
@app.route('/cart.html', methods=['POST', 'GET'])
def cart():
    cart_items = CartItem.query.all()
    add_to_cart_form = AddToCartForm()
    if not cart_items:
        flash('Your cart is empty.', 'info')

        return redirect(url_for('appointment'))

    return render_template('cart.html', cart_items=cart_items, add_to_cart_form=add_to_cart_form)

# Delete treatment/product from cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    cart_item_id = request.form.get('cart_item_id')

    cart_item = CartItem.query.get(cart_item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    else:
        flash('Item not found in cart!', 'danger')

    return redirect(url_for('cart'))

# Product details route
@app.route('/product_details', methods=['POST'])
def product_details():
    add_to_cart_form = AddToCartForm()

    products = Product.query.all()

    # Prepare the data to pass to the template
    cart_items = [
        {'product_id': product.product_id,
            'name': product.name, 'price': product.price}
        for product in products
    ]

    # Render the cart template with the product data
    return render_template('product_details.html', add_to_cart_form=add_to_cart_form, cart_items=cart_items)

# Search for product on landing page
@app.route('/product_search', methods=['GET', 'POST'])
def product_search():
    add_to_cart_form = AddToCartForm()

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        products = Product.query.filter(
            Product.name.ilike(f"%{search_query}%")).all()

        # Prepare the data to pass to the template
        cart_items = [
            {'product_id': product.product_id, 'name': product.name, 'price': product.price,
             'desc1': product.description1, 'desc2': product.description2}
            for product in products
        ]
        for product in products:
            print(product.name, product.description1, product.description2)

        if len(cart_items):
            return render_template('product_details_qresult.html', add_to_cart_form=add_to_cart_form, cart_items=cart_items)
        else:
            flash('Empty result for your search!', 'message')
            return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/do_checkout', methods=['POST'])
def do_checkout():
    add_to_cart_form = AddToCartForm()

    return render_template('checkout.html', add_to_cart_form=add_to_cart_form)

# Checkout form
@app.route('/proc_checkout', methods=['POST'])
def proc_checkout():
    form = CheckoutForm(request.form)

    if form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        cell_phone = form.cell_phone.data
        email = form.email.data

        # Save customer to the database
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            cell_phone=cell_phone,
            email=email)
        db.session.add(customer)
        db.session.commit()

        # Save cart items to the order
        cart_items = CartItem.query.all()
        order = Order(customer_id=customer.id)

        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity)
            db.session.add(order_item)

        db.session.commit()

        # Empty the cart
        CartItem.query.delete()
        db.session.commit()

        flash('Checkout successful!', 'success')
        return redirect(url_for('appointment'))
    else:
        flash('Invalid form data. Please check your input.', 'error')
        return redirect(url_for('cart'))


# To maintain track of the application-level data during a request
if __name__ == '__main__':
    with app.app_context() as ctxt:
        db.create_all()

        product_count = Product.query.count()

        if product_count == 0:
            try:
                new_product = Product(product_id=1,
                                      name="Principal Physiotherapist Initial Consultation (40mins)",
                                      price=130,
                                      description1='The "Principal Physiotherapist Initial Consultation (40mins)" is a comprehensive and focused session designed to provide individuals with a thorough assessment and expert guidance on their specific physical concerns. As the principal physiotherapist, this professional is highly experienced, knowledgeable, and skilled in diagnosing and treating a wide range of musculoskeletal conditions.\n The initial consultation typically lasts for approximately 40 minutes, ensuring there is sufficient time to address the individual`s concerns, perform a detailed assessment, and develop an appropriate treatment plan. The session usually takes place in a comfortable and private setting, such as a physiotherapy clinic or healthcare facility.\n During the consultation, the principal physiotherapist will begin by engaging in a conversation with the individual to gather more information about their symptoms, medical history, and any specific activities or movements that may exacerbate or alleviate their condition. This discussion helps the physiotherapist gain a comprehensive understanding of the individual\'s condition and its impact on their daily life.\n Afterward, the principal physiotherapist will perform a thorough physical examination, which may involve assessing joint mobility, muscle strength, posture, balance, and flexibility. They may also employ specialized tests and measures to further evaluate the individual\'s condition, such as range of motion assessments, palpation of affected areas, or specific functional tests.\n Based on the information gathered from the discussion and physical examination, the principal physiotherapist will then provide a detailed explanation of the diagnosis, outlining the underlying causes of the individual`s symptoms. They will discuss the treatment options available and develop a personalized treatment plan tailored to the individual`s needs, goals, and lifestyle.\n',
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=2,
                                      name="Principal Physiotherapist Subsequent Consultation (30mins)",
                                      price=110,
                                      description1="The \"Principal Physiotherapist Subsequent Consultation (30mins)\" is a follow-up session that builds on the initial consultation, focusing on monitoring progress, adjusting treatment plans as needed, and providing ongoing support.\nThe subsequent consultation, lasting approximately 30 minutes, allows the principal physiotherapist to assess the individual's response to treatment and make necessary modifications. It takes place in a similar setting as the initial consultation, such as a physiotherapy clinic.\nDuring the subsequent consultation, the principal physiotherapist engages in a conversation with the individual to gather feedback on progress since the last session. They inquire about changes in symptoms, functional abilities, or challenges faced. This discussion helps the physiotherapist evaluate the effectiveness of the initial intervention.\nFollowing the discussion, the principal physiotherapist performs a focused assessment to evaluate the current condition. This involves reassessing range of motion, muscle strength, functional movements, or specific tests relevant to the case. The physiotherapist compares findings to the initial consultation to track progress accurately.\nBased on the assessment and feedback, the principal physiotherapist adjusts the treatment plan. This may involve modifying exercise intensity or frequency, introducing new techniques or modalities, or additional interventions. The physiotherapist explains the rationale behind these adjustments and their contribution to overall recovery.\nDuring the subsequent consultation, the individual can discuss concerns, ask questions, and seek clarification regarding their condition or treatment plan. The principal physiotherapist provides ongoing education, advice, and self-management strategies to empower the individual in managing symptoms and preventing injuries.\nThe subsequent consultation offers continuous support, encouragement, and motivation. The physiotherapist monitors progress, sets goals, and collaborates with the individual for optimal outcomes.\nBy the end of the subsequent consultation, the individual understands their progress, modifications to the treatment plan, and next steps in their rehabilitation. They may receive recommendations for further sessions or referrals to other healthcare professionals if needed.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=3,
                                      name="Practice Physiotherapist Initial Consultation (40mins)",
                                      price=125,
                                      description1="The \"Practice Physiotherapist Initial Consultation (40mins)\" is a thorough 40-minute session for individuals seeking expert assessment and guidance for their physical concerns. The physiotherapist will review medical history, conduct a detailed assessment, and develop a personalized treatment plan.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=4,
                                      name="Practice Physiotherapist Subsequent Consultation (30mins)",
                                      price=105,
                                      description1="The \"Practice Physiotherapist Subsequent Consultation (30mins)\" is a shorter follow-up session designed to track the individual's progress and make necessary adjustments to their treatment plan. During this 30-minute consultation, the physiotherapist will assess how the individual has responded to the initial treatment and gather feedback on any changes in symptoms or functional abilities.\nBased on the assessment and feedback, the physiotherapist will modify the treatment plan as needed to ensure continued progress. They may introduce new exercises or techniques, adjust the intensity or frequency of existing interventions, or provide additional recommendations to address any specific concerns or challenges.\nThe subsequent consultation is an opportunity for the individual to discuss any questions, concerns, or difficulties they may have encountered during their rehabilitation journey. The physiotherapist will provide ongoing education, advice, and support to empower the individual in managing their condition and achieving their goals.\nOverall, the \"Practice Physiotherapist Subsequent Consultation (30mins)\" serves as a valuable check-in session to ensure that the treatment plan remains aligned with the individual's progress and evolving needs, ultimately helping them achieve optimal outcomes and improved physical well-being.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=5,
                                      name="20 Classes of Group Physiotherapy",
                                      price=350,
                                      description1="The \"20 Classes of Group Physiotherapy\" program offers a series of 20 group sessions aimed at improving participants' physical well-being and addressing specific therapeutic needs. Each class provides an opportunity for individuals to engage in guided exercises and therapeutic activities in a supportive group setting.\nDuring these group physiotherapy sessions, a qualified physiotherapist will lead the participants through a variety of exercises and movements tailored to address their specific conditions or goals. The physiotherapist will provide instructions, demonstrations, and guidance to ensure proper technique and safety throughout the class.\nThe exercises and activities conducted during the group sessions may include stretching, strengthening exercises, balance and coordination drills, cardiovascular conditioning, and functional movements. The physiotherapist will design the program in a progressive manner, gradually increasing the intensity and complexity of the exercises as participants build strength, endurance, and mobility.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=6,
                                      name="32 Classes of Group Physiotherapy",
                                      price=550,
                                      description1="The \"32 Classes of Group Physiotherapy\" program offers a series of 20 group sessions aimed at improving participants' physical well-being and addressing specific therapeutic needs. Each class provides an opportunity for individuals to engage in guided exercises and therapeutic activities in a supportive group setting.\nDuring these group physiotherapy sessions, a qualified physiotherapist will lead the participants through a variety of exercises and movements tailored to address their specific conditions or goals. The physiotherapist will provide instructions, demonstrations, and guidance to ensure proper technique and safety throughout the class.\nThe exercises and activities conducted during the group sessions may include stretching, strengthening exercises, balance and coordination drills, cardiovascular conditioning, and functional movements. The physiotherapist will design the program in a progressive manner, gradually increasing the intensity and complexity of the exercises as participants build strength, endurance, and mobility.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

                new_product = Product(product_id=7,
                                      name="58 Classes of Group Physiotherapy",
                                      price=990,
                                      description1="The \"58 Classes of Group Physiotherapy\" program offers a series of 20 group sessions aimed at improving participants' physical well-being and addressing specific therapeutic needs. Each class provides an opportunity for individuals to engage in guided exercises and therapeutic activities in a supportive group setting.\nDuring these group physiotherapy sessions, a qualified physiotherapist will lead the participants through a variety of exercises and movements tailored to address their specific conditions or goals. The physiotherapist will provide instructions, demonstrations, and guidance to ensure proper technique and safety throughout the class.\nThe exercises and activities conducted during the group sessions may include stretching, strengthening exercises, balance and coordination drills, cardiovascular conditioning, and functional movements. The physiotherapist will design the program in a progressive manner, gradually increasing the intensity and complexity of the exercises as participants build strength, endurance, and mobility.",
                                      description2="D2"
                                      )
                db.session.add(new_product)
                db.session.commit()

            except Exception as e:
                traceback.print_exc()
    app.run(debug=True)
