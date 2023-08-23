from application import app
from flask import render_template, flash, request, url_for, redirect, session
from application import db
from .forms import RecipeForm, SearchForm, IngredientsForm
from datetime import datetime
from bson import ObjectId
from wtforms.fields import Label
import bcrypt



@app.route("/")
def home():
    recipes = []
    for recipe in db.recipes.find().sort("date_created", -1):
        recipe["_id"] = str(recipe["_id"])
        recipe["date_created"] = recipe["date_created"].strftime("%d.%m.%Y")
        recipes.append(recipe)
    return render_template("home.html", recipes = recipes)

#User handling
@app.route("/logged_in", methods=["POST", "GET"])
def logged_in():
    users = db.users
    login_user = users.find_one({"name" : request.form['username']})

    if login_user:
        password = request.form['password'].encode("utf-8")
        if  bcrypt.checkpw(password, login_user["password"]):
            session["username"] = request.form["username"]
            return redirect(url_for("view_recipes"))
        
    flash("Username and password combination is wrong", "danger")
    return redirect(url_for("login"))
    

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        users = db.users
        existing_user = users.find_one({"name" : request.form["username"]})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode("utf-8"), bcrypt.gensalt())
            users.insert_one({"name": request.form['username'], "password" : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for("home"))
        
        flash(request.form['username'] + " username is already exist", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


#Recipe handling
@app.route("/view_recipes")
def view_recipes():
    if "username" in session:
        recipes = []
        for recipe in db.recipes.find({"added_by": session["username"]}).sort("date_created", -1):
            recipe["_id"] = str(recipe["_id"])
            recipe["date_created"] = recipe["date_created"].strftime("%d.%m.%Y")
            recipes.append(recipe)
        return render_template("view_recipes.html", recipes = recipes)
    
    return redirect(url_for("home"))


@app.route("/add_recipe", methods =["POST", "GET"])
def add_recipe():
    if "username" in session:
        if request.method == "POST":
            form = RecipeForm()
            if form.add_ingredient.data:
                form.ingredients.append_entry(None)

            elif form.validate_on_submit():
                name = form.name.data
                ingredients = form.ingredients.data
                instructions = form.instructions.data
                time = form.time.data

                db.recipes.insert_one({
                    "name": name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "time": time,
                    "date_created": datetime.utcnow(),
                    "added_by" : session["username"]
                })
                flash("Recipe succesfully added", "info")
                return redirect("/")      
            return render_template("add_recipe.html", form = form, title="Add Recipe") 
    
        else:
            form = RecipeForm()
        return render_template("add_recipe.html", form = form, title="Add Recipe")
    
    return redirect(url_for("home"))


@app.route("/search_recipe", methods=["GET", "POST"])
def search_recipe():
    recipes = []
    if request.method == "POST":
        form = SearchForm()
        option = form.options.data
        search = form.search.data
        print(option)
        print(search)
        if option == "name":
            for recipe in db.recipes.find().sort("date_created", -1):
                if recipe["name"].lower() == search.lower():
                    recipe["date_created"] = recipe["date_created"].strftime("%d.%m.%Y")
                    recipes.append(recipe)

        elif option == "ingredient":
            for recipe in db.recipes.find().sort("date_created", -1):
                for ingredient in recipe["ingredients"]:
                    if ingredient["ingredient"].lower() == search.lower():
                        recipe["date_created"] = recipe["date_created"].strftime("%d.%m.%Y")
                        recipes.append(recipe)   

        elif option == "time":
            try:
                search = int(search)
            except ValueError:
                flash("Time input must be number", "danger")
                return redirect(url_for("search_recipe"))
        
            for recipe in db.recipes.find().sort("date_created", -1):
                if recipe["time"] == int(search):
                    recipe["date_created"] = recipe["date_created"].strftime("%d.%m.%Y")
                    recipes.append(recipe)

        if len(recipes) == 0:
            flash("No recipes Found", "danger")
            return redirect(url_for("search_recipe"))
        return render_template("home.html", recipes = recipes, title="Search Recipe")
    
    else:
        form = SearchForm()
    return render_template("search_recipe.html", form = form, title="Search Recipe")


@app.route("/delete_recipe/<id>")
def delete_recipe(id):
    db.recipes.find_one_and_delete({"_id": ObjectId(id)})
    flash("Recipe deleted", "info")
    return redirect("/")


@app.route("/update_recipe/<id>", methods = ["POST", "GET"])
def update_recipe(id):
    if request.method == "POST":
        form = RecipeForm()
        if form.add_ingredient.data:
            form.ingredients.append_entry(None)
        elif form.validate_on_submit():
            name = form.name.data
            ingredients = form.ingredients.data
            instructions = form.instructions.data
            time = form.time.data
            db.recipes.find_one_and_update({"_id": ObjectId(id)}, {"$set": {
                "name": name,
                "ingredients": ingredients,
                "instructions": instructions,
                "time": time,
                "date_created": datetime.utcnow()                                                         
            }})
            flash("Recipe succesfully updated", "info")
            return redirect("/")
        return render_template("add_recipe.html", form = form, title="Update Recipe")   
    else:
        recipe = db.recipes.find_one({"_id": ObjectId(id)})
        form = RecipeForm(data=recipe)
        return render_template("add_recipe.html", form = form, title="Update Recipe")
