# Certificate Verification System – Presentation Overview (Hackathon)

This document is a PPT-ready, end-to-end overview of your project. You can copy slide sections directly into PowerPoint/Google Slides.

## 1) Title & Problem

- Title: Certificate Verification System (OCR + Hash + MongoDB)
- Problem: Certificates are easy to forge; manual verification is slow and error-prone.
- Goal: Automate verification, detect tampering, and streamline certificate management.

## 2) Solution – What We Built

- OCR extracts text from PDF/images (Tesseract + PyMuPDF) and parses key fields.
- Stores canonical certificate metadata in MongoDB with fast search indexes.
- Verifies via:
  - File upload: OCR + SHA-256 integrity check + optional QR decode.
  - Manual fields: certificate_id/name/roll/course.
- Admin dashboard supports bulk import (JSON/CSV) and registration with file hashing.

## 3) Architecture (High Level)

- Frontend: Next.js (React), Tailwind CSS, Axios.
- Backend: Flask (Python), PyMuPDF (fitz), Tesseract (pytesseract), OpenCV (optional), PyMongo, pyzbar (optional for QR).
- Database: MongoDB (collections: certificates, verifications) with indexes on certificate_id_lower, file_hash, and normalized fields.

```mermaid
flowchart LR
  User[User/Verifier] -->|Upload file / enter fields| FE[Next.js Frontend]
  FE -->|HTTP/JSON| API[Flask API]
  API -->|OCR/QR| OCR[OCR Pipeline\n(Tesseract, PyMuPDF, OpenCV?)]
  API -->|CRUD| DB[(MongoDB)]
  API -->|Verdict+Record| FE
```

## 4) End-to-End Flows

### A. Verification (User)
1. Upload certificate (PDF/image) or enter fields on the Verify page.
2. Backend OCR extracts text; attempts QR decode; computes SHA-256 file hash.
3. Matching priority: QR-derived certificate_id → certificate_id → fields.
4. Returns verdict (valid/not_found), matched_by, integrity (match/mismatch/unknown), qr_verified, and record.

### B. Certificate Onboarding (Admin)
1. Import JSON/CSV via dashboard OR register a certificate with file + metadata.
2. On register: SHA-256 hash computed; optional auto OCR to fill missing fields.
3. Upsert into MongoDB with normalized fields and audit log entry.

### C. Verification Deep Dive (High-level vs Low-level)

High-level (what happens conceptually)
- Input options:
  - Upload a PDF/image, or
  - Enter certificate_id/name/roll_number/course as JSON.
- System extracts or uses provided identifiers → finds matching record in DB.
- If a file is uploaded, it computes SHA-256 and compares with stored `file_hash` for integrity.
- If a QR is present in the file, it parses it and cross-checks with the record.
- Returns a verdict and detailed signals: matched_by, integrity, qr_verified, and the matched record.

Low-level (step-by-step algorithm)
- By file (multipart):
  1) Save upload (secure filename, unique ID).
  2) Compute `observed_hash = SHA256(file_bytes)`.
  3) OCR: if image → preprocess + best PSM OCR; if PDF → direct text else rasterize + OCR.
  4) Extract candidate fields via regex (certificate_id, roll_number, name, course).
  5) QR attempt:
     - If image: run pyzbar on PIL image.
     - If PDF: rasterize page 1 (PyMuPDF) → PIL → pyzbar.
     - Parse QR payload: try JSON → else URL query → else token; derive `qr_id`/`qr_hash`.
  6) Matching logic:
     - If `qr_id` present and no `cert_id`, set `cert_id = qr_id` and `matched_by = qr`.
     - If `cert_id` present: DB get_by_certificate_id(cert_id) → if found, `matched_by = certificate_id`.
     - Else: find_candidate(name, roll, course) using normalized fields → if found, `matched_by = fields`.
  7) Verdict & signals:
     - `verdict = valid` if record found else `not_found`.
     - `integrity = match|mismatch|unknown` depending on stored `file_hash` vs `observed_hash`.
     - `qr_verified = true` if `qr_id == record.certificate_id` OR (`qr_hash` matches stored `file_hash`).
  8) Cleanup the uploaded temp file.

- By fields (JSON):
  1) Read JSON: certificate_id? name? roll_number? course? file_hash? qr_payload?
  2) If certificate_id → get_by_certificate_id; else find_candidate by normalized fields.
  3) If file_hash provided and record has `file_hash`, compare for integrity.
  4) If qr_payload provided, parse like above and set `qr_verified` accordingly.
  5) Return verdict, matched_by, record, integrity, qr flags.

