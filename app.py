from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from investment_pipeline import InvestmentAnalysisPipeline

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_deal():
    """
    Main endpoint to analyze an investment deal file.
    Expects a file upload with the investment deal document.
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(filepath)
        
        # Initialize pipeline
        pipeline = InvestmentAnalysisPipeline()
        
        # Run analysis
        results = pipeline.analyze(filepath)
        
        # Save reports
        report_id = f"report_{timestamp}"
        real_estate_path = os.path.join(app.config['REPORTS_FOLDER'], f"{report_id}_real_estate.txt")
        financial_path = os.path.join(app.config['REPORTS_FOLDER'], f"{report_id}_financial.txt")
        market_path = os.path.join(app.config['REPORTS_FOLDER'], f"{report_id}_market.txt")
        legal_path = os.path.join(app.config['REPORTS_FOLDER'], f"{report_id}_legal.txt")
        orchestrator_path = os.path.join(app.config['REPORTS_FOLDER'], f"{report_id}_orchestrator.txt")
        
        # Write reports to files
        with open(real_estate_path, 'w') as f:
            f.write(results['real_estate_report'])
        
        with open(financial_path, 'w') as f:
            f.write(results['financial_modeling_report'])
        
        with open(market_path, 'w') as f:
            f.write(results['market_analysis_report'])
        
        with open(legal_path, 'w') as f:
            f.write(results['legal_report'])
        
        with open(orchestrator_path, 'w') as f:
            f.write(results['orchestrator_report'])
        
        # Return results
        return jsonify({
            "status": "success",
            "report_id": report_id,
            "real_estate_report": results['real_estate_report'],
            "financial_modeling_report": results['financial_modeling_report'],
            "market_analysis_report": results['market_analysis_report'],
            "legal_report": results['legal_report'],
            "orchestrator_report": results['orchestrator_report'],
            "reports": {
                "real_estate": f"/reports/{report_id}_real_estate.txt",
                "financial": f"/reports/{report_id}_financial.txt",
                "market": f"/reports/{report_id}_market.txt",
                "legal": f"/reports/{report_id}_legal.txt",
                "orchestrator": f"/reports/{report_id}_orchestrator.txt"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Download a specific report file"""
    try:
        filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Changed default to 5001 to avoid macOS AirPlay conflict
    print(f"Starting Investment Deal Analysis Server on http://localhost:{port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Analyze endpoint: http://localhost:{port}/analyze")
    app.run(host='0.0.0.0', port=port, debug=True)

