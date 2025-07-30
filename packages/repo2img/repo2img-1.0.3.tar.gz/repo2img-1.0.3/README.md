# repo2img (CLI)
A Python tool to encode and decode full code repositories into a single PNG image. Supports optional AES-256 encryption.

##  Features
- Encode full folders into a single .png file
- Decode image back into original repo (exact structure)
- Optional AES-256 encryption using password
- Offline CLI utility

##  Installation
```bash
pip install -r requirements.txt
```

##  Encode
```bash
python main.py encode --path ./my_repo --out repo.png --encrypt --password mypass
```

##  Decode
```bash
python main.py decode --path repo.png --out ./restored_repo --password mypass
```

##  Project Structure
- cli/: CLI argument handlers
- core/: core logic (archive, crypto, encode/decode)
- utils/: helpers for I/O, hashing
- main.py: CLI entrypoint

##  Encryption
- AES-256-GCM (with salt + password-derived key)
- Ensure password is kept safe to recover the repo

##  Notes
- Max repo size supported ~12GB (based on PNG pixel limits)
- All encoding is lossless and fully reversible
- Output image is not meant to be human-viewable
