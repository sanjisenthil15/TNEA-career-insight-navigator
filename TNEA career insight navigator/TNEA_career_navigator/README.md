# Smart TNEA College Recommendation System

A Flask-based web application that provides intelligent college recommendations for TNEA (Tamil Nadu Engineering Admissions) candidates based on their preferences, cutoff scores, and academic profile.

## Features

- Interactive college recommendation engine
- Real-time cutoff score analysis
- Branch-wise college filtering
- Personalized recommendations
- Responsive web interface

## Project Structure

```
TNEA_College_Recommendation/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── database/             # Database files
├── datasets/             # CSV data files for colleges, cutoffs, branches
├── static/               # Static assets (CSS, JS, Images)
├── templates/            # HTML templates
├── models/               # ML models and data models
├── routes/               # API routes and blueprints
├── utils/                # Utility functions
└── assets/               # Additional assets
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
