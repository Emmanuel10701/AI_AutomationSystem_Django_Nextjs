

# ✈️ AI Flight Booking Assistant

A **modern AI-powered flight booking platform** that combines the power of **Django REST Framework (DRF)**, **LangChain**, **LangGraph**, **LlamaIndex**, and **Next.js** to create an intelligent, automated, and conversational flight booking experience.

---

## 🧠 About the Project

The **AI Flight Booking Assistant** represents a new generation of **Agentic AI web systems** — where language models are empowered with **tools**, **databases**, and **actions** to perform real-world operations.

Users can interact with a natural language interface to **search, compare, and book flights**, while the AI agent handles complex back-end logic such as:
- Checking flight availability
- Retrieving flight data from the database (via RAG and LlamaIndex)
- Making bookings
- Automating payments
- Managing user profiles securely

This project demonstrates a **full-stack integration of AI**, backend APIs, and frontend design — all built with modern, scalable technologies.

---

## ⚙️ Core Features

### 🧩 User & Authentication
- Secure registration and login via **JWT Authentication**
- User profile management (personal details, history, preferences)
- Password reset, verification, and token refresh endpoints

### 💬 AI Flight Agent
- Interactive chat interface where users communicate with an **AI-powered agent**
- Powered by **GPT (OpenAI)** or **Gemini (Google)**
- Uses **LangChain**, **LangGraph**, and **LlamaIndex** for reasoning and retrieval
- Implements **Retrieval-Augmented Generation (RAG)** to query real-time flight data

### 🛫 Flight Search & Booking
- Search flights by destination, date, airline, and price
- Real-time updates from backend database
- AI-assisted flight recommendation and comparison
- Smart agent automatically books the flight based on chat input

### 💳 Payment & Automation
- Payment integration with **Stripe / PayPal**
- Automatic booking confirmation once payment is completed
- AI handles transaction flow and responds with confirmation

### 🌐 Frontend Experience
- Built using **Next.js 14+** with **React 18**
- Modern **Tailwind CSS** UI components
- **Responsive**, **animated**, and **accessible** user experience
- Integrated chat interface with AI agent

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js, React, Tailwind CSS, Axios, Toastify, Framer Motion |
| **Backend** | Django 5+, Django REST Framework (DRF), Python 3.11+ |
| **AI Layer** | LangChain, LangGraph, LlamaIndex, OpenAI/Gemini APIs |
| **Database** | SQLite / PostgreSQL |
| **Payments** | Stripe or PayPal API |
| **Auth** | JWT Authentication |
| **Deployment** | Vercel (Frontend) + Render/Railway (Backend) |

---

## 🧱 Project Structure

```

flight-ai-project/
│
├── backend/
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── users/
│   ├── flights/
│   ├── bookings/
│   ├── payments/
│   ├── ai\_agent/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.local
│
├── .gitignore
├── README.md
└── LICENSE.md

````

---

## 🧭 System Architecture

```mermaid
graph TD
A[User] -->|Chat Input| B[Next.js Frontend]
B -->|API Call| C[Django REST Framework API]
C -->|Query| D[LangChain Agent]
D -->|Retrieve Data| E[LlamaIndex / Database]
E -->|RAG Response| D
D -->|Generated Response| C
C -->|Send AI Response| B
B -->|Display| A
````

-----

## 🚀 Installation & Setup

### 🔹 1. Clone the repository

```bash
git clone [https://github.com/emmanuel/flight-ai-project.git](https://github.com/emmanuel/flight-ai-project.git)
cd flight-ai-project
```

### 🔹 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate    # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

**Create Django Apps (If starting from scratch):**

```bash
# Assuming you've created a project named 'core'
# django-admin startproject core .

python manage.py startapp users
python manage.py startapp flights
python manage.py startapp bookings
python manage.py startapp payments
python manage.py startapp ai_agent
```

**Run migrations and start the server:**

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 🔹 3. Frontend Setup

```bash
cd ../frontend
npx create-next-app@latest . # Choose your setup options
npm install axios react-toastify tailwindcss postcss autoprefixer framer-motion
npx tailwindcss init -p # Initializes Tailwind config files
npm run dev
```

Then open:

👉 `http://localhost:3000`

### 🔹 4. Environment Variables

Create the following files and populate them with your keys:

