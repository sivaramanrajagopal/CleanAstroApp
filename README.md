# Vedic Astrology Dashboard

A modern, production-ready Vedic Astrology Dashboard built with Python and Flask, following Parashara principles. Features accurate planetary positions, house analysis, yogas, Shadbala, Vimshottari Dasha (Mahadasha & Antardasha), transits, and compatibility analysis. Designed for clarity, robustness, and user-friendliness.

---

## Features
- **Birth Chart**: Lagna, planetary positions, house analysis, yogas, Shadbala, and summary
- **Dasha**: Vimshottari Mahadasha and Antardasha (Bhukti) periods, with current period highlighted
- **Transits**: Current planetary transits mapped to houses, with effects
- **Compatibility**: Synastry analysis between two charts
- **User Experience**: LocalStorage caching of birth details, clear button, tooltips, and legend explanations

---

## Directory Structure

```
CleanAstroApp/
├── app.py
├── vedic_astrology_engine.py
├── vedic_astrology_modular.py
├── transit_calculator.py
├── compatibility_analyzer.py
├── requirements.txt
└── templates/
    ├── chart.html
    ├── dasha.html
    ├── transits.html
    ├── compatibility.html
    └── index.html
```

---

## Setup & Running Locally

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or, if pip is not found:
   python3 -m pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python app.py
   # or
   python3 app.py
   ```
4. **Open your browser:**
   [http://localhost:5050/](http://localhost:5050/)

---

## Usage
- Enter your birth details in any form. They will be cached in your browser for convenience.
- Use the "Clear Details" button to clear cached data.
- Navigate between Chart, Dasha, Transits, and Compatibility pages from the navigation bar.
- Tooltips and a legend explain key astrological terms.

---

## GitHub Check-in
1. Initialize git (if not already):
   ```bash
   git init
   ```
2. Add all files:
   ```bash
   git add .
   ```
3. Commit:
   ```bash
   git commit -m "Initial clean production-ready Vedic Astrology Dashboard"
   ```
4. Add your remote and push:
   ```bash
   git remote add origin <your-repo-url>
   git branch -M main
   git push -u origin main
   ```

---

## Troubleshooting
- **pip not found:** Use `python3 -m pip` instead of `pip`.
- **Swiss Ephemeris errors:** Ensure ephemeris files are present or set the path in your code.
- **Port conflicts:** Change the port in `app.py` if needed.
- **Other errors:** Copy the error message and seek help or open an issue.

---

## Extending/Customizing
- Add more yogas, detailed Shadbala breakdown, or PDF export as needed.
- All core logic is modular and ready for extension.

---

## Credits
- Built with [Flask](https://flask.palletsprojects.com/), [Swiss Ephemeris](https://www.astro.com/swisseph/), and Python 3.
- Classical Vedic astrology principles (Parashara). 