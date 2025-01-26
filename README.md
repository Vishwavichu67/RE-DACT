# Redaction Tool

A web-based application built with Flask that allows users to redact sensitive information from text, images, and documents (PDF and DOCX).

## Features

1. **Text Redaction**:
   - Redacts sensitive data such as phone numbers, emails, passwords, account numbers, and addresses.
   - Offers three redaction levels:
     - **Low**: Partial redaction.
     - **Moderate**: Full redaction of sensitive information.
     - **High**: Complete removal of all content.

2. **Image Redaction**:
   - Upload images for redaction.
   - Supports two levels:
     - **Blackout**: Covers the entire image or detected text areas with black.
     - **Blur**: Blurs sensitive areas or the entire image.
   - Includes OCR-based detection for text in images.

3. **Document Redaction**:
   - Handles PDF and DOCX files.
   - Redacts sensitive data using regex-based patterns.

4. **File Upload and Download**:
   - Uploaded files are stored temporarily for processing.
   - Redacted files are available for download.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd redaction_tool
