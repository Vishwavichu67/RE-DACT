from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import re
import io
from docx import Document
from PIL import Image, ImageDraw, ImageFilter
import pytesseract
from pytesseract import Output
import fitz  # PyMuPDF for PDF manipulation
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path as needed

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['REDACTED_IMAGES_FOLDER'] = 'redacted_images/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png'}
app.config['REDACTED_DOCUMENTS_FOLDER'] = './redacted_documents'


# Ensure the required folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REDACTED_IMAGES_FOLDER'], exist_ok=True)
os.makedirs(app.config['REDACTED_DOCUMENTS_FOLDER'], exist_ok=True)


# Patterns for redaction
PATTERNS = {
    "name": r"\b([A-Z][a-z]*\s[A-Z][a-z]*)\b",  # Full name (e.g., John Doe)
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",  # Credit card numbers
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",  # Social Security Numbers (e.g., 123-45-6789)
    "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",  # IP addresses
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email addresses
    "password": r"(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}",
    "address": r"(?i)(\bAddress:\s*.+)",
    "phone_number": r"(?i)(\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{4,6})",
    "account_number": r"(?i)(\d{4}[-\s]?){4}",
   
}

# Helper function: Allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function: Save uploaded files
def save_uploaded_file(file, folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(folder, filename)
    file.save(file_path)
    return file_path, filename

# Redact text content
def redact_text(content, patterns=PATTERNS, level='low'):
    logging.info(f"Original Content: {content}")
    redacted_content = content

    # Check for sensitive patterns
    for label, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            logging.info(f"Sensitive pattern '{label}' matches found: {matches}")
            for match in matches:
                if level == 'low':
                    # Partially redact sensitive matches (e.g., show first 2 characters)
                    replacement = f"{match[:2]}{'*' * (len(match) - 4)}{match[-2:]}"
                elif level == 'moderate':
                    # Fully redact sensitive matches
                    replacement = "*" * len(match)
                elif level == 'high':
                    # Completely redact with fixed placeholder
                    replacement = "*****"
                redacted_content = redacted_content.replace(match, replacement)

    # Handle input with no sensitive patterns
    if redacted_content == content:
        logging.info("No sensitive patterns matched. Applying default redaction.")
        if level == 'low':
            redacted_content = redact_random_text(content, percentage=30)
        elif level == 'moderate':
            redacted_content = redact_random_text(content, percentage=60)
        elif level == 'high':
            redacted_content = "*****"

    logging.info(f"Redacted Content: {redacted_content}")
    return redacted_content

# Helper function to redact random text by percentage
def redact_random_text(text, percentage):
    num_chars_to_redact = int(len(text) * (percentage / 100))
    redacted = list(text)
    for i in range(num_chars_to_redact):
        if redacted[i].isalnum():  # Only redact alphanumeric characters
            redacted[i] = "*"
    return "".join(redacted)

#redact the image
def redact_image(file_path, redaction_level):
    try:
        img = Image.open(file_path)
        img = img.convert("RGB")  # Ensure image compatibility

        if redaction_level == 'blur':
            img = img.filter(ImageFilter.GaussianBlur(15))  # Apply a strong blur
        elif redaction_level == 'black':
            draw = ImageDraw.Draw(img)
            draw.rectangle([0, 0, img.width, img.height], fill="black")  # Black out the entire image
        else:
            raise ValueError("Invalid redaction level provided.")

        return img  # Return the redacted image object
    except Exception as e:
        logging.error(f"Error in redact_image: {e}")
        raise


def redact_text_in_image(file_path, patterns=PATTERNS, redaction_level='high'):
    try:
        logging.info(f"Opening image for OCR: {file_path}")
        img = Image.open(file_path)
        img = img.convert("RGB")

        logging.info(f"Applied redaction level: {redaction_level}")

        # Test pattern matching for debugging
        test_text = "John Doe, 123-456-7890"
        for label, pattern in patterns.items():
            logging.info(f"Testing pattern '{label}' against sample text '{test_text}': {re.search(pattern, test_text)}")

        # Perform OCR on the image
        ocr_result = pytesseract.image_to_data(img, output_type=Output.DICT)

        # Log OCR results for debugging
        logging.info(f"OCR Results: {ocr_result['text']}")

        # Draw on the image for redaction
        draw = ImageDraw.Draw(img)

        for i, text in enumerate(ocr_result['text']):
            if text.strip():  # Only process non-empty text
                logging.info(f"Processing text: {text.strip()}")
                for label, pattern in patterns.items():
                    if re.search(pattern, text):
                        logging.info(f"Match found for pattern '{label}': {text.strip()}")
                        (x, y, w, h) = (ocr_result['left'][i], ocr_result['top'][i],
                                        ocr_result['width'][i], ocr_result['height'][i])

                        if redaction_level == 'blur':
                            crop = img.crop((x, y, x + w, y + h))
                            crop = crop.filter(ImageFilter.GaussianBlur(15))
                            img.paste(crop, (x, y))
                            logging.info(f"Blur applied to region: {(x, y, w, h)}")

                        elif redaction_level == 'black':
                            draw.rectangle([x, y, x + w, y + h], fill="black")
                            logging.info(f"Black rectangle drawn at: {(x, y, w, h)}")

                        elif redaction_level == 'moderate':
                            # Semi-transparent rectangle
                            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                            overlay_draw = ImageDraw.Draw(overlay)
                            overlay_draw.rectangle([x, y, x + w, y + h], fill=(255, 0, 0, 128))
                            img = Image.alpha_composite(img.convert("RGBA"), overlay)
                            logging.info(f"Moderate redaction applied at: {(x, y, w, h)}")
        
        return img.convert("RGB")  # Convert back to RGB if modified to RGBA

    except Exception as e:
        logging.error(f"Error in redact_text_in_image: {e}")
        raise
def redact_pdf(file_path):
    pdf_document = fitz.open(file_path)
    for page in pdf_document:
        try:
            # Redact text
            for word in page.get_text("words"):
                text = word[4]
                if any(re.search(pattern, text) for pattern in [
                    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                    r'\b\d{4} \d{4} \d{4} \d{4}\b',  # Credit card
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                    r'\b\d{10}\b'  # Phone number
                ]):
                    rect = fitz.Rect(word[:4])
                    page.add_redact_annot(rect, text="[REDACTED]", fill=(0, 0, 0))
            page.apply_redactions()

            # Blur images
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    base_image = pdf_document.extract_image(xref)
                    image = Image.open(io.BytesIO(base_image["image"]))
                    blurred_image = image.filter(ImageFilter.GaussianBlur(10))
                    blurred_image.save(f"temp_image_{img_index}.png")
                    rect = page.get_image_rects(xref)[0]
                    page.insert_image(rect, stream=open(f"temp_image_{img_index}.png", "rb").read())
                except Exception as e:
                    logging.error(f"Error processing image in PDF: {e}")

        except Exception as e:
            logging.error(f"Error processing page in PDF: {e}")

    # Save redacted PDF
    redacted_file_path = os.path.join(app.config['REDACTED_DOCUMENTS_FOLDER'], f"redacted_{os.path.basename(file_path)}")
    pdf_document.save(redacted_file_path, deflate=True)
    return redacted_file_path


def redact_word(file_path):
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            paragraph.text = redact_text(paragraph.text)

        # Save redacted Word document
        redacted_file_path = os.path.join(app.config['REDACTED_DOCUMENTS_FOLDER'], f"redacted_{os.path.basename(file_path)}")
        doc.save(redacted_file_path)
        return redacted_file_path
    except Exception as e:
        logging.error(f"Error processing Word document: {e}")
        raise



# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/text_redaction', methods=['GET', 'POST'])
def text_redaction():
    if request.method == 'POST':
        try:
            # Get text input from the form
            content = request.form.get('text_content', '').strip()
            if not content:
                # Return an error if no content is provided
                return render_template('text_redaction.html', error="Please provide text for redaction.")

            # Get the redaction level from the form
            redaction_level = request.form.get('redaction_level', 'low').lower()

            # Perform redaction
            redacted_content = redact_text(content, level=redaction_level)

            # Render the results
            return render_template(
                'text_redaction.html',
                original_content=content,
                redacted_content=redacted_content
            )

        except Exception as e:
            # Log the error and display a user-friendly message
            logging.error(f"Error in text_redaction route: {e}")
            return render_template('text_redaction.html', error="An error occurred during text redaction.")
    
    # For GET requests, just render the empty form
    return render_template('text_redaction.html')



@app.route('/image_redaction', methods=['GET', 'POST'])
def image_redaction():
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    file_path, filename = save_uploaded_file(image, app.config['UPLOAD_FOLDER'])
                    redaction_level = request.form.get('redaction_level', 'black')  # Get selected redaction level

                    # Perform redaction based on selected level
                    if redaction_level == 'ocr':
                        # OCR-based high-level text redaction
                        redacted_image = redact_text_in_image(file_path, redaction_level='high')
                    else:
                        # Non-OCR-based redaction (Blackout or Blur)
                        redacted_image = redact_image(file_path, redaction_level)

                    # Save the redacted image
                    redacted_image_path = os.path.join(app.config['REDACTED_IMAGES_FOLDER'], f'redacted_{filename}')
                    redacted_image.save(redacted_image_path)

                    return send_file(redacted_image_path, as_attachment=True)

            return render_template('image_redaction.html', error="Invalid or missing file.")
        except Exception as e:
            logging.error(f"Error in image_redaction route: {e}")
            return render_template('image_redaction.html', error="An error occurred during redaction.")
    return render_template('image_redaction.html')


@app.route('/document_redaction', methods=['GET', 'POST'])
def document_redaction():
    if request.method == 'POST':
        try:
            if 'document' in request.files:
                document = request.files['document']
                if document:
                    file_path, filename = save_uploaded_file(document, app.config['UPLOAD_FOLDER'])
                    file_extension = os.path.splitext(filename)[1].lower()

                    if file_extension == '.pdf':
                        redacted_file = redact_pdf(file_path)
                    elif file_extension in ['.doc', '.docx']:
                        redacted_file = redact_word(file_path)
                    else:
                        return render_template('document_redaction.html', error="Unsupported file format. Please upload a PDF or Word document.")

                    if os.path.exists(redacted_file):
                        return send_file(redacted_file, as_attachment=True)
                    else:
                        return render_template('document_redaction.html', error="Failed to save the redacted file.")
            else:
                return render_template('document_redaction.html', error="No file uploaded. Please upload a valid document.")

        except Exception as e:
            logging.error(f"Error in document redaction: {e}")
            return render_template('document_redaction.html', error="An error occurred while processing the document.")
    return render_template('document_redaction.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':

     # Get the port from the environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 to allow external access
    app.run(host="0.0.0.0", port=port)
