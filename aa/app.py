from flask import Flask, render_template_string, request, redirect, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)

# Use environment variables for configuration
app.secret_key = os.environ.get('SECRET_KEY', "your_secret_key_please_change_this_for_security")

# MongoDB connection
mongodb_uri = os.environ.get('MONGODB_URI', "mongodb+srv://varma:varma1225@varma.f5zdh.mongodb.net/?retryWrites=true&w=majority&appName=varma")
client = MongoClient(mongodb_uri)
db = client["hospital_bot"]
doctors_collection = db["doctor"]
appointments_collection = db["appointments"]
prescriptions_collection = db["prescriptions"]  # New collection for prescriptions

# --- Helper function to generate time slots ---
def generate_time_slots():
    slots = []
    
    # Morning slots: 7 AM to 12 PM (exclusive of 12 PM start)
    start_time_morning = datetime.strptime("07:00", "%H:%M")
    end_time_morning = datetime.strptime("12:00", "%H:%M") # Slot up to 11:50
    
    current_time = start_time_morning
    while current_time < end_time_morning:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=10)
        
    # Afternoon/Evening slots: 2 PM to 9 PM (exclusive of 9 PM start)
    start_time_afternoon = datetime.strptime("14:00", "%H:%M")
    end_time_afternoon = datetime.strptime("21:00", "%H:%M") # Slot up to 20:50
    
    current_time = start_time_afternoon
    while current_time < end_time_afternoon:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=10)
        
    return slots

# --- Helper function to get booked time slots for a specific date ---
def get_booked_slots_for_date(date, exclude_appointment_id=None):
    """Get list of booked time slots for a specific date"""
    query = {"date": date}
    if exclude_appointment_id:
        query["appointment_id"] = {"$ne": exclude_appointment_id}
    
    booked_appointments = appointments_collection.find(query)
    booked_slots = [appointment["time"] for appointment in booked_appointments]
    return booked_slots

# --- Existing Templates (included for completeness) ---
home_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aastha Homoeo Clinic</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
</head>
<body class="font-sans bg-white">
    <nav class="bg-white shadow-lg fixed w-full top-0 z-50">
        <div class="max-w-6xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-3">
                    <div class="bg-teal-600 text-white p-3 rounded-full">
                        <i class="ri-heart-pulse-line text-xl"></i>
                    </div>
                    <span class="text-xl font-bold text-gray-800">Aastha Homoeo Clinic</span>
                </div>
                <div class="hidden md:flex space-x-8 text-gray-700 font-medium" id="navbar-menu-desktop">
                    <a href="#home" class="hover:text-teal-600 transition-colors">Home</a>
                    <a href="#doctor" class="hover:text-teal-600 transition-colors">Meet Doctor</a>
                    <a href="#contact" class="hover:text-teal-600 transition-colors">Contact</a>
                    <a href="/login" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">Doctor Login</a>
                </div>
                <div class="md:hidden">
                    <button id="mobile-menu-button" class="text-gray-700">
                        <i class="ri-menu-line text-2xl"></i>
                    </button>
                </div>
            </div>
        </div>
        <div id="mobile-menu" class="md:hidden hidden bg-white py-2 shadow-lg">
            <a href="#home" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Home</a>
            <a href="#doctor" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Meet Doctor</a>
            <a href="#contact" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Contact</a>
            <a href="/login" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Doctor Login</a>
        </div>
    </nav>

    <section id="home" class="pt-20 min-h-screen bg-gradient-to-br from-teal-600 to-teal-300 text-white flex items-center">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <h1 class="text-4xl md:text-6xl font-bold mb-6">
                Welcome to Aastha Homoeo Clinic
            </h1>
            <p class="text-xl mb-8 max-w-3xl mx-auto">
                Experience holistic homeopathic treatment tailored to your unique needs, guided by expertise and empathy. Our approach combines traditional healing wisdom with modern understanding to restore your natural balance.
            </p>
            <div class="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-4">
                <a href="#doctor" class="w-full md:w-auto bg-white text-teal-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block">
                    Meet the Doctor
                </a>
                <a href="#contact" class="w-full md:w-auto border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-teal-600 transition-colors inline-block">
                    Contact Us
                </a>
            </div>
        </div>
    </section>
    <section id="doctor" class="py-20 bg-white">
        <div class="max-w-6xl mx-auto px-4">
            <div class="bg-white rounded-xl shadow-lg p-8 max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">Dr. Priya Sharma</h2>
                    <p class="text-lg text-gray-600">BHMS, MD (Homeopathy), 15+ Years Experience</p>
                </div>
                
                <div class="grid md:grid-cols-3 gap-6 mb-8">
                    <div class="text-center">
                        <div class="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-3">
                            <i class="ri-mental-health-line text-teal-600 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-gray-800">Psychiatry & Mental Health</h3>
                    </div>
                    <div class="text-center">
                        <div class="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-3">
                            <i class="ri-graduation-cap-line text-teal-600 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-gray-800">Learning Disabilities</h3>
                    </div>
                    <div class="text-center">
                        <div class="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-3">
                            <i class="ri-heart-line text-teal-600 text-2xl"></i>
                        </div>
                        <h3 class="font-semibold text-gray-800">Mood Disorders</h3>
                    </div>
                </div>
                
                <div class="grid md:grid-cols-3 gap-6">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                            <i class="ri-phone-line text-teal-600 text-xl"></i>
                        </div>
                        <div>
                            <p class="font-medium text-gray-800">Phone</p>
                            <p class="text-gray-600">+91 98765 43210</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                            <i class="ri-mail-line text-teal-600 text-xl"></i>
                        </div>
                        <div>
                            <p class="font-medium text-gray-800">Email</p>
                            <p class="text-gray-600">dr.priya@aasthahomoeo.com</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                            <i class="ri-map-pin-line text-teal-600 text-xl"></i>
                        </div>
                        <div>
                            <p class="font-medium text-gray-800">Location</p>
                            <p class="text-gray-600">Hyderabad, India</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="py-20 bg-gray-50">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">What Our Patients Say</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mr-3">
                            <i class="ri-user-line text-teal-600"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">Rajesh Kumar</h3>
                            <div class="flex text-yellow-400">
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                            </div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"Dr. Sharma's homeopathic treatment completely transformed my chronic anxiety. Her compassionate approach and personalized care made all the difference in my healing journey."</p>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mr-3">
                            <i class="ri-user-line text-teal-600"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">Meera Patel</h3>
                            <div class="flex text-yellow-400">
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                            </div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"My daughter's learning difficulties improved significantly under Dr. Sharma's care. The holistic approach addressed not just symptoms but the root cause of her challenges."</p>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mr-3">
                            <i class="ri-user-line text-teal-600"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">Arjun Singh</h3>
                            <div class="flex text-yellow-400">
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                                <i class="ri-star-fill"></i>
                            </div>
                        </div>
                    </div>
                    <p class="text-gray-600 italic">"Professional, knowledgeable, and genuinely caring. Dr. Sharma's treatment helped me overcome depression naturally without harsh side effects. Highly recommended!"</p>
                </div>
            </div>
        </div>
    </section>

    <section id="contact" class="py-20 bg-white">
        <div class="max-w-6xl mx-auto px-4">
            <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">Contact Us</h2>
            <div class="grid md:grid-cols-2 gap-12">
                <div class="bg-white rounded-lg shadow-md p-8">
                    <h3 class="text-2xl font-semibold text-gray-800 mb-6">Get in Touch</h3>
                    <div class="space-y-6">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-map-pin-line text-teal-600 text-xl"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">Address</p>
                                <p class="text-gray-600">123 Main Street, Hyderabad, India</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-mail-line text-teal-600 text-xl"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">Email</p>
                                <p class="text-gray-600">info@aasthahomoeo.com</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-phone-line text-teal-600 text-xl"></i>
                            </div>
                            <div>
                                <p class="font-medium text-gray-800">Phone</p>
                                <p class="text-gray-600">+91 12345 67890</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-8">
                        <h4 class="font-semibold text-gray-800 mb-4">Follow Us</h4>
                        <div class="flex space-x-4">
                            <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-facebook-fill text-teal-600"></i>
                            </div>
                            <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-twitter-fill text-teal-600"></i>
                            </div>
                            <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-instagram-fill text-teal-600"></i>
                            </div>
                            <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                                <i class="ri-linkedin-fill text-teal-600"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-8">
                    <h3 class="text-2xl font-semibold text-gray-800 mb-6">Send Message</h3>
                    <form class="space-y-4">
                        <input type="text" placeholder="Your Name" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
                        <input type="email" placeholder="Your Email" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
                        <input type="tel" placeholder="Your Phone" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
                        <textarea placeholder="Your Message" rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"></textarea>
                        <button type="submit" class="w-full bg-teal-600 text-white py-3 rounded-lg font-semibold hover:bg-teal-700 transition-colors">
                            Send Message
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>

    <footer class="bg-gray-800 text-white py-12">
        <div class="max-w-6xl mx-auto px-4">
            <div class="grid md:grid-cols-3 gap-8">
                <div>
                    <div class="flex items-center space-x-3 mb-4">
                        <div class="bg-teal-600 text-white p-2 rounded-full">
                            <i class="ri-heart-pulse-line"></i>
                        </div>
                        <span class="text-xl font-bold">Aastha Homoeo Clinic</span>
                    </div>
                    <p class="text-gray-300 mb-4">
                        Providing compassionate homeopathic care with personalized treatment approaches for holistic healing and wellness.
                    </p>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold mb-4">Quick Links</h4>
                    <ul class="space-y-2">
                        <li><a href="#home" class="text-gray-300 hover:text-white transition-colors">Home</a></li>
                        <li><a href="#doctor" class="text-gray-300 hover:text-white transition-colors">Meet a doctor</a></li>
                        <li><a href="#contact" class="text-gray-300 hover:text-white transition-colors">contact</a></li>
                        
                    </ul>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold mb-4">Connect With Us</h4>
                    <div class="flex space-x-4 mb-4">
                        <div class="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                            <i class="ri-facebook-fill text-white"></i>
                        </div>
                        <div class="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                            <i class="ri-twitter-fill text-white"></i>
                        </div>
                        <div class="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                            <i class="ri-instagram-fill text-white"></i>
                        </div>
                        <div class="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                            <i class="ri-linkedin-fill text-white"></i>
                        </div>
                    </div>
                    <p class="text-gray-300 text-sm">© 2024 Aastha Homoeo Clinic. All rights reserved.</p>
                </div>
            </div>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const mobileMenuButton = document.getElementById('mobile-menu-button');
            const mobileMenu = document.getElementById('mobile-menu');

            if (mobileMenuButton && mobileMenu) { // Ensure elements exist
                mobileMenuButton.addEventListener('click', function() {
                    mobileMenu.classList.toggle('hidden');
                });

                // Close the mobile menu when a link is clicked (for smoother navigation)
                mobileMenu.querySelectorAll('a').forEach(link => {
                    link.addEventListener('click', () => {
                        mobileMenu.classList.add('hidden');
                    });
                });
            }
        });
    </script>
