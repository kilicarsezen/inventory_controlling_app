from app import db
from datetime import datetime

class DateTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    # Additional date attributes can be added here
    inventories = db.relationship('Inventory', backref='date', lazy='dynamic')
    material_prices = db.relationship('MaterialPrice', backref='date', lazy='dynamic')
    forecasts = db.relationship('Forecast', backref='date', lazy='dynamic')
    open_orders = db.relationship('OpenOrder', backref='date', lazy='dynamic')
    sales = db.relationship('Sale', backref='date', lazy='dynamic')

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    locations = db.relationship('Location', backref='region', lazy='dynamic')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    storage_locations = db.relationship('StorageLocation', backref='location', lazy='dynamic')

class StorageLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    inventories = db.relationship('Inventory', backref='storage_location', lazy='dynamic')

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_code = db.Column(db.String(50), unique=True, nullable=False)
    sap_code = db.Column(db.String(50), unique=True, nullable=False)
    material_number = db.Column(db.String(50), unique=True, nullable=False)
    jpdm_number = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=True)
    material_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, nullable=False)
    systems = db.relationship('MaterialSystem', backref='material', lazy='dynamic')
    inventories = db.relationship('Inventory', backref='material', lazy='dynamic')
    material_prices = db.relationship('MaterialPrice', backref='material', lazy='dynamic')
    forecasts = db.relationship('Forecast', backref='material', lazy='dynamic')
    open_orders = db.relationship('OpenOrder', backref='material', lazy='dynamic')
    sales = db.relationship('Sale', backref='material', lazy='dynamic')

class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    usage = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Integer, nullable=False)
    # Additional system-specific fields can be added here

    # Establish a relationship to MaterialSystem
    material_systems = db.relationship('MaterialSystem', backref='system', lazy='dynamic')

class MaterialSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)



class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    storage_location_id = db.Column(db.Integer, db.ForeignKey('storage_location.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

class MaterialPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    sourcer = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.DateTime, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    forecasted_for_date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

class OpenOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    open_order_date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity_sold = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))
