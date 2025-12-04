# Step 1: Clone project
git clone https://github.com/nikhildewoolkar/biogas-chatbot.git
cd biogas-chatbot

# Step 2: Create Virtual Environment
pip install virtualenvwrapper-win
mkvirtualenv biogasenv
workon biogasenv

# Step 3: Install Dependencies
pip install -r requirements.txt

# Step 4: Create DB in PostgreSQL
# Name DB: 'chatbot'

# Step 5: Run Migrations
python manage.py makemigrations
python manage.py migrate

# Step 6: Create Admin User
python manage.py createsuperuser

# Step 7: Run Application
python manage.py runserver

# Step 8: Run Tests
python manage.py test

Note:- Dont forget to add .env file to the project