</body>
</html>
"""

# Reusable Appointment Form Template (for both Add and Edit)
appointment_form_template = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100">
<head>
  <meta charset="UTF-8">
  <title>{{ 'Add New' if mode == 'add' else 'Edit' }} Appointment - Aastha Homoeo Clinic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
</head>
<body>
  <nav class="bg-teal-600 p-4 text-white flex justify-between items-center">
    <h1 class="text-xl font-bold">Aastha Homoeo Clinic - {{ 'Add New' if mode == 'add' else 'Edit' }} Appointment</h1>
    <div>
      <a href="/dashboard" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Dashboard</a>
      <a href="{{ url_for('logout') }}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100">Logout</a>
    </div>
  </nav>

  <div class="p-6">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="mb-4 text-sm p-3 rounded bg-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-100 text-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-800">
          {{ message }}
        </div>
      {% endfor %}
    {% endwith %}

    <div class="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
      <h2 class="text-2xl font-semibold mb-6">{{ 'Add New' if mode == 'add' else 'Edit' }} Appointment</h2>
      
      <form method="POST" action="{{ '/add_appointment' if mode == 'add' else '/edit_appointment/' + appointment_data.appointment_id }}" class="space-y-4">
        
        {# Hidden field for appointment_id when editing, to ensure it's passed with form data #}
        {% if mode == 'edit' %}
        <input type="hidden" name="appointment_id" value="{{ appointment_data.appointment_id }}">
        {% endif %}

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="name" class="block text-gray-700 font-medium mb-2">Patient Name *</label>
            <input type="text" id="name" name="name" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ appointment_data.name if appointment_data else '' }}">
          </div>
          
          <div>
            <label for="phone" class="block text-gray-700 font-medium mb-2">Phone Number *</label>
            <input type="tel" id="phone" name="phone" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ appointment_data.phone if appointment_data else '' }}">
          </div>
          
          <div>
            <label for="email" class="block text-gray-700 font-medium mb-2">Email</label>
            <input type="email" id="email" name="email"
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ appointment_data.email if appointment_data else '' }}">
          </div>
          
          <div>
            <label for="date" class="block text-gray-700 font-medium mb-2">Appointment Date *</label>
            <input type="date" id="date" name="date" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ appointment_data.date if appointment_data else '' }}"
                   min="{{ today_date }}"> {# Added min attribute here #}
          </div>
          
          <div>
            <label for="time" class="block text-gray-700 font-medium mb-2">Appointment Time *</label>
            <select id="time" name="time" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
                <option value="" disabled {% if not appointment_data or not appointment_data.time %}selected{% endif %}>Select a time slot</option>
                {% for slot in time_slots %}
                    <option value="{{ slot }}" 
                            {% if appointment_data and appointment_data.time == slot %}selected{% endif %}
                            class="{% if slot in booked_slots %}text-green-600 font-semibold{% else %}text-black{% endif %}">
                        {{ slot }}{% if slot in booked_slots %} (Booked){% endif %}
                    </option>
                    {% if slot == "11:50" %}
                        <option value="" disabled class="text-red-500 font-bold">--- Lunch Break (12:00 - 14:00) ---</option>
                    {% endif %}
                {% endfor %}
            </select>
            <p class="text-sm text-gray-600 mt-1">
                <span class="text-green-600 font-semibold">● Green slots are booked</span> | 
                <span class="text-black">● Black slots are available</span>
            </p>
          </div>
        </div>
        
        <div>
          <label for="address" class="block text-gray-700 font-medium mb-2">Address</label>
          <textarea id="address" name="address" rows="2"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">{{ appointment_data.address if appointment_data else '' }}</textarea>
        </div>
        
        <div>
          <label for="symptoms" class="block text-gray-700 font-medium mb-2">Symptoms/Reason *</label>
          <textarea id="symptoms" name="symptoms" rows="3" required
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">{{ appointment_data.symptoms if appointment_data else '' }}</textarea>
        </div>
        
        <div class="flex space-x-4">
          <button type="submit" class="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            {{ 'Create Appointment' if mode == 'add' else 'Save Changes' }}
          </button>
          <a href="/dashboard" class="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors">
            Cancel
          </a>
        </div>
      </form>
    </div>
  </div>
  
  <script>
    // Function to update time slots based on selected date
    function updateTimeSlots() {
      const dateInput = document.getElementById('date');
      const timeSelect = document.getElementById('time');
      const selectedDate = dateInput.value;
      
      if (selectedDate) {
        // Make AJAX request to get booked slots for the selected date
        fetch(`/get_booked_slots/${selectedDate}`)
          .then(response => response.json())
          .then(data => {
            const bookedSlots = data.booked_slots;
            
            // Update the time slot options
            Array.from(timeSelect.options).forEach(option => {
              if (option.value && option.value !== '') {
                const slotTime = option.value;
                if (bookedSlots.includes(slotTime)) {
                  option.className = 'text-green-600 font-semibold';
                  option.textContent = slotTime + ' (Booked)';
                } else {
                  option.className = 'text-black';
                  option.textContent = slotTime;
                }
              }
            });
          })
          .catch(error => {
            console.error('Error fetching booked slots:', error);
          });
      }
    }
    
    // Add event listener to date input
    document.addEventListener('DOMContentLoaded', function() {
      const dateInput = document.getElementById('date');
      if (dateInput) {
        dateInput.addEventListener('change', updateTimeSlots);
      }
    });
  </script>
</body>
</html>
"""

# Prescription Form Template
prescription_form_template = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100">
<head>
  <meta charset="UTF-8">
  <title>Add Prescription - Aastha Homoeo Clinic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