Contract (inputs/outputs)
- Inputs:
  - Multipart: file (pdf|png|jpg|jpeg|bmp|tiff, ≤16MB)
  - JSON: { certificate_id?, name?, roll_number?, course?, file_hash?, qr_payload? }
- Output (success): {
  success, verdict, matched_by, record?, integrity, observed_file_hash?, qr_payload?, qr_verified?
}
- Output (error): { success:false, error, message? }, with HTTP 400/401/413/500.

Edge cases handled
- Missing/empty file → 400; unsupported type → 400; file too large → 413.
- PDF with zero pages → error message captured; OCR failures degrade gracefully.
- QR optional: if pyzbar not installed or QR absent, the verification still proceeds.
- Normalization uses lowercase and removes whitespace for name/roll/course; originals preserved.

## 5) Key Features

- Multi-format support: PDF, PNG, JPG, JPEG, BMP, TIFF (up to 16MB).
- OCR tuning: best PSM selection by mean confidence; preprocess with OpenCV (if installed).
- QR support: decodes payloads; accepts JSON/URL/token and cross-checks with stored data.
- Integrity: SHA-256 hash comparison detects tampering.
- Admin features: import, register, stats, recent records.

## 6) Backend APIs (Summary)

- GET `/` – Health check (includes MongoDB status).
- POST `/api/ocr` – Multipart file → OCR result + extracted_fields.
- POST `/api/verify` – By file (multipart) or by fields (JSON) → verdict, record, integrity, qr status.
- POST `/api/import` – Admin bulk import JSON/CSV-like payload (X-API-Key).
- POST `/api/register` – Admin register file + metadata; computes file_hash; optional auto_ocr (X-API-Key).
- GET `/api/admin/stats` – Admin stats (counts, issuers, recent).
- GET `/api/admin/records` – Admin paginated list; supports limit/offset.

Notes:
- Admin auth: header `X-API-Key` (default demo key: `demo-admin-key`, can override via `ADMIN_KEYS`).
- Errors: 400 (bad uploads), 401 (auth), 413 (size), 500 (internal) with JSON messages.

## 7) Data Model (MongoDB)

- certificates: `certificate_id`, normalized fields (`*_normalized`), `file_hash`, `file_name`, `file_ext`, timestamps.
- verifications: audit entries with type, certificate_id, file_hash, timestamp, admin role.
- Indexes:
  - `certificate_id_lower`, `file_hash`
  - Compound: `(name_normalized, roll_number_normalized, course_normalized)`
  - Logs: `timestamp`

## 8) Security & Constraints

- Admin authentication via API key with role and optional issuer scope.
- CORS enabled for localhost development.
- File constraints: allowed extensions and 16MB limit; temporary files are removed after processing.
- Integrity: SHA-256 hash comparison when applicable.

## 9) Cryptography Deep Dive (Implemented + Roadmap)

This section highlights the cryptographic techniques and the technical approach you can present.

### 9.1 Implemented Today

- SHA-256 File Hashing (tamper detection)
  - Canonicalization: raw file bytes (no normalization); hash covers the entire uploaded artifact.
  - Storage: hex-encoded string in MongoDB `file_hash`.
  - Code (backend/db/store.py):

```python
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
```

- Integrity Verification (Upload-time check)
  - Algorithm (POST /api/verify):
    1) Read uploaded file → compute `observed_hash = SHA256(bytes)`
    2) Lookup record by `certificate_id` or candidate fields
    3) If stored `file_hash` present, compare
       - match → integrity = "match"
       - mismatch → integrity = "mismatch"
       - otherwise → integrity = "unknown"

- QR-Aided Validation (Opportunistic)
  - If a QR is present and decodable, parse payload to extract `certificate_id` and optionally `file_hash`.
  - Cross-check: If `qr.certificate_id == record.certificate_id` OR `qr.file_hash == record.file_hash`, set `qr_verified = true`.
  - Accepts JSON, URL query string, or plain token formats.

### 9.2 Proposed Enhancements (Technical Roadmap)

- Signed QR Payloads (Binding identity → artifact)
  - Use a compact signature over the payload (Ed25519 preferred for short keys/signatures). Options:
    - COSE_Sign1 (CBOR) or JWS (compact JSON) for transport.
  - Suggested payload schema (JSON example):

