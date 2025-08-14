from app import app

if __name__ == "__main__":
    import os
    # Ensure the app runs on 0.0.0.0 for Replit public access
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