</head>
<body>
  <nav class="bg-teal-600 p-4 text-white flex justify-between items-center">
    <h1 class="text-xl font-bold">Aastha Homoeo Clinic - Add Prescription</h1>
    <div>
      <a href="/dashboard" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Dashboard</a>
      <a href="/prescriptions" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">View Prescriptions</a>
      <a href="{{ url_for('logout') }}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100">Logout</a>
    </div>
  </nav>

  <div class="p-6">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="mb-4 text-sm p-3 rounded bg-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-100 text-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-800">
          {{ message }}
        </div>
      {% endfor %}
    {% endwith %}

    <div class="bg-white rounded-lg shadow-md p-6 max-w-4xl mx-auto">
      <h2 class="text-2xl font-semibold mb-6">Add New Prescription</h2>
      
      <form method="POST" action="/add_prescription" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="patient_name" class="block text-gray-700 font-medium mb-2">Patient Name *</label>
            <input type="text" id="patient_name" name="patient_name" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ prescription_data.patient_name if prescription_data else '' }}">
          </div>
          
          <div>
            <label for="patient_phone" class="block text-gray-700 font-medium mb-2">Patient Phone *</label>
            <input type="tel" id="patient_phone" name="patient_phone" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ prescription_data.patient_phone if prescription_data else '' }}">
          </div>
          
          <div>
            <label for="prescription_date" class="block text-gray-700 font-medium mb-2">Prescription Date *</label>
            <input type="date" id="prescription_date" name="prescription_date" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ prescription_data.prescription_date if prescription_data else today_date }}">
          </div>
          
          <div>
            <label for="diagnosis" class="block text-gray-700 font-medium mb-2">Diagnosis *</label>
            <input type="text" id="diagnosis" name="diagnosis" required
                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                   value="{{ prescription_data.diagnosis if prescription_data else '' }}">
          </div>
        </div>
        
        <div>
          <label for="medicines" class="block text-gray-700 font-medium mb-2">Medicines *</label>
          <div id="medicines-container" class="space-y-4">
            <div class="medicine-entry border border-gray-200 rounded-lg p-4">
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label class="block text-gray-700 text-sm font-medium mb-1">Medicine Name</label>
                  <input type="text" name="medicine_names[]" required
                         class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                         placeholder="e.g., Arnica Montana">
                </div>
                <div>
                  <label class="block text-gray-700 text-sm font-medium mb-1">Potency</label>
                  <input type="text" name="potencies[]" required
                         class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                         placeholder="e.g., 30C">
                </div>
                <div>
                  <label class="block text-gray-700 text-sm font-medium mb-1">Dosage</label>
                  <input type="text" name="dosages[]" required
                         class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                         placeholder="e.g., 3 times daily">
                </div>
                <div>
                  <label class="block text-gray-700 text-sm font-medium mb-1">Duration</label>
                  <input type="text" name="durations[]" required
                         class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                         placeholder="e.g., 7 days">
                </div>
              </div>
            </div>
          </div>
          <button type="button" id="add-medicine" class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
            <i class="ri-add-line mr-1"></i>Add Another Medicine
          </button>
        </div>
        
        <div>
          <label for="instructions" class="block text-gray-700 font-medium mb-2">Special Instructions</label>
          <textarea id="instructions" name="instructions" rows="3"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                    placeholder="Any special instructions for the patient...">{{ prescription_data.instructions if prescription_data else '' }}</textarea>
        </div>
        
        <div>
          <label for="notes" class="block text-gray-700 font-medium mb-2">Doctor's Notes</label>
          <textarea id="notes" name="notes" rows="3"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
                    placeholder="Additional notes...">{{ prescription_data.notes if prescription_data else '' }}</textarea>
        </div>
        
        <div class="flex space-x-4">
          <button type="submit" class="bg-teal-600 text-white px-6 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            Save Prescription
          </button>
          <a href="/prescriptions" class="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors">
            Cancel
          </a>
        </div>
      </form>
    </div>
  </div>
  
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const addMedicineBtn = document.getElementById('add-medicine');
      const medicinesContainer = document.getElementById('medicines-container');
      
      addMedicineBtn.addEventListener('click', function() {
        const medicineEntry = document.createElement('div');
        medicineEntry.className = 'medicine-entry border border-gray-200 rounded-lg p-4';
        medicineEntry.innerHTML = `
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-gray-700 text-sm font-medium mb-1">Medicine Name</label>
              <input type="text" name="medicine_names[]" required
                     class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                     placeholder="e.g., Arnica Montana">
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-medium mb-1">Potency</label>
              <input type="text" name="potencies[]" required
                     class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                     placeholder="e.g., 30C">
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-medium mb-1">Dosage</label>
              <input type="text" name="dosages[]" required
                     class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                     placeholder="e.g., 3 times daily">
            </div>
            <div class="flex items-end">
              <div class="flex-1">
                <label class="block text-gray-700 text-sm font-medium mb-1">Duration</label>
                <input type="text" name="durations[]" required
                       class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-teal-500"
                       placeholder="e.g., 7 days">
              </div>
              <button type="button" class="ml-2 bg-red-500 text-white px-3 py-2 rounded hover:bg-red-600 transition-colors remove-medicine">
                <i class="ri-delete-bin-line"></i>
              </button>
            </div>
          </div>
        `;
        
        medicinesContainer.appendChild(medicineEntry);
        
        // Add remove functionality to the new entry
        const removeBtn = medicineEntry.querySelector('.remove-medicine');
        removeBtn.addEventListener('click', function() {
          medicineEntry.remove();
        });
      });
      
      // Add remove functionality to the first entry
      const firstRemoveBtn = medicinesContainer.querySelector('.remove-medicine');
      if (firstRemoveBtn) {
        firstRemoveBtn.addEventListener('click', function() {
          medicinesContainer.querySelector('.medicine-entry').remove();
        });
      }
    });
  </script>
</body>
</html>
"""

# Prescription History Template
prescription_history_template = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100">
<head>
  <meta charset="UTF-8">
  <title>Prescription History - Aastha Homoeo Clinic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
</head>
<body>
  <nav class="bg-teal-600 p-4 text-white flex justify-between items-center">
    <h1 class="text-xl font-bold">Aastha Homoeo Clinic - Prescription History</h1>
    <div>
      <a href="/dashboard" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Dashboard</a>
      <a href="/add_prescription" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Add Prescription</a>
      <a href="{{ url_for('logout') }}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100">Logout</a>
    </div>
  </nav>

  <div class="p-6">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="mb-4 text-sm p-3 rounded bg-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-100 text-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-800">
          {{ message }}
        </div>
      {% endfor %}
    {% endwith %}

    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-semibold">
          {% if patient_phone %}
            {% if patient_name %}
              Prescriptions for Patient: {{ patient_name }} ({{ patient_phone }})
            {% else %}
              Prescriptions for Patient: {{ patient_phone }}
            {% endif %}
          {% else %}
            Prescription History
          {% endif %}
        </h2>
        <div class="flex space-x-2">
          {% if patient_phone %}
            <a href="/prescriptions" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
              <i class="ri-list-check mr-1"></i>View All Prescriptions
            </a>
          {% endif %}
          <a href="/add_prescription{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            <i class="ri-add-line mr-1"></i>Add New Prescription
          </a>
        </div>
      </div>

      <form method="GET" action="/prescriptions" class="mb-6 flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-4">
        {% if patient_phone %}
          <input type="hidden" name="patient_phone" value="{{ patient_phone }}">
        {% endif %}
        <input type="text" name="search_query" placeholder="Search by Patient Name or Phone..." 
               class="flex-grow w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
               value="{{ search_query if search_query else '' }}">
        <button type="submit" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
          <i class="ri-search-line mr-1"></i>Search
        </button>
        {% if search_query %}
          <a href="/prescriptions{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors">Clear Search</a>
        {% endif %}

        <div class="flex items-center space-x-2 w-full md:w-auto">
          <label for="sort_by" class="text-gray-700">Sort by:</label>
          <select id="sort_by" name="sort_by" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
            <option value="">Default (Latest First)</option>
            <option value="patient_name_asc" {% if sort_by == 'patient_name_asc' %}selected{% endif %}>Patient Name (A-Z)</option>
            <option value="patient_name_desc" {% if sort_by == 'patient_name_desc' %}selected{% endif %}>Patient Name (Z-A)</option>
            <option value="date_asc" {% if sort_by == 'date_asc' %}selected{% endif %}>Date (Oldest First)</option>
            <option value="date_desc" {% if sort_by == 'date_desc' %}selected{% endif %}>Date (Newest First)</option>
          </select>
          <button type="submit" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            Sort
          </button>
        </div>
      </form>

      <div class="space-y-6">
        {% for prescription in prescriptions %}
        <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-xl font-semibold text-gray-800">{{ prescription.patient_name }}</h3>
              <p class="text-gray-600">{{ prescription.patient_phone }}</p>
              <p class="text-sm text-gray-500">Prescription Date: {{ prescription.prescription_date }}</p>
              <p class="text-sm text-gray-500">Prescription ID: {{ prescription.prescription_id }}</p>
            </div>
            <div class="text-right">
              <span class="bg-teal-100 text-teal-800 px-3 py-1 rounded-full text-sm font-medium">
                {{ prescription.created_at_str }}
              </span>
            </div>
          </div>
          
          <div class="grid md:grid-cols-2 gap-6 mb-4">
            <div>
              <h4 class="font-semibold text-gray-700 mb-2">Diagnosis</h4>
              <p class="text-gray-600">{{ prescription.diagnosis }}</p>
            </div>
            <div>
              <h4 class="font-semibold text-gray-700 mb-2">Special Instructions</h4>
              <p class="text-gray-600">{{ prescription.instructions or 'None' }}</p>
            </div>
          </div>
          
          <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-3">Medicines</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              {% for medicine in prescription.medicines %}
              <div class="border-b border-gray-200 pb-3 mb-3 last:border-b-0 last:pb-0 last:mb-0">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span class="font-medium text-gray-700">Medicine:</span>
                    <p class="text-gray-600">{{ medicine.name }}</p>
                  </div>
                  <div>
                    <span class="font-medium text-gray-700">Potency:</span>
                    <p class="text-gray-600">{{ medicine.potency }}</p>
                  </div>
                  <div>
                    <span class="font-medium text-gray-700">Dosage:</span>
                    <p class="text-gray-600">{{ medicine.dosage }}</p>
                  </div>
                  <div>
                    <span class="font-medium text-gray-700">Duration:</span>
                    <p class="text-gray-600">{{ medicine.duration }}</p>
                  </div>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
          
          {% if prescription.notes %}
          <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Doctor's Notes</h4>
            <p class="text-gray-600 bg-blue-50 p-3 rounded-lg">{{ prescription.notes }}</p>
          </div>
          {% endif %}
          
          <div class="flex justify-end space-x-2">
            <a href="/view_prescription/{{ prescription.prescription_id }}{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" 
               class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors text-sm">
              <i class="ri-eye-line mr-1"></i>View Details
            </a>
            <a href="/print_prescription/{{ prescription.prescription_id }}{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" 
               class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors text-sm">
              <i class="ri-printer-line mr-1"></i>Print
            </a>
            <a href="/delete_prescription/{{ prescription.prescription_id }}{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" 
               class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors text-sm"
               onclick="return confirm('Are you sure you want to delete this prescription? This action cannot be undone.')">
              <i class="ri-delete-bin-line mr-1"></i>Delete
            </a>
          </div>
        </div>
        {% endfor %}
        
        {% if not prescriptions %}
        <div class="text-center py-12">
          <div class="text-gray-400 mb-4">
            <i class="ri-medicine-bottle-line text-6xl"></i>
          </div>
          <h3 class="text-xl font-semibold text-gray-600 mb-2">
            {% if patient_phone %}
              {% if patient_name %}
                No Prescriptions Found for Patient: {{ patient_name }} ({{ patient_phone }})
              {% else %}
                No Prescriptions Found for Patient: {{ patient_phone }}
              {% endif %}
            {% else %}
              No Prescriptions Found
            {% endif %}
          </h3>
          <p class="text-gray-500 mb-4">
            {% if patient_phone %}
              This patient doesn't have any prescriptions yet.
            {% else %}
              Start by adding your first prescription.
            {% endif %}
          </p>
          <a href="/add_prescription{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" class="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-colors">
            {% if patient_phone %}
              Add Prescription for This Patient
            {% else %}
              Add First Prescription
            {% endif %}
          </a>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
"""

