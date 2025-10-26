# Document Processing Guide

## Overview

The Morgan Legal Tender system now supports automated document processing with AI-powered analysis. Upload PDFs, images, Word documents, or Excel files, and the system will:

1. **Extract text content** (including OCR for scanned documents and images)
2. **Detect legal tasks** from the content
3. **Route to appropriate AI specialists** via Google Gemini
4. **Generate actionable insights** for review

---

## Supported Document Types

### Text-Based Documents
- **PDF files** (.pdf) - Text extraction with OCR fallback for scanned PDFs
- **Word documents** (.doc, .docx) - Full text and table extraction
- **Excel spreadsheets** (.xls, .xlsx) - All sheets and cell data
- **Plain text** (.txt) - Direct text processing

### Image Documents (OCR)
- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **BMP** (.bmp)
- **TIFF** (.tiff)

### Limits
- **Maximum file size**: 50MB per file
- **Batch uploads**: Multiple files supported

---

## How It Works

### Backend Processing Flow

```
Document Upload
    ↓
Text Extraction (PyPDF2, python-docx, openpyxl, pytesseract)
    ↓
Orchestrator Analysis
    ↓
Task Detection (retrieve records, legal research, drafting, etc.)
    ↓
Specialist Routing (Gemini AI)
    ↓
AI-Generated Results
```

### Frontend Interface

1. **Navigate to "Documents" tab** in the web interface
2. **Click or drag-and-drop** to upload a file
3. **Optionally enter a Case ID** for tracking
4. **Click "Upload and Process"**
5. **View results** including:
   - Extracted text
   - Detected tasks
   - AI specialist recommendations
   - Generated responses

---

## API Endpoints

### Upload Single Document
```bash
POST /api/documents/upload
Content-Type: multipart/form-data

Parameters:
- file: The document file (required)
- case_id: Associated case ID (optional)
- auto_process: Auto-send to orchestrator (default: true)
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/document.pdf" \
  -F "case_id=CASE-2024-001" \
  -F "auto_process=true"
```

### Batch Upload
```bash
POST /api/documents/batch-upload
Content-Type: multipart/form-data

Parameters:
- files: Multiple document files
- case_id: Associated case ID (optional)
```

### Extract Text Only
```bash
POST /api/documents/extract-text
Content-Type: multipart/form-data

Parameters:
- file: The document file
```

### Get Supported Types
```bash
GET /api/documents/supported-types
```

---

## Example Use Cases

### 1. Legal Memorandum Processing
Upload a legal memo and the system will:
- Detect tasks like "retrieve medical records"
- Identify legal research needs
- Route to Legal Researcher for case law analysis
- Generate citations and recommendations

### 2. Medical Records
Upload scanned medical records and the system will:
- OCR the document to extract text
- Identify medical providers and treatments
- Route to Records Wrangler
- Generate record request letters

### 3. Client Correspondence
Upload client emails or letters and the system will:
- Extract questions and concerns
- Detect communication needs
- Route to Communication Guru
- Draft appropriate responses

### 4. Court Documents
Upload court filings or motions and the system will:
- Extract legal arguments
- Detect research needs
- Route to Legal Researcher
- Provide relevant case law and analysis

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Document 'memo.pdf' processed successfully",
  "document_info": {
    "filename": "memo.pdf",
    "file_size": 1234567,
    "document_type": "pdf",
    "text_content": "...",
    "pages": 5,
    "extraction_method": "pdf_text",
    "success": true
  },
  "orchestrator_result": {
    "processing_id": "PROC-1234567890",
    "detected_tasks": [...],
    "routing_decisions": [...],
    "specialist_responses": [...],
    "approval_required": "pending"
  }
}
```

---

## OCR Configuration

### Prerequisites
For OCR functionality, Tesseract must be installed on the system:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Python Dependencies
```bash
pip install pytesseract pdf2image
```

---

## Best Practices

### 1. Document Quality
- **Use high-resolution scans** (300 DPI or higher) for best OCR results
- **Ensure clear text** in images for accurate extraction
- **PDF text extraction** is faster and more accurate than OCR

### 2. File Organization
- **Include case IDs** for better tracking
- **Use descriptive filenames** for easier identification
- **Upload related documents together** using batch upload

### 3. Review AI Output
- **Always review** AI-generated responses before sending to clients
- **Verify citations** for accuracy
- **Confirm task detection** matches your intent

### 4. Privacy & Security
- Documents are **processed in memory** and not permanently stored
- **PII/PHI detection** flags sensitive information
- **Use secure connections** (HTTPS) in production

---

## Error Handling

### Common Errors

**File Too Large:**
```json
{
  "detail": "File size exceeds maximum allowed size of 50MB"
}
```

**Unsupported Format:**
```json
{
  "detail": "Unsupported file type: application/zip"
}
```

**OCR Not Available:**
```json
{
  "detail": "OCR is not available. Install pytesseract and tesseract-ocr"
}
```

---

## Performance Tips

### Text-Based PDFs
- Processing time: **~1-3 seconds** for typical documents
- No OCR required - fastest method

### Scanned PDFs / Images
- Processing time: **~5-15 seconds** depending on page count
- OCR required - slower but handles scanned documents

### Batch Processing
- Upload multiple related documents together
- System combines text and processes as a single context
- More efficient for case-related document sets

---

## Testing

### Test Document
A sample legal memorandum is provided in `/test-documents/sample-legal-memo.txt`

### Run Test
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test-documents/sample-legal-memo.txt" \
  -F "case_id=TEST-CASE" \
  -F "auto_process=true"
```

### Expected Results
- **Tasks Detected**: 4 (retrieve records, schedule deposition, legal research, draft letter)
- **Specialists Routed**: Records Wrangler, Voice Scheduler, Legal Researcher, Communication Guru
- **Processing Time**: < 3 seconds

---

## Troubleshooting

### OCR Not Working
1. Verify Tesseract is installed: `tesseract --version`
2. Check Python packages: `pip list | grep pytesseract`
3. Review backend logs for OCR errors

### Poor Text Extraction
1. Check document quality (resolution, clarity)
2. Try different extraction methods
3. Pre-process images (enhance contrast, deskew)

### Slow Processing
1. Reduce file size before upload
2. Use text-based PDFs instead of scanned when possible
3. Process large batches during off-peak hours

---

## Future Enhancements

- **Document classification** (contracts, pleadings, correspondence)
- **Named entity recognition** (parties, dates, amounts)
- **Document comparison** (track changes, version control)
- **Template generation** (auto-fill forms from extracted data)
- **Multi-language support** (OCR and analysis in multiple languages)

---

For questions or issues, contact the development team or check the main README.
