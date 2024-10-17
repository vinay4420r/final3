const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.urlencoded({ extended: true })); // For form submissions

let submissionCounter = 0; // Global counter for submission ID
const submissions = {};    // Store submissions (you can replace this with a DB)

app.set('view engine', 'ejs');  // Assuming EJS for templating (optional)

// Configure Nodemailer for email sending
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'kv7216509@gmail.com',
        pass: 'usrh ccdo vjup fczv'  // Replace with app password, not actual password
    }
});

// Function to generate unique submission code
function generateUniqueCode() {
    submissionCounter++;
    return `IJEMSS${String(submissionCounter).padStart(3, '0')}`;
}

// Route to handle form submission
app.post('/submit', (req, res) => {
    // Collect form data
    const paperTitle = req.body.paper_title;
    const abstract = req.body.abstract;
    const researchArea = req.body.research_area;
    const authors = [];

    // Collect author details (up to 7 authors)
    for (let i = 1; i <= 7; i++) {
        const authorName = req.body[`author_name_${i}`];
        const authorEmail = req.body[`author_email_${i}`];
        const authorContact = req.body[`author_contact_${i}`];
        const authorInstitute = req.body[`author_institute_${i}`];

        if (authorName && authorEmail && authorContact && authorInstitute) {
            authors.push({
                name: authorName,
                email: authorEmail,
                contact: authorContact,
                institute: authorInstitute
            });
        }
    }

    // Generate a unique submission ID
    const uniqueCode = generateUniqueCode();

    // Store the submission details
    submissions[uniqueCode] = {
        paperTitle: paperTitle,
        researchArea: researchArea,
        status: 'Wait for 48 to 72 hours',
        authors: authors
    };

    // Send confirmation email to the first author (if available)
    if (authors.length > 0) {
        const firstAuthor = authors[0];
        const mailOptions = {
            from: 'your-email@gmail.com',
            to: firstAuthor.email,
            subject: 'Paper Submission Confirmation',
            text: `
Dear ${firstAuthor.name},

Thank you for submitting your paper to IJEMSS. Here are the details of your submission:

Paper Title: ${paperTitle}
Unique Submission ID: ${uniqueCode}
Current Status: Wait for 48 to 72 hours.

Best regards,
IJEMSS Team`
        };

        transporter.sendMail(mailOptions, (error, info) => {
            if (error) {
                console.log('Error sending email: ', error);
            } else {
                console.log('Email sent: ' + info.response);
            }
        });
    }

    // Send notification to admin with submission details
    const adminMailOptions = {
        from: 'your-email@gmail.com',
        to: 'kvinay00912@gmail.com`',  // Admin's email
        subject: 'New Paper Submission',
        text: `
A new paper has been submitted.

Submission ID: ${uniqueCode}
Paper Title: ${paperTitle}
Research Area: ${researchArea}

First Author: ${authors[0] ? authors[0].name : 'N/A'}
`
    };

    transporter.sendMail(adminMailOptions, (error, info) => {
        if (error) {
            console.log('Error sending admin email: ', error);
        } else {
            console.log('Admin email sent: ' + info.response);
        }
    });

    // Response to the form submitter
    res.send('Form submitted successfully! Your submission ID is: ' + uniqueCode);
});

// Route to render the form (for testing)
app.get('/', (req, res) => {
    res.render('submit'); // Assuming submit.ejs exists
});

// Start the server
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
