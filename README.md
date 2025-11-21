# Investment Deal Analysis App

A multi-agent pipeline application that analyzes investment deal documents and generates comprehensive reports on pros, cons, and final recommendations.

## Features

- **Web Interface**: Beautiful, modern frontend for easy file upload and result viewing
- **File Upload**: Accepts investment deal documents in multiple formats (TXT, PDF, DOC, DOCX, MD)
- **Drag & Drop**: Intuitive file upload with drag-and-drop support
- **Multi-Agent Pipeline**: Uses specialized AI agents for:
  - **Pros Analysis**: Identifies positive aspects, opportunities, and strengths
  - **Cons Analysis**: Identifies risks, challenges, and potential downsides
  - **Final Report**: Synthesizes analysis into a comprehensive investment recommendation
- **Report Generation**: Generates three separate reports plus a final synthesis
- **Report Download**: Download individual reports or all reports at once

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=5000
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5001` (default port changed to avoid macOS AirPlay conflict)
   
   - **Web Interface**: Open `http://localhost:5001` in your browser
   - **API Endpoint**: `http://localhost:5001/analyze`
   
   To use a different port, set the `PORT` environment variable:
   ```bash
   PORT=5000 python app.py
   ```

## API Endpoints

### POST `/analyze`
Analyzes an investment deal document.

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Body: `file` (investment deal document)

**Response**:
```json
{
  "status": "success",
  "report_id": "report_20240101_120000",
  "pros_report": "...",
  "cons_report": "...",
  "final_report": "...",
  "reports": {
    "pros": "/reports/report_20240101_120000_pros.txt",
    "cons": "/reports/report_20240101_120000_cons.txt",
    "final": "/reports/report_20240101_120000_final.txt"
  }
}
```

### GET `/reports/<filename>`
Downloads a specific report file.

### GET `/health`
Health check endpoint.

## Usage Example

```bash
# Using curl
curl -X POST http://localhost:5001/analyze \
  -F "file=@investment_deal.pdf"

# Using Python requests
import requests

with open('investment_deal.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5001/analyze',
        files={'file': f}
    )
    print(response.json())
```

## Project Structure

```
baypoint_mvp/
├── app.py                 # Main Flask application
├── investment_pipeline.py  # Multi-agent analysis pipeline
├── file_processor.py      # File processing utilities
├── router.py             # Original router (separate functionality)
├── requirements.txt      # Python dependencies
├── static/               # Frontend files
│   ├── index.html       # Main HTML page
│   ├── style.css        # Stylesheet
│   └── script.js        # Frontend JavaScript
├── uploads/             # Uploaded files (created automatically)
└── reports/             # Generated reports (created automatically)
```

## How It Works

1. **File Upload**: User uploads an investment deal document
2. **File Processing**: Document is processed and text is extracted
3. **Pros Analysis**: Pros agent analyzes positive aspects
4. **Cons Analysis**: Cons agent analyzes risks and challenges
5. **Final Report**: Final agent synthesizes both analyses into a recommendation
6. **Report Generation**: All reports are saved and returned to the user

## Notes

- Maximum file size: 16MB
- Supported file formats: TXT, PDF, DOC, DOCX, MD
- Reports are saved in the `reports/` directory
- Uploaded files are saved in the `uploads/` directory