dashboard_template = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100">
<head>
  <meta charset="UTF-8">
  <title>Dashboard - Aastha Homoeo Clinic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
</head>
<body>
  <nav class="bg-teal-600 p-4 text-white flex justify-between items-center">
    <h1 class="text-xl font-bold">Aastha Homoeo Clinic - Dashboard</h1>
    <div>
      <span class="mr-4">Welcome, Dr. {{ doctor }}</span>
      <a href="{{ url_for('logout') }}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100">Logout</a>
    </div>
  </nav>

  <div class="p-6">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="mb-4 text-sm p-3 rounded bg-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-100 text-{{ 'red' if category == 'error' else 'green' if category == 'success' else 'blue' }}-800">
          {{ message }}
        </div>
      {% endfor %}
    {% endwith %}

    <div class="bg-white rounded-lg shadow-md p-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Appointment Records</h2>
        <div class="flex space-x-2">
          <a href="/add_appointment" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            <i class="ri-add-line mr-1"></i>Add Appointment
          </a>
          <a href="/prescriptions" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            <i class="ri-medicine-bottle-line mr-1"></i>Prescriptions
          </a>
        </div>
      </div>

      <form method="GET" action="/dashboard" class="mb-6 flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-4">
        <input type="text" name="search_query" placeholder="Search by Name or Appointment ID..." 
               class="flex-grow w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500"
               value="{{ search_query if search_query else '' }}">
        <button type="submit" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
          <i class="ri-search-line mr-1"></i>Search
        </button>
        {% if search_query %}
          <a href="/dashboard" class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors">Clear Search</a>
        {% endif %}

        <div class="flex items-center space-x-2 w-full md:w-auto">
          <label for="sort_by" class="text-gray-700">Sort by:</label>
          <select id="sort_by" name="sort_by" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-teal-500">
            <option value="">Default (Latest Created)</option>
            <option value="name_asc" {% if sort_by == 'name_asc' %}selected{% endif %}>Patient Name (A-Z)</option>
            <option value="name_desc" {% if sort_by == 'name_desc' %}selected{% endif %}>Patient Name (Z-A)</option>
            <option value="date_asc" {% if sort_by == 'date_asc' %}selected{% endif %}>Appointment Date (Oldest First)</option>
            <option value="date_desc" {% if sort_by == 'date_desc' %}selected{% endif %}>Appointment Date (Newest First)</option>
          </select>
          <button type="submit" class="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors">
            Sort
          </button>
        </div>
      </form>


      <div class="overflow-x-auto">
        <div class="max-h-[600px] overflow-y-auto border rounded-lg shadow-inner"> 
          <table class="w-full text-sm text-left">
            <thead class="bg-teal-100 text-teal-800 sticky top-0 bg-teal-100 z-10"> 
              <tr>
                <th class="p-2 border">Appointment ID</th>
                <th class="p-2 border">Name</th>
                <th class="p-2 border">Phone</th>
                <th class="p-2 border">Email</th>
                <th class="p-2 border">Address</th>
                <th class="p-2 border">Symptoms</th>
                <th class="p-2 border">Date</th>
                <th class="p-2 border">Time</th>
                <th class="p-2 border">Status</th>
                <th class="p-2 border">Created At</th>
                <th class="p-2 border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {% for appointment in appointments %}
                <tr class="hover:bg-teal-50">
                  <td class="p-2 border">{{ appointment.get('appointment_id', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('name', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('phone', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('email', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('address', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('symptoms', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('date', 'N/A') }}</td>
                  <td class="p-2 border">{{ appointment.get('time', 'N/A') }}</td>
                  <td class="p-2 border">
                    <span class="px-2 py-1 rounded text-xs font-medium 
                      {% if appointment.get('status') == 'confirmed' %}bg-green-100 text-green-800
                      {% elif appointment.get('status') == 'pending' %}bg-yellow-100 text-yellow-800
                      {% elif appointment.get('status') == 'cancelled' %}bg-red-100 text-red-800
                      {% else %}bg-gray-100 text-gray-800{% endif %}">
                      {{ appointment.get('status', 'N/A') }}
                    </span>
                  </td>
                  <td class="p-2 border">{{ appointment.get('created_at_str', 'N/A') }}</td>
                  <td class="p-2 border">
                    <div class="flex flex-col space-y-1"> 
                      {% if appointment.get('status') != 'confirmed' %}
                      <a href="/update_appointment_status/{{ appointment.get('appointment_id', '') }}/confirmed" 
                         class="bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600 text-center"
                         onclick="return confirm('Confirm this appointment?')">
                        Confirm
                      </a>
                      {% endif %}
                      {% if appointment.get('status') != 'cancelled' %}
                      <a href="/update_appointment_status/{{ appointment.get('appointment_id', '') }}/cancelled" 
                         class="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600 text-center"
                         onclick="return confirm('Cancel this appointment?')">
                        Cancel
                      </a>
                      {% endif %}
                      {% if appointment.get('status') == 'confirmed' %}
                      <a href="/update_appointment_status/{{ appointment.get('appointment_id', '') }}/pending" 
                       class="bg-yellow-500 text-white px-2 py-1 rounded text-xs hover:bg-yellow-600 text-center">
                        Pending
                      </a>
                      {% endif %}
                      {# New Edit Button #}
                      <a href="/edit_appointment/{{ appointment.get('appointment_id', '') }}" 
                         class="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600 text-center">
                        Edit
                      </a>
                      {# View Prescriptions Button #}
                      <a href="/prescriptions?patient_phone={{ appointment.get('phone', '') }}" 
                         class="bg-purple-500 text-white px-2 py-1 rounded text-xs hover:bg-purple-600 text-center"
                         title="View prescriptions for {{ appointment.get('name', '') }}">
                        <i class="ri-medicine-bottle-line mr-1"></i>Prescriptions
                      </a>
                    </div>
                  </td>
                </tr>
              {% endfor %}
              {% if not appointments %}
              <tr>
                <td colspan="11" class="p-4 text-center text-gray-500">No appointments found.</td>
              </tr>
              {% endif %}
            </tbody>
          </table>
        </div> {# End of max-height div #}
      </div>
    </div>
  </div>
</body>
</html>

"""

# --- Routes ---
@app.route("/")
def home():
    return render_template_string(home_template)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        doctor = doctors_collection.find_one({"username": username, "password": password})
        if doctor:
            session["doctor"] = username
            flash("Logged in successfully!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password", "error")
            return render_template_string("""
                <!DOCTYPE html>
                <html lang="en" class="bg-gray-100">
                <head>
                    <meta charset="UTF-8">
                    <title>Doctor Login</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="flex items-center justify-center min-h-screen bg-gray-100">
                    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
                        <h2 class="text-2xl font-bold mb-6 text-center text-gray-800">Doctor Login</h2>
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% for category, message in messages %}
                                <div class="mb-4 text-sm p-3 rounded bg-red-100 text-red-800">
                                    {{ message }}
                                </div>
                            {% endfor %}
                        {% endwith %}
                        <form method="POST" action="/login">
                            <div class="mb-4">
                                <label for="username" class="block text-gray-700 text-sm font-bold mb-2">Username:</label>
                                <input type="text" id="username" name="username" required
                                       class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                            </div>
                            <div class="mb-6">
                                <label for="password" class="block text-gray-700 text-sm font-bold mb-2">Password:</label>
                                <input type="password" id="password" name="password" required
                                       class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline">
                            </div>
                            <div class="flex items-center justify-between">
                                <button type="submit"
                                        class="bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                                    Login
                                </button>
                                <a href="/" class="inline-block align-baseline font-bold text-sm text-teal-600 hover:text-teal-800">
                                    Back to Home
                                </a>
                            </div>
                        </form>
                    </div>
                </body>
                </html>
            """)
    
    if "doctor" in session:
        return redirect("/dashboard")
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en" class="bg-gray-100">
        <head>
            <meta charset="UTF-8">
            <title>Doctor Login</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="flex items-center justify-center min-h-screen bg-gray-100">
            <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
                <h2 class="text-2xl font-bold mb-6 text-center text-gray-800">Doctor Login</h2>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% for category, message in messages %}
                        <div class="mb-4 text-sm p-3 rounded bg-red-100 text-red-800">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endwith %}
                <form method="POST" action="/login">
                    <div class="mb-4">
                        <label for="username" class="block text-gray-700 text-sm font-bold mb-2">Username:</label>
                        <input type="text" id="username" name="username" required
                               class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                    </div>
                    <div class="mb-6">
                        <label for="password" class="block text-gray-700 text-sm font-bold mb-2">Password:</label>
                        <input type="password" id="password" name="password" required
                               class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline">
                    </div>
                    <div class="flex items-center justify-between">
                        <button type="submit"
                                class="bg-teal-600 hover:bg-teal-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                            Login
                        </button>
                        <a href="/" class="inline-block align-baseline font-bold text-sm text-teal-600 hover:text-teal-800">
                            Back to Home
                        </a>
                    </div>
                </form>
            </div>
        </body>
        </html>
    """) 

@app.route("/dashboard")
def dashboard():
    if "doctor" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect("/")
    
    search_query = request.args.get('search_query', '').strip()
    sort_by = request.args.get('sort_by', '') 
    
    query = {}
    if search_query:
        query = {
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"appointment_id": {"$regex": search_query, "$options": "i"}},
                {"patient_name": {"$regex": search_query, "$options": "i"}} 
            ]
        }
    
    appointments = list(appointments_collection.find(query))
    
    print(f"Fetched {len(appointments)} appointments from the database for query: {query}")

    for appointment in appointments:
        # Prioritize 'created_at_str' (from Flask app insertions)
        if 'created_at_str' in appointment and appointment['created_at_str'] != 'N/A':
            # Try to parse it to ensure consistency, then re-format
            try:
                # Common format for Flask app: "DD-MM-YYYY HH:MM AM/PM IST"
                dt_obj = datetime.strptime(appointment['created_at_str'], "%d-%m-%Y %I:%M %p IST")
                appointment['created_at_str'] = dt_obj.strftime("%d-%m-%Y %I:%M %p IST")
            except ValueError:
                # If it's already a string but in a different valid format from previous runs, handle it
                # Example: "2025-07-28 09:48 PM IST"
                try:
                    dt_obj = datetime.strptime(appointment['created_at_str'], "%Y-%m-%d %I:%M %p IST") 
                    appointment['created_at_str'] = dt_obj.strftime("%d-%m-%Y %I:%M %p IST")
                except ValueError:
                    # If parsing fails, keep the original string or set to N/A
                    appointment['created_at_str'] = appointment.get('created_at_str', 'N/A')
        # Check for 'created_at' (common for manual insertions or other systems)
        elif 'created_at' in appointment:
            created_val = appointment['created_at']
            if isinstance(created_val, datetime):
                # If it's a datetime object (PyMongo default for BSON Date)
                appointment['created_at_str'] = created_val.strftime("%d-%m-%Y %I:%M %p IST")
            elif isinstance(created_val, str):
                # If it's a string, try to parse various formats
                parsed = False
                formats_to_try = [
                    "%Y-%m-%d %I:%M:%S %p", # Example: "2025-07-28 10:37:39 PM" (from your error)
                    "%Y-%m-%d %I:%M %p",    # Example: "2025-07-28 09:48 PM" (from your dashboard)
                    "%Y-%m-%d %H:%M:%S",    # Common format without AM/PM (if you have any)
                    "%d-%m-%Y %I:%M %p IST" # Already desired format (for existing correct entries)
                ]
                for fmt in formats_to_try:
                    try:
                        dt_obj = datetime.strptime(created_val, fmt)
                        appointment['created_at_str'] = dt_obj.strftime("%d-%m-%Y %I:%M %p IST")
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    # If all parsing attempts fail, keep original or default
                    appointment['created_at_str'] = created_val if created_val else 'N/A'
            else:
                appointment['created_at_str'] = 'N/A' # Fallback for unexpected types
        else:
            # If neither field exists, default to 'N/A'
            appointment['created_at_str'] = 'N/A'
            
        # Also ensure 'name' field is populated for display from 'patient_name' if needed
        if 'name' not in appointment and 'patient_name' in appointment:
            appointment['name'] = appointment['patient_name']

        # Ensure 'phone' field is populated from 'patient_phone' if needed
        if 'phone' not in appointment and 'patient_phone' in appointment:
            appointment['phone'] = appointment['patient_phone']

    # Apply sorting logic
    def get_sort_key_for_date(appointment_item):
        date_str = appointment_item.get('date', '2000-01-01')
        time_str = appointment_item.get('time', '00:00')
        
        # Normalize time_str to 24-hour format if it contains AM/PM
        if 'AM' in time_str or 'PM' in time_str:
            try:
                # Try parsing with seconds, then without seconds
                try:
                    dt_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M:%S %p")
                except ValueError:
                    dt_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
                return dt_obj
            except ValueError:
                return datetime.min # Fallback for unparseable date/time
        else:
            try:
                # Assume 24-hour format if no AM/PM
                dt_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                return dt_obj
            except ValueError:
                return datetime.min # Fallback for unparseable date/time

    if sort_by == 'name_asc':
        appointments.sort(key=lambda x: x.get('name', '').lower())
    elif sort_by == 'name_desc':
        appointments.sort(key=lambda x: x.get('name', '').lower(), reverse=True)
    elif sort_by == 'date_asc':
        appointments.sort(key=get_sort_key_for_date)
    elif sort_by == 'date_desc':
        appointments.sort(key=get_sort_key_for_date, reverse=True)
    else:
        # Default sorting by created_at_str (latest first)
        def get_created_at_sort_key(appointment_item):
            created_at_str = appointment_item.get('created_at_str', '')
            if created_at_str and 'N/A' not in created_at_str:
                # Try multiple formats for created_at_str for sorting
                sort_formats_to_try = [
                    "%d-%m-%Y %I:%M %p IST",  # Your desired output format
                    "%Y-%m-%d %I:%M:%S %p",  # Format from manual entry error
                    "%Y-%m-%d %I:%M %p",     # Another possible format
                    "%Y-%m-%d %H:%M:%S",     # Another common format
                ]
                for fmt in sort_formats_to_try:
                    try:
                        return datetime.strptime(created_at_str, fmt)
                    except ValueError:
                        continue
            return datetime.min # Fallback for 'N/A' or unparseable dates
        
        appointments.sort(key=get_created_at_sort_key, reverse=True)


    return render_template_string(dashboard_template, doctor=session["doctor"], appointments=appointments, search_query=search_query, sort_by=sort_by)

@app.route("/logout")
def logout():
    session.pop("doctor", None)
    flash("You have been logged out.", "success")
    return redirect("/")

@app.route("/update_appointment_status/<appointment_id>/<status>")
def update_appointment_status(appointment_id, status):
    if "doctor" not in session:
        flash("Please log in to update appointment status.", "error")
        return redirect("/")
    
    # Expanded valid statuses based on your dashboard data
    valid_statuses = ['confirmed', 'pending', 'cancelled', 'checked_in', 'booked', 'completed']
    if status not in valid_statuses: 
        flash("Invalid status provided.", "error")
        return redirect("/dashboard")

    try:
        result = appointments_collection.update_one(
            {"appointment_id": appointment_id},
            {"$set": {"status": status}}
        )
        
        if result.modified_count > 0:
            flash(f"Appointment {appointment_id} status updated to {status.capitalize()}.", "success")
        else:
            flash(f"Appointment with ID {appointment_id} not found or status already {status}.", "info") 
    except Exception as e:
        flash(f"Error updating appointment: {str(e)}", "error")
    
    return redirect("/dashboard")

@app.route("/add_appointment", methods=["GET", "POST"])
def add_appointment():
    if "doctor" not in session:
        flash("Please log in to add appointments.", "error")
        return redirect("/")
    
    appointment_data = {} 
    time_slots = generate_time_slots() 
    today_date = datetime.now().strftime("%Y-%m-%d") # Get today's date in YYYY-MM-DD format
    
    # Get the selected date from form or default to today
    selected_date = request.form.get("date", today_date) if request.method == "POST" else today_date
    booked_slots = get_booked_slots_for_date(selected_date)

    if request.method == "POST":
        try:
            name = request.form["name"]
            phone = request.form["phone"]
            email = request.form["email"]
            date = request.form["date"]
            time = request.form["time"] 
            address = request.form["address"]
            symptoms = request.form["symptoms"]

            # Normalize phone number to ensure +91 prefix
            normalized_phone = phone.strip()
            if normalized_phone.startswith('+91'):
                # Already has +91, keep as is
                pass
            elif normalized_phone.startswith('91'):
                # Has 91, add + prefix
                normalized_phone = f"+{normalized_phone}"
            elif normalized_phone.startswith('0'):
                # Has leading 0, remove it and add +91
                normalized_phone = f"+91{normalized_phone[1:]}"
            else:
                # No prefix, add +91
                normalized_phone = f"+91{normalized_phone}"

            appointment_data = {
                "name": name,
                "phone": normalized_phone,
                "email": email,
                "date": date,
                "time": time,
                "address": address,
                "symptoms": symptoms
            }

            # Server-side validation for date:
            if date < today_date:
                flash("Cannot book an appointment for a past date.", "error")
                return render_template_string(appointment_form_template, mode='add', appointment_data=appointment_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)


            existing_appointment = appointments_collection.find_one({
                "date": date,
                "time": time
            })
            
            if existing_appointment:
                flash(f"An appointment already exists for {date} at {time}. Please choose a different time or date.", "error")
                return render_template_string(appointment_form_template, mode='add', appointment_data=appointment_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)

            date_str = datetime.now().strftime("%Y%m%d")
            while True:
                random_num = str(random.randint(1, 9999)).zfill(4)
                potential_appointment_id = f"AHC-{date_str}-{random_num}"
                if not appointments_collection.find_one({"appointment_id": potential_appointment_id}):
                    appointment_id = potential_appointment_id
                    break
            
            new_appointment_data = {
                "appointment_id": appointment_id,
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
                "symptoms": symptoms,
                "date": date,
                "time": time,
                "status": "pending",
                "created_at_str": datetime.now().strftime("%d-%m-%Y %I:%M %p IST") 
            }
            
            appointments_collection.insert_one(new_appointment_data)
            flash(f"Appointment {appointment_id} created successfully.", "success")
            return redirect("/dashboard")
            
        except Exception as e:
            flash(f"Error creating appointment: {str(e)}", "error")
            return render_template_string(appointment_form_template, mode='add', appointment_data=appointment_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)
    
    return render_template_string(appointment_form_template, mode='add', appointment_data=appointment_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)

@app.route("/edit_appointment/<appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if "doctor" not in session:
        flash("Please log in to edit appointments.", "error")
        return redirect("/")
    
    appointment = appointments_collection.find_one({"appointment_id": appointment_id})

    if not appointment:
        flash("Appointment not found.", "error")
        return redirect("/dashboard")

    time_slots = generate_time_slots() 
    today_date = datetime.now().strftime("%Y-%m-%d") 
    
    # Get the selected date from form or use appointment date
    selected_date = request.form.get("date", appointment.get("date", today_date)) if request.method == "POST" else appointment.get("date", today_date)
    booked_slots = get_booked_slots_for_date(selected_date, exclude_appointment_id=appointment_id)

    if request.method == "POST":
        try:
            # Normalize phone number to ensure +91 prefix
            phone = request.form["phone"]
            normalized_phone = phone.strip()
            if normalized_phone.startswith('+91'):
                # Already has +91, keep as is
                pass
            elif normalized_phone.startswith('91'):
                # Has 91, add + prefix
                normalized_phone = f"+{normalized_phone}"
            elif normalized_phone.startswith('0'):
                # Has leading 0, remove it and add +91
                normalized_phone = f"+91{normalized_phone[1:]}"
            else:
                # No prefix, add +91
                normalized_phone = f"+91{normalized_phone}"

            updated_data = {
                "name": request.form["name"],
                "phone": normalized_phone,
                "email": request.form["email"],
                "date": request.form["date"],
                "time": request.form["time"], 
                "address": request.form["address"],
                "symptoms": request.form["symptoms"]
            }

            # Server-side validation for date:
            if updated_data["date"] < today_date:
                flash("Cannot set appointment date to a past date.", "error")
                return render_template_string(appointment_form_template, mode='edit', appointment_data=updated_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)


            existing_conflict = appointments_collection.find_one({
                "date": updated_data["date"],
                "time": updated_data["time"],
                "appointment_id": {"$ne": appointment_id}
            })

            if existing_conflict:
                flash(f"Another appointment already exists for {updated_data['date']} at {updated_data['time']}. Please choose a different time or date.", "error")
                return render_template_string(appointment_form_template, mode='edit', appointment_data=updated_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)

            result = appointments_collection.update_one(
                {"appointment_id": appointment_id},
                {"$set": updated_data}
            )

            if result.modified_count > 0:
                flash(f"Appointment {appointment_id} updated successfully.", "success")
            else:
                flash(f"No changes made to appointment {appointment_id}.", "info")
            
            return redirect("/dashboard")

        except Exception as e:
            flash(f"Error updating appointment: {str(e)}", "error")
            return render_template_string(appointment_form_template, mode='edit', appointment_data=updated_data, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)
    
    return render_template_string(appointment_form_template, mode='edit', appointment_data=appointment, time_slots=time_slots, today_date=today_date, booked_slots=booked_slots)

@app.route("/get_booked_slots/<date>")
def get_booked_slots(date):
    """API endpoint to get booked slots for a specific date"""
    if "doctor" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        booked_slots = get_booked_slots_for_date(date)
        return jsonify({"booked_slots": booked_slots})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Prescription Routes ---
@app.route("/add_prescription", methods=["GET", "POST"])
def add_prescription():
    if "doctor" not in session:
        flash("Please log in to add prescriptions.", "error")
        return redirect("/")
    
    prescription_data = {}
    today_date = datetime.now().strftime("%Y-%m-%d")
    
                # Check for patient information from query parameters (when coming from patient-specific view)
    if request.method == "GET":
        patient_phone = request.args.get('patient_phone', '').strip()
        print(f"DEBUG: Received patient_phone parameter: '{patient_phone}'")
        if patient_phone:
            # Normalize phone number for search (remove +91 if present, add if missing)
            normalized_phone = patient_phone
            if patient_phone.startswith('+91'):
                normalized_phone = patient_phone[3:]  # Remove +91
            elif patient_phone.startswith('91'):
                normalized_phone = patient_phone[2:]  # Remove 91
            elif patient_phone.startswith('0'):
                normalized_phone = patient_phone[1:]  # Remove leading 0
            
            # Try multiple phone number formats for search
            phone_variants = [
                patient_phone,  # Original format
                f"+91{normalized_phone}",  # With +91
                f"91{normalized_phone}",   # With 91
                f"0{normalized_phone}",    # With 0
                normalized_phone           # Clean number
            ]
            
            print(f"DEBUG: Searching with phone variants: {phone_variants}")
            
            # Try to get patient name from appointments
            appointment = None
            for phone_variant in phone_variants:
                appointment = appointments_collection.find_one({"phone": phone_variant})
                if appointment:
                    print(f"DEBUG: Found appointment with phone variant: '{phone_variant}'")
                    break
            
            if appointment:
                prescription_data["patient_name"] = appointment.get("name", "")
                prescription_data["patient_phone"] = appointment.get("phone", patient_phone)
                print(f"DEBUG: Found appointment for {patient_phone}, name: {appointment.get('name', '')}")
            else:
                # Check if patient exists in prescriptions
                prescription = None
                for phone_variant in phone_variants:
                    prescription = prescriptions_collection.find_one({"patient_phone": phone_variant})
                    if prescription:
                        print(f"DEBUG: Found prescription with phone variant: '{phone_variant}'")
                        break
                
                if prescription:
                    prescription_data["patient_name"] = prescription.get("patient_name", "")
                    prescription_data["patient_phone"] = prescription.get("patient_phone", patient_phone)
                    print(f"DEBUG: Found prescription for {patient_phone}, name: {prescription.get('patient_name', '')}")
                else:
                    print(f"DEBUG: No patient found for phone: {patient_phone}")
                    # Let's also check what phone numbers exist in the database
                    all_appointments = list(appointments_collection.find({}, {"phone": 1, "name": 1}))
                    print(f"DEBUG: All phone numbers in appointments: {[a.get('phone') for a in all_appointments]}")
                    all_prescriptions = list(prescriptions_collection.find({}, {"patient_phone": 1, "patient_name": 1}))
                    print(f"DEBUG: All phone numbers in prescriptions: {[p.get('patient_phone') for p in all_prescriptions]}")
        
        print(f"DEBUG: Final prescription_data: {prescription_data}")
    
    if request.method == "POST":
        try:
            patient_name = request.form["patient_name"]
            patient_phone = request.form["patient_phone"]
            prescription_date = request.form["prescription_date"]
            diagnosis = request.form["diagnosis"]
            instructions = request.form["instructions"]
            notes = request.form["notes"]
            
            # Normalize phone number to ensure +91 prefix
            normalized_phone = patient_phone.strip()
            if normalized_phone.startswith('+91'):
                # Already has +91, keep as is
                pass
            elif normalized_phone.startswith('91'):
                # Has 91, add + prefix
                normalized_phone = f"+{normalized_phone}"
            elif normalized_phone.startswith('0'):
                # Has leading 0, remove it and add +91
                normalized_phone = f"+91{normalized_phone[1:]}"
            else:
                # No prefix, add +91
                normalized_phone = f"+91{normalized_phone}"
            
            # Get medicine data from form arrays
            medicine_names = request.form.getlist("medicine_names[]")
            potencies = request.form.getlist("potencies[]")
            dosages = request.form.getlist("dosages[]")
            durations = request.form.getlist("durations[]")
            
            # Validate that we have at least one medicine
            if not medicine_names or not medicine_names[0]:
                flash("At least one medicine is required.", "error")
                prescription_data = {
                    "patient_name": patient_name,
                    "patient_phone": normalized_phone,
                    "prescription_date": prescription_date,
                    "diagnosis": diagnosis,
                    "instructions": instructions,
                    "notes": notes
                }
                return render_template_string(prescription_form_template, prescription_data=prescription_data, today_date=today_date)
            
            # Create medicines list
            medicines = []
            for i in range(len(medicine_names)):
                if medicine_names[i].strip():  # Only add if medicine name is not empty
                    medicines.append({
                        "name": medicine_names[i].strip(),
                        "potency": potencies[i].strip() if i < len(potencies) else "",
                        "dosage": dosages[i].strip() if i < len(dosages) else "",
                        "duration": durations[i].strip() if i < len(durations) else ""
                    })
            
            # Generate prescription ID
            date_str = datetime.now().strftime("%Y%m%d")
            while True:
                random_num = str(random.randint(1, 9999)).zfill(4)
                potential_prescription_id = f"PRES-{date_str}-{random_num}"
                if not prescriptions_collection.find_one({"prescription_id": potential_prescription_id}):
                    prescription_id = potential_prescription_id
                    break
            
            new_prescription_data = {
                "prescription_id": prescription_id,
                "patient_name": patient_name,
                "patient_phone": normalized_phone,
                "prescription_date": prescription_date,
                "diagnosis": diagnosis,
                "medicines": medicines,
                "instructions": instructions,
                "notes": notes,
                "created_at_str": datetime.now().strftime("%d-%m-%Y %I:%M %p IST")
            }
            
            prescriptions_collection.insert_one(new_prescription_data)
            flash(f"Prescription {prescription_id} created successfully.", "success")
            
            # Redirect back to patient-specific view if we came from there
            if normalized_phone:
                return redirect(f"/prescriptions?patient_phone={normalized_phone}")
            else:
                return redirect("/prescriptions")
            
        except Exception as e:
            flash(f"Error creating prescription: {str(e)}", "error")
            prescription_data = {
                "patient_name": patient_name if 'patient_name' in locals() else "",
                "patient_phone": normalized_phone if 'normalized_phone' in locals() else (patient_phone if 'patient_phone' in locals() else ""),
                "prescription_date": prescription_date if 'prescription_date' in locals() else today_date,
                "diagnosis": diagnosis if 'diagnosis' in locals() else "",
                "instructions": instructions if 'instructions' in locals() else "",
                "notes": notes if 'notes' in locals() else ""
            }
            return render_template_string(prescription_form_template, prescription_data=prescription_data, today_date=today_date)
    
    print(f"DEBUG: Final render with prescription_data: {prescription_data}")
    print(f"DEBUG: Template will receive prescription_data.patient_name: '{prescription_data.get('patient_name', 'NOT_FOUND')}'")
    print(f"DEBUG: Template will receive prescription_data.patient_phone: '{prescription_data.get('patient_phone', 'NOT_FOUND')}'")
    return render_template_string(prescription_form_template, prescription_data=prescription_data, today_date=today_date)

@app.route("/prescriptions")
def prescriptions():
    if "doctor" not in session:
        flash("Please log in to view prescriptions.", "error")
        return redirect("/")
    
    search_query = request.args.get('search_query', '').strip()
    sort_by = request.args.get('sort_by', '')
    patient_phone = request.args.get('patient_phone', '').strip()
    
    query = {}
    if patient_phone:
        # Filter by specific patient phone number
        query["patient_phone"] = patient_phone
    elif search_query:
        query = {
            "$or": [
                {"patient_name": {"$regex": search_query, "$options": "i"}},
                {"patient_phone": {"$regex": search_query, "$options": "i"}},
                {"prescription_id": {"$regex": search_query, "$options": "i"}}
            ]
        }
    
    prescriptions_list = list(prescriptions_collection.find(query))
    
    # Apply sorting
    if sort_by == 'patient_name_asc':
        prescriptions_list.sort(key=lambda x: x.get('patient_name', '').lower())
    elif sort_by == 'patient_name_desc':
        prescriptions_list.sort(key=lambda x: x.get('patient_name', '').lower(), reverse=True)
    elif sort_by == 'date_asc':
        prescriptions_list.sort(key=lambda x: x.get('prescription_date', ''))
    elif sort_by == 'date_desc':
        prescriptions_list.sort(key=lambda x: x.get('prescription_date', ''), reverse=True)
    else:
        # Default sorting by created_at_str (latest first)
        def get_created_at_sort_key(prescription_item):
            created_at_str = prescription_item.get('created_at_str', '')
            if created_at_str and 'N/A' not in created_at_str:
                try:
                    return datetime.strptime(created_at_str, "%d-%m-%Y %I:%M %p IST")
                except ValueError:
                    return datetime.min
            return datetime.min
        
        prescriptions_list.sort(key=get_created_at_sort_key, reverse=True)
    
    # Get patient name for display if filtering by patient_phone
    patient_name = ""
    if patient_phone and prescriptions_list:
        # Get the patient name from the first prescription
        patient_name = prescriptions_list[0].get('patient_name', '')
    elif patient_phone:
        # If no prescriptions found, try to get patient name from appointments
        appointment = appointments_collection.find_one({"phone": patient_phone})
        if appointment:
            patient_name = appointment.get('name', '')
    
    return render_template_string(prescription_history_template, prescriptions=prescriptions_list, search_query=search_query, sort_by=sort_by, patient_phone=patient_phone, patient_name=patient_name)

@app.route("/view_prescription/<prescription_id>")
def view_prescription(prescription_id):
    if "doctor" not in session:
        flash("Please log in to view prescriptions.", "error")
        return redirect("/")
    
    prescription = prescriptions_collection.find_one({"prescription_id": prescription_id})
    
    if not prescription:
        flash("Prescription not found.", "error")
        return redirect("/prescriptions")
    
    # Get patient_phone from query parameter for back navigation
    patient_phone = request.args.get('patient_phone', '')
    
    # Create a detailed view template for single prescription
    detailed_template = """
    <!DOCTYPE html>
    <html lang="en" class="bg-gray-100">
    <head>
      <meta charset="UTF-8">
      <title>Prescription Details - Aastha Homoeo Clinic</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css">
    </head>
    <body>
      <nav class="bg-teal-600 p-4 text-white flex justify-between items-center">
        <h1 class="text-xl font-bold">Aastha Homoeo Clinic - Prescription Details</h1>
        <div>
          <a href="/prescriptions{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Back to Prescriptions</a>
          <a href="/dashboard" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100 mr-2">Dashboard</a>
          <a href="{{ url_for('logout') }}" class="bg-white text-teal-700 px-3 py-1 rounded hover:bg-teal-100">Logout</a>
        </div>
      </nav>

      <div class="p-6">
        <div class="bg-white rounded-lg shadow-md p-8 max-w-4xl mx-auto">
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="text-3xl font-bold text-gray-800">{{ prescription.patient_name }}</h2>
              <p class="text-lg text-gray-600">{{ prescription.patient_phone }}</p>
              <p class="text-gray-500">Prescription ID: {{ prescription.prescription_id }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-500">Prescription Date</p>
              <p class="text-lg font-semibold text-gray-800">{{ prescription.prescription_date }}</p>
              <p class="text-sm text-gray-500">{{ prescription.created_at_str }}</p>
            </div>
          </div>
          
          <div class="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 class="text-xl font-semibold text-gray-700 mb-3">Diagnosis</h3>
              <p class="text-gray-600 text-lg">{{ prescription.diagnosis }}</p>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-700 mb-3">Special Instructions</h3>
              <p class="text-gray-600">{{ prescription.instructions or 'None provided' }}</p>
            </div>
          </div>
          
          <div class="mb-8">
            <h3 class="text-xl font-semibold text-gray-700 mb-4">Medicines Prescribed</h3>
            <div class="bg-gray-50 rounded-lg p-6">
              {% for medicine in prescription.medicines %}
              <div class="border border-gray-200 rounded-lg p-4 mb-4 last:mb-0">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 class="font-semibold text-gray-800 text-lg mb-2">{{ medicine.name }}</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="font-medium text-gray-700">Potency:</span>
                        <span class="text-gray-600">{{ medicine.potency }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="font-medium text-gray-700">Dosage:</span>
                        <span class="text-gray-600">{{ medicine.dosage }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="font-medium text-gray-700">Duration:</span>
                        <span class="text-gray-600">{{ medicine.duration }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
          
          {% if prescription.notes %}
          <div class="mb-8">
            <h3 class="text-xl font-semibold text-gray-700 mb-3">Doctor's Notes</h3>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p class="text-gray-700">{{ prescription.notes }}</p>
            </div>
          </div>
          {% endif %}
          
          <div class="flex justify-center space-x-4 pt-6 border-t border-gray-200">
            <a href="/prescriptions" class="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors">
              <i class="ri-arrow-left-line mr-2"></i>Back to Prescriptions
            </a>
            <a href="/print_prescription/{{ prescription.prescription_id }}" class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors">
              <i class="ri-printer-line mr-2"></i>Print Prescription
            </a>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    
    return render_template_string(detailed_template, prescription=prescription, patient_phone=patient_phone)

@app.route("/print_prescription/<prescription_id>")
def print_prescription(prescription_id):
    if "doctor" not in session:
        flash("Please log in to print prescriptions.", "error")
        return redirect("/")
    
    prescription = prescriptions_collection.find_one({"prescription_id": prescription_id})
    
    if not prescription:
        flash("Prescription not found.", "error")
        return redirect("/prescriptions")
    
    # Get patient_phone from query parameter for back navigation
    patient_phone = request.args.get('patient_phone', '')
    
    # Create a print-friendly template
    print_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Prescription - {{ prescription.patient_name }}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .clinic-name { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .clinic-info { font-size: 14px; color: #666; }
        .patient-info { margin-bottom: 30px; }
        .patient-info h3 { margin: 0 0 10px 0; color: #333; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 25px; }
        .section h4 { margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        .medicine { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        .medicine h5 { margin: 0 0 10px 0; color: #333; }
        .medicine-details { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
        .detail-item { margin-bottom: 8px; }
        .detail-label { font-weight: bold; color: #555; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; }
        .signature-line { margin-top: 50px; }
        @media print {
          body { margin: 0; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="clinic-name">Aastha Homoeo Clinic</div>
        <div class="clinic-info">Dr. Priya Sharma, BHMS, MD (Homeopathy)</div>
        <div class="clinic-info">Hyderabad, India | Phone: +91 98765 43210</div>
      </div>
      
      <div class="patient-info">
        <h3>Patient Information</h3>
        <div class="info-grid">
          <div><strong>Name:</strong> {{ prescription.patient_name }}</div>
          <div><strong>Phone:</strong> {{ prescription.patient_phone }}</div>
          <div><strong>Prescription Date:</strong> {{ prescription.prescription_date }}</div>
          <div><strong>Prescription ID:</strong> {{ prescription.prescription_id }}</div>
        </div>
      </div>
      
      <div class="section">
        <h4>Diagnosis</h4>
        <p>{{ prescription.diagnosis }}</p>
      </div>
      
      <div class="section">
        <h4>Medicines Prescribed</h4>
        {% for medicine in prescription.medicines %}
        <div class="medicine">
          <h5>{{ medicine.name }}</h5>
          <div class="medicine-details">
            <div class="detail-item">
              <span class="detail-label">Potency:</span> {{ medicine.potency }}
            </div>
            <div class="detail-item">
              <span class="detail-label">Dosage:</span> {{ medicine.dosage }}
            </div>
            <div class="detail-item">
              <span class="detail-label">Duration:</span> {{ medicine.duration }}
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
      
      {% if prescription.instructions %}
      <div class="section">
        <h4>Special Instructions</h4>
        <p>{{ prescription.instructions }}</p>
      </div>
      {% endif %}
      
      {% if prescription.notes %}
      <div class="section">
        <h4>Doctor's Notes</h4>
        <p>{{ prescription.notes }}</p>
      </div>
      {% endif %}
      
      <div class="footer">
        <div class="signature-line">
          <p>_________________________</p>
          <p><strong>Dr. Priya Sharma</strong></p>
          <p>BHMS, MD (Homeopathy)</p>
          <p>Date: {{ prescription.prescription_date }}</p>
        </div>
      </div>
      
      <div class="no-print" style="text-align: center; margin-top: 30px;">
        <button onclick="window.print()" style="background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">Print</button>
        <a href="/prescriptions{% if patient_phone %}?patient_phone={{ patient_phone }}{% endif %}" style="background: #666; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Prescriptions</a>
      </div>
    </body>
    </html>
    """
    
    return render_template_string(print_template, prescription=prescription, patient_phone=patient_phone)

@app.route("/delete_prescription/<prescription_id>")
def delete_prescription(prescription_id):
    if "doctor" not in session:
        flash("Please log in to delete prescriptions.", "error")
        return redirect("/")
    
    prescription = prescriptions_collection.find_one({"prescription_id": prescription_id})
    
    if not prescription:
        flash("Prescription not found.", "error")
        return redirect("/prescriptions")
    
    try:
        prescriptions_collection.delete_one({"prescription_id": prescription_id})
        flash(f"Prescription {prescription_id} deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting prescription: {str(e)}", "error")
    
    # Redirect back to prescriptions page, preserving patient_phone if it was a patient-specific view
    patient_phone = request.args.get('patient_phone', '')
    if patient_phone:
        return redirect(f"/prescriptions?patient_phone={patient_phone}")
    else:
        return redirect("/prescriptions")

if __name__ == "__main__":
    # Create default doctor account if none exists
    if doctors_collection.count_documents({}) == 0:
        doctors_collection.insert_one({"username": "drpriya", "password": "password123"})
        print("Default doctor 'drpriya' created with password 'password123'. Please change this in production!")
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)