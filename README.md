# QRNG API

Simple Flask API for Quantum Random Number Generation (QRNG).

Structure:

qrng_api/
│── app.py              # Flask entry point
│── qrng.py             # QRNG logic (placeholder)
│── routes.py           # API routes/endpoints
│── utils.py            # Helper functions
│── requirements.txt    # Dependencies
│── README.md           # Documentation

Run:

pip install -r requirements.txt
python app.py

Endpoints:

GET /api/random/bits?n=8
GET /api/random/hex?n=16
