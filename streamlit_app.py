git add .
git commit -m "Add PDF upload feature"
git push
```

Streamlit Cloud will auto-redeploy in ~30 seconds.

---

## How It Works:

1. Click **"Upload PDF"** in sidebar
2. Drag & drop your SMT telemetry PDF(s)
3. App parses the title to extract:
   - Car numbers (#1 vs #5, etc.)
   - 5-lap averages
   - Time deltas
4. Corner data is estimated based on the total delta

---

## ⚠️ Note on PDF Parsing:

The current parser extracts data from the PDF title format:
```
SMT Driver Compare: P, Practice Final Sticker Run Mid #1 L45-L49 (5 Lap Ave: 28.723) vs #5 L59-L63 (5 Lap Ave: 28.498)
