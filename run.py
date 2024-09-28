import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if PORT is not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
