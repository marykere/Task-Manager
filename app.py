from __init__ import create_app, db

# Initialize the app by calling create_app
app = create_app()

# Create the tables (this can be done once in development)
with app.app_context():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
