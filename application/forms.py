from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired


class IngredientsForm(FlaskForm):
     ingredient = StringField("Ingredient", validators=[DataRequired()])
     amount = StringField("Amount", validators=[DataRequired()])
     unit = StringField("Unit", validators=[DataRequired()])

class RecipeForm(FlaskForm):
     name = StringField("Recipe name", validators=[DataRequired()])
     ingredients = FieldList(FormField(IngredientsForm), min_entries=1)
     add_ingredient = SubmitField("Add ingredient")
     instructions = StringField("instructions", validators=[DataRequired()])
     time = IntegerField("Time")
     submit =  SubmitField("Submit")

class SearchForm(FlaskForm):
     options = SelectField("Search by", choices=[("name", "Name"), ("ingredient", "Ingredient"), ("time", "Time(min)")])
     search = StringField("search", validators=[DataRequired()])
     submit =  SubmitField("Search")