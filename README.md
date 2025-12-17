# dakota-leads

A FastAPI-based webhook server designed for integration and automation, ready for cloud deployment (e.g., Render).  
Created and maintained by [surfingcloud9].

## Features

- Built with **FastAPI** for speed and simplicity
- Handles webhook events (customize as needed)
- Ready for deployment to cloud hosts

## Getting Started

### Prerequisites

- Python 3.8+
- Requirements listed in `requirements.txt`

### Installation

Clone the repository:
```sh
git clone https://github.com/surfingcloud9/dakota-leads.git
cd dakota-leads
```

Create a virtual environment (recommended) and install dependencies:
```sh
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally

```sh
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Deploying

- Configure environment variables as needed by your deployment provider (see below for Eleven Labs).
- Push to your deployment platform (e.g., Render, Heroku, etc.).

## Configuration

If you integrate with external APIs like Eleven Labs, **you may need to set API keys or other environment variables.**

**Example variables you might need:**
- `ELEVENLABS_API_KEY`
- Any webhook secrets or tokens

You can set these in your Render/hosting provider’s dashboard as environment variables, or in a `.env` file **(make sure not to commit secrets!)**.

## Contributing

PRs are welcome! For major changes, please open an issue first.

## License

Specify your license here, if any (MIT, Apache, etc.).