| File | Variable | Description |
|---|---|---|
| **`backend/.env`** | `DEBUG` | `True` or `False` |
| | `SECRET_KEY` | Your Django secret key |
| | `DATABASE_URL` | PostgreSQL connection string |
| | `OPENAI_API_KEY` | Your OpenAI key for GPT |
| | `GOOGLE_API_KEY` | Your Google API key for Gemini |
| | `STRIPE_SECRET_KEY` | Stripe secret key for payments |
| **`frontend/.env.local`**| `NEXT_PUBLIC_BACKEND_URL`| `http://127.0.0.1:8000` or production URL |
| | `NEXT_PUBLIC_STRIPE_PUBLIC_KEY`| Stripe public key for frontend integration |

-----

## 💬 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/users/register/` | `POST` | Create a new user account |
| `/api/users/login/` | `POST` | Login user and receive JWT tokens |
| `/api/flights/` | `GET` | List all available flights |
| `/api/flights/search/?from=NYC&to=LON`| `GET` | Search for flights by criteria |
| `/api/bookings/` | `POST` | Create a new booking reservation |
| `/api/payments/` | `POST` | Handle payment processing |
| `/api/ai/chat/` | `POST` | Chat with the AI flight agent |

-----

## 🧠 AI Agent Flow

1.  **User asks a question:**
    > "Find me a flight from Nairobi to Dubai next Friday"
2.  Backend receives the request and triggers the **LangChain + LangGraph agent**.
3.  **LlamaIndex** fetches relevant flight data from the database.
4.  The **AI model (GPT/Gemini)** generates a grounded, structured response based on the retrieved data.
5.  The response includes flight options and prices.
6.  If the user confirms the booking, payment and booking automation executes via specialized agent tools.
7.  **Agent replies:**
    > "Your flight from Nairobi to Dubai on Oct 25th is confirmed ✈️"

-----

## 🧪 Testing

Run backend tests:

```bash
pytest
```

Run frontend tests:

```bash
npm run test
```

-----

## 🧰 Tools & Integrations

| Tool | Purpose |
|---|---|
| **LangChain** | LLM orchestration, prompt engineering, and memory management |
| **LangGraph** | Agentic workflow graphing, state management, and node-based reasoning |
| **LlamaIndex** | Knowledge retrieval from structured data (RAG) |
| **Hugging Face** | Embeddings and NLP models for semantic search |
| **Stripe API** | Payment gateway integration |
| **React Toastify** | User notification system |
| **Axios** | HTTP client for API requests |
| **Tailwind CSS** | Utility-first UI styling |
| **Framer Motion** | Animations and transitions |

### ⚡ RAG & LlamaIndex Workflow

The system uses **Retrieval-Augmented Generation (RAG)** for accurate, factual responses:

1.  User query is converted into **embeddings** using Hugging Face models.
2.  **LlamaIndex** retrieves related flight records from the vector store.
3.  The retrieved data is added to the **LangChain context** as grounding information.
4.  The **LLM (GPT/Gemini)** generates a final, factual response based on verified data.

-----

## 🔐 Security

  - **JWT-based authentication** and refresh tokens for session management.
  - **CORS** and **CSRF** protection enforced by DRF.
  - Encrypted **`.env`** variables and best practices for key management.
  - AI moderation and safety filters integrated with the LLM providers.
  - Safe tool calling and input validation in **LangGraph** workflows.

-----

## 📦 Deployment

### Frontend

  - Deploy easily on **Vercel** or **Netlify**.
  - Connect your GitHub repo → Auto build from the `frontend` directory.

### Backend

  - Deploy on **Render**, **Railway**, or **DigitalOcean App Platform**.
  - Set environment variables securely via the platform dashboard.

### Database

  - Use **PostgreSQL (Supabase/Neon)** for production data.
  - Run migrations automatically during the deploy process.

-----

## 📚 Documentation & Learning Resources

  - [LangChain Python Docs](https://www.langchain.com/)
  - [LangGraph Overview](https://langchain-ai.github.io/langgraph/)
  - [LlamaIndex Docs](https://docs.llamaindex.ai/)
  - [Next.js Docs](https://nextjs.org/docs)
  - [Django REST Framework Docs](https://www.django-rest-framework.org/)
  - [Stripe API Docs](https://stripe.com/docs/api)

-----

## 👨‍💻 Author

**Emmanuel**

🧑‍💻 Software Engineer | AI & Full-Stack Developer

🚀 Passionate about merging Artificial Intelligence and Web Engineering to solve real-world challenges.

📧 **Contact:** `emmanuel@example.com`

🌐 **GitHub:** `github.com/emmanuel`

-----

## 🪪 License

This project is licensed under the **MIT License** – see the `LICENSE.md` file for details.

⭐ If you found this project helpful, please give it a star\!

```

Is there anything else I can help you with regarding this project, like drafting the `requirements.txt` or `package.json` files?
```