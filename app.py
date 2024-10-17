from flask import Flask, request, render_template, redirect, flash, session, url_for, Response
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kv7216509@gmail.com'  # Use your actual Gmail credentials
app.config['MAIL_PASSWORD'] = 'usrh ccdo vjup fczv'  # Use your actual app-specific password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.secret_key = 'supersecretkey'  # Required for sessions

mail = Mail(app)

# Global counter for submission ID (in production, use a database)
submission_counter = 0

# Dictionary to store submissions and statuses (in production, replace this with a database)
submissions = {}

def generate_unique_code():
    global submission_counter
    submission_counter += 1
    return f"IJEMSS{str(submission_counter).zfill(3)}"  # Unique code format

# Mocked admin credentials (replace these with a more secure method in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'yourpassword'

# Route to render the login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_page'))  # Redirect to admin page if login successful
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

# Route for logging out
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Paper submission route
@app.route('/', methods=['GET', 'POST'])
def submit_form():
    if request.method == 'POST':
        # Get the form fields
        paper_title = request.form['paper_title']
        abstract = request.form['abstract']
        research_area = request.form['research_area']
        country = request.form['country']

        # Author details (up to 7 authors)
        authors = []
        for i in range(1, 8):
            author_name = request.form.get(f'author_name_{i}', 'Empty')
            author_email = request.form.get(f'author_email_{i}', 'Empty')
            author_contact = request.form.get(f'author_contact_{i}', 'Empty')
            author_institute = request.form.get(f'author_institute_{i}', 'Empty')
            
            authors.append({
                'name': author_name or 'Empty',
                'email': author_email or 'Empty',
                'contact': author_contact or 'Empty',
                'institute': author_institute or 'Empty'
            })

        # Handle file upload
        file = request.files['file']

        # Generate a unique submission code
        unique_code = generate_unique_code()

        # Set default status as "Wait for 48 to 72 hours"
        submissions[unique_code] = {
            'paper_title': paper_title,
            'research_area': research_area,
            'status': 'Wait for 48 to 72 hours'
        }

        # Prepare email details for user (only first author receives confirmation)
        user_email = authors[0]['email'] if authors else None
        if user_email != 'Empty':
            confirmation_msg = Message('Paper Submission Confirmation',
                                       sender='kv7216509@gmail.com',
                                       recipients=[user_email])
            confirmation_msg.body = f"""
            Dear {authors[0]['name']},
            
Thanks for considering IJPREMS. Your paper has been successfully received.
Paper Title: {paper_title}

Your unique submission ID is: {unique_code}

The current status is: Wait for 48 to 72 hours.

For further communication, refer to Paper ID-{unique_code}

Best regards,
Journal Team
            """
            mail.send(confirmation_msg)

        # Prepare email details for admin with all author details
        admin_msg = Message('New Paper Submission',
                            sender='kv7216509@gmail.com',
                            recipients=['kv7216509@gmail.com'])
        
        # Generate the admin email body with all authors
        author_details = "\n".join([f"Author {i+1}:\n  Name: {a['name']}\n  Email: {a['email']}\n  Contact: {a['contact']}\n  Institute: {a['institute']}\n"
                                    for i, a in enumerate(authors)])

        admin_msg.body = f"""
        A new paper has been submitted.

        Submission ID: {unique_code}
        Paper Title: {paper_title}
        Research Area: {research_area}

        Author Details:
        {author_details}
        """

        if file:
            admin_msg.attach(file.filename, file.content_type, file.read())
        mail.send(admin_msg)

        # Save the uploaded file to the server
        if file:
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            file.save(os.path.join('uploads', file.filename))

        return "Form submitted successfully!"

    return render_template('submit.html')

# Route for tracking submission status
@app.route('/track', methods=['GET', 'POST'])
def track_submission():
    if request.method == 'POST':
        submission_code = request.form['submission_code']
        paper_found = False
        paper_not_found = False

        if submission_code in submissions:
            paper_found = True
            submission_details = submissions[submission_code]
            return render_template('track1.html', 
                                   paper_found=paper_found, 
                                   submission_code=submission_code,
                                   paper_title=submission_details['paper_title'],
                                   research_area=submission_details['research_area'],
                                   status=submission_details['status'])
        else:
            paper_not_found = True
            return render_template('track1.html', paper_not_found=paper_not_found)

    return render_template('track1.html')

# Protecting the admin route with session authentication
@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        submission_code = request.form['submission_code']
        new_status = request.form['new_status']
        
        # Update the status if submission exists
        if submission_code in submissions:
            submissions[submission_code]['status'] = new_status
            flash(f"Status for submission {submission_code} has been updated to {new_status}")
        else:
            flash(f"Submission with code {submission_code} not found.")
    
    return render_template('admin.html', submissions=submissions)

# Route for reviewer form submission
@app.route('/reviewer', methods=['GET', 'POST'])
def reviewer_form():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        qualification = request.form['qualification']
        specialization = request.form['specialization']
        country = request.form['country']
        resume = request.files['resume']
        photo = request.files['photo']

        # Email the details to admin
        admin_msg = Message('New Reviewer Membership Submission',
                            sender='kv7216509@gmail.com',
                            recipients=['kv7216509@gmail.com'])
        admin_msg.body = f"""
        A new reviewer has applied for membership.

        Name: {full_name}
        Email: {email}
        Qualification: {qualification}
        Specialization: {specialization}
        Country: {country}
        """
        if resume:
            admin_msg.attach(resume.filename, resume.content_type, resume.read())
        if photo:
            admin_msg.attach(photo.filename, photo.content_type, photo.read())
        mail.send(admin_msg)

        return "Reviewer form submitted successfully!"

    return render_template('review.html')

if __name__ == '__main__':
    app.run(debug=True)