```json
{
  "certificate_id": "JH-UNI-2022-0001",
  "file_hash": "61857430ce3e2350...",
  "issuer_id": "XYZ-UNIV",
  "issued_at": "2025-09-24T10:30:00Z",
  "exp": "2028-09-24T10:30:00Z",
  "alg": "Ed25519",
  "kid": "xyz-univ-key-2025-01",
  "sig": "BASE64URL_SIGNATURE"
}
```

- Issuer PKI / Key Registry
  - Maintain issuer public keys in a registry (DB table or JWKS endpoint) keyed by `kid`.
  - Rotation policy, expiry and revocation.

- Content Addressing & Timestamping
  - Merkle-based proofs for batches; anchor Merkle root on a public timestamping service (e.g., OpenTimestamps) or blockchain for immutable audit.
  - Store `ots` receipt per batch for later verification.

- Hash-Based Download Links
  - When distributing certificates, serve by content hash and enforce `Content-MD5`/ETag (with HTTPS/TLS 1.3).

- HMAC for Short-Lived Tokens
  - Sign ephemeral tokens with HMAC (server secret) including nonce and expiry to prevent replay.

### 9.3 Threat Model & Mitigations

- Forged PDF/Image → Mitigated by SHA-256 mismatch.
- QR Substitution → Today: cross-check id/hash; Roadmap: signed QR + expiry.
- Replay of Old QR → Roadmap: include `exp` and revocation checks.
- Unauthorized Admin Ops → API key auth now; add rate limits/IP allowlists/audit.

### 9.4 Technical Specs (Precise)

- Hash Domain: `SHA256(file_bytes)`; hex string stored as `file_hash`.
- Matching Priority in Verify: QR id → certificate_id → normalized fields.
- Normalization (search only): lowercased, whitespace stripped; originals preserved.
- Transport Security: Use HTTPS in production; set HSTS.

## 10) Performance Considerations

- OCR: choose best PSM by confidence; rasterize PDFs at configurable zoom (default 3.0) for accuracy.
- MongoDB: indexes enable fast lookups and paginated listing.
- PyMuPDF direct text extraction used before OCR for vector PDFs (faster/better when available).

## 10) Setup & Run (Local Demo)

Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Ensure MongoDB is running at `mongodb://localhost:27017/`.
4. Windows only: set `TESSERACT_CMD` to your Tesseract exe if not in PATH (e.g., `/c/Program Files/Tesseract-OCR/tesseract.exe`).
5. `python app.py` → API at `http://localhost:5000`.

Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev` → UI at `http://localhost:3000`.

Quick Checks
- Verify by fields:
  - `POST /api/verify` with `{ "certificate_id": "..." }`.
- Import sample (admin):
  - `POST /api/import` with header `X-API-Key: demo-admin-key` and `{ "records": [ ... ] }`.

## 11) Limitations

- OCR accuracy depends on scan quality; OpenCV preprocessing improves results if installed.
- QR decode requires `pyzbar` and readable QR.
- Root README mentions Poppler; actual code uses PyMuPDF and does NOT require Poppler.

## 12) Roadmap (Next Iterations)

- Digital signatures (sign & verify) for stronger authenticity.
- QR payload standardization with cryptographic binding to file hash.
- Issuer portal and role-based data segregation.
- ML-driven template-based extraction; multilingual OCR.
- Optional blockchain anchoring for immutable proofs.

## 13) Slide Deck Outline (Copy-Paste)

1. Title & Team
2. Problem & Impact
3. Solution Overview (what we built)
4. Architecture Diagram (FE → API → OCR/DB)
5. User Flow: Verification (upload/fields → verdict)
6. Verification Deep Dive (High-level vs Low-level algorithm)
6. Admin Flow: Import & Registration (hashing)
7. Features & Differentiators
8. Demo Screens (OCR, Verify, Admin)
9. API Summary (endpoints & contracts)
10. Data Model & Indexing
11. Cryptographic Techniques (Deep Dive)
  - Implemented: SHA-256 + QR cross-check
  - Roadmap: Signed QR (Ed25519), PKI, Merkle proofs/anchoring, HMAC tokens
12. Security (API key, roles, CORS) & Integrity
13. Performance & Scalability
14. Limitations
15. Roadmap
16. Setup & Live Demo Steps
17. Q&A

## 14) Talking Points (Presenter Notes)

- Emphasize multi-layer verification: database match + file integrity + QR.
- Highlight MongoDB migration: indexes, normalized search, stats.
- Call out OCR strategy: direct text for vector PDFs, fallback OCR for scans.
- Show that admin operations are authenticated and auditable.
- Close with a roadmap that’s realistic for post-hackathon growth.
