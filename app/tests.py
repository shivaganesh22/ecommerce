from django.test import TestCase
import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyB9lHrkaiaYig7U7P03ErTgfKkgvLWP3qE",
  "authDomain": "ecommerce-94595.firebaseapp.com",
  "projectId": "ecommerce-94595",
  "storageBucket": "ecommerce-94595.appspot.com",
  "databaseURL":"https://ecommerce-94595-default-rtdb.firebaseio.com",
  "messagingSenderId": "272756702097",
  "appId": "1:272756702097:web:bc74ad885341da21a57830",
  "measurementId": "G-H3CY3C8TFH"
}
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
# auth.create_user_with_email_and_password("21eg112b26@anurag.edu.in","Shiva123@")
auth.sign_in_with_email_and_password("21eg112b26@anurag.edu.in","Shiva123@")