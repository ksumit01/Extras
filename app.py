from flask import Flask, render_template, request, redirect, url_for,flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()
# from wtforms import StringField, 
from wtforms import StringField, DecimalField, TextAreaField, BooleanField, IntegerField,SubmitField,SelectField
# from flask_flash import Flash
from wtforms.validators import DataRequired
from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/GA201_Zomato'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.init_app(app)
# migrate = Migrate(app, db)
# manager = Manager(app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

#create model Item

class Menu(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(250))
    price = db.Column(db.Float)
    availability = db.Column(db.Boolean)
    quantity = db.Column(db.Integer, default=0)  # Add the quantity field


def __init__(self, name, description, price, availability, quantity=0):
    self.name = name
    self.description = description
    self.price = price
    self.availability = availability
    self.quantity = quantity
 

class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('menu.item_id'))
    dish = db.relationship('Menu', backref='orders')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="received")  # Status of the order, default is "received"

    def __init__(self, dish_id, status="received"):  # Constructor for creating a new order
        self.dish_id = dish_id
        self.status = status  # Set the status when creating a new order



#create a form class
class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    availability = BooleanField('Availability')
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')



# Create the UpdateForm class
class UpdateForm(FlaskForm):
    item_id = IntegerField('Enter Item ID you want to update', validators=[DataRequired()])
    # Add additional fields for the details you want to update (e.g., name, description, price, availability)
    name = StringField('New Item Name')
    description = TextAreaField('New Description')
    price = DecimalField('New Price')
    availability = BooleanField('New Availability')
    submit = SubmitField('Update')


# Create the DeleteForm class
class DeleteForm(FlaskForm):
    
    item_id = IntegerField('Enter Item ID you want to Delete', validators=[DataRequired()])
    submit = SubmitField('Delete')

#Order Form
# from wtforms import SelectField, IntegerField, SubmitField
# from wtforms.validators import DataRequired

class OrderForm(FlaskForm):
    # Create a SelectField with both item_id and item_name as choices
    menu_item = SelectField('Menu Item', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Place Order')



@app.route('/')
def home():
  return render_template('index.html')

@app.route('/user/<name>')
def user(name):
  return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

app.errorhandler(500)
def page_not_found(e):
  return render_template('500.html'), 500


@app.route('/menu', methods=['GET', 'POST'])
def addItem():
    form = ItemForm()
    item_inventory = Menu.query.order_by(Menu.item_id).all()
    # print(item_inventory)
    if form.validate_on_submit():
        # Retrieve data from the form
        name = form.name.data
        description = form.description.data
        price = form.price.data
        availability = form.availability.data
        quantity = form.quantity.data  # Get the quantity from the form

        # Check if an item with the same name already exists
        existing_item = Menu.query.filter_by(name=name).first()

        if existing_item:
            # If the item with the same name exists, update its quantity
            existing_item.quantity += quantity
            db.session.commit()
            flash("Item quantity updated successfully", 'success')
        else:
            # If the item with the same name doesn't exist, create a new item
            new_item = Menu(name=name, description=description, price=price, availability=availability, quantity=quantity)
            db.session.add(new_item)
            db.session.commit()
            flash("Item added successfully", 'success')

        # Clear the form input fields
        form.name.data = ''
        form.description.data = ''
        form.price.data = ''
        form.availability.data = ''
        form.quantity.data = ''  # Reset the quantity field

    return render_template('menuItem.html', form=form, item_inventory=item_inventory)




@app.route('/update_item', methods=['GET', 'POST'])
def updateItem():
    form = UpdateForm()
    flash_message = None

    if form.validate_on_submit():
        item_id = form.item_id.data

        # Find the menu item based on the menu_id
        item_to_update = Menu.query.get(item_id)

        if item_to_update:
            # Update the menu item details with the values from the form fields
            if form.name.data:
                item_to_update.name = form.name.data
            if form.description.data:
                item_to_update.description = form.description.data
            if form.price.data:
                item_to_update.price = form.price.data
            if form.availability.data is not None:
                item_to_update.availability = form.availability.data

            db.session.commit()  # Commit the changes to the database

            flash_message = f'Menu item with ID {item_id} updated successfully'
            
        else:
            flash_message = f'Menu item with ID {item_id} not found'

        # Clear the form fields
        form.item_id.data = None
        form.name.data = None
        form.description.data = None
        form.price.data = None
        form.availability.data = False

    return render_template('updateItem.html', form=form, flash_message=flash_message)




@app.route('/delete_item', methods=['GET', 'POST'])
def deleteItem():
    form = DeleteForm()
    flash_message = None

    if form.validate_on_submit():
        item_id = form.item_id.data

        # Find the menu item based on the menu_id
        item_to_delete = Menu.query.get(item_id)

        if item_to_delete:
            # Delete the menu item from the database
            db.session.delete(item_to_delete)
            db.session.commit()  # Commit the changes to the database

            flash_message = f'Menu item with ID {item_id} deleted successfully'
            
        else:
            flash_message = f'Menu item with ID {item_id} not found'
        form.item_id.data = None
        
    return render_template('deleteItem.html', form=form, flash_message=flash_message)

@app.route('/view_menu')
def viewMenu():
    # Retrieve all menu items from the database
    menu_items = Menu.query.all()
    return render_template('viewMenu.html', menu_items=menu_items)



@app.route('/order_confirmation')
def order_confirmation():
    return 'Your order has been placed successfully!'


# @app.route('/place_order', methods=['GET', 'POST'])
@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    form = OrderForm()

    # Populate menu_item choices with (item_id, item_name) tuples
    menu_items = Menu.query.all()
    choices = [(item.item_id, item.name) for item in menu_items]
    form.menu_item.choices = choices

    if form.validate_on_submit():
        dish_id = form.menu_item.data  # dish_id will now contain the selected item_id
        quantity = form.quantity.data

        # Create a new order and save it to the database
        order = Orders(dish_id=dish_id, quantity=quantity)
        db.session.add(order)
        db.session.commit()

        return redirect(url_for('order_confirmation'))

    return render_template('placeOrder.html', form=form)



 






if __name__ == '__main__':
  app.run(debug=True)
