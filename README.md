# 🩺 MediNotes Pro

**AI-powered consultation assistant for healthcare professionals.**

MediNotes Pro turns a doctor's raw consultation notes into three ready-to-use outputs, streamed live as the AI writes them:

1. 📋 **Summary of the visit** for the doctor's records
2. ✅ **Next steps** for the doctor
3. 📧 **A patient-friendly email** the doctor can send to the patient

Users sign in with **Clerk**, and the app is protected behind a paid **Clerk Billing** subscription plan. The frontend is a **Next.js** static export; the backend is a **FastAPI** server that calls the **OpenAI API** and streams the response with **Server-Sent Events (SSE)**. The whole app is packaged into a single **Docker** image that can run locally or on **AWS Lambda**.

> ⚠️ For demonstration purposes only. Not intended for real clinical use.

---

## ✨ Features

- 🔐 Sign-in / sign-up with Clerk (modal sign-in, user menu)
- 💳 Subscription paywall: `/product` is only available on the `premium_subscription` plan, otherwise a Clerk pricing table is shown
- 📝 Consultation form with patient name, visit date (date picker) and notes
- ⚡ Real-time streaming of the AI response (SSE via `@microsoft/fetch-event-source`)
- 🛡️ Backend verifies the Clerk JWT on every request
- 🧾 Markdown rendering with Tailwind Typography, light and dark mode
- 🐳 Multi-stage Docker build: one container serves both the frontend and the API
- ☁️ AWS Lambda ready via the AWS Lambda Web Adapter (with response streaming)

---

## 🛠️ Tech Stack

| Layer          | Technology                                                          |
|----------------|---------------------------------------------------------------------|
| Frontend       | Next.js 16 (Pages Router, static export), React 19, TypeScript      |
| Styling        | Tailwind CSS 4, `@tailwindcss/typography`                           |
| UI libraries   | `react-datepicker`, `react-markdown`, `remark-gfm`, `remark-breaks` |
| Auth & Billing | Clerk (`@clerk/nextjs`, `fastapi-clerk-auth`)                       |
| Streaming      | Server-Sent Events, `@microsoft/fetch-event-source`                 |
| Backend        | Python 3.12, FastAPI, Uvicorn, Pydantic                             |
| AI             | OpenAI API (`gpt-5-nano`)                                           |
| Deployment     | Docker, AWS Lambda Web Adapter                                      |

---

## 📁 Project Structure

```
saas/
├── api/
│   ├── server.py         # FastAPI app for Docker/AWS: POST /api/consultation, GET /health, serves the static frontend
│   └── index.py          # FastAPI function for Vercel: POST /api
├── pages/
│   ├── _app.tsx          # ClerkProvider + global styles
│   ├── _document.tsx     # Custom HTML document (title, meta)
│   ├── index.tsx         # Landing page (hero, features, sign in)
│   └── product.tsx       # Consultation form, protected by the subscription plan
├── public/               # Static assets
├── styles/
│   └── globals.css       # Tailwind CSS + Markdown styles
├── Dockerfile            # Multi-stage build: Next.js export -> Python/FastAPI image
├── next.config.ts        # Static export (output: 'export')
├── requirements.txt      # Python dependencies
├── package.json          # Node dependencies & scripts
└── tsconfig.json
```

---

## ⚙️ How It Works

1. The user signs in with Clerk on the landing page and clicks **Go to App**.
2. `/product` checks the user's plan with `<Protect plan="premium_subscription">`. Users without the plan see the `<PricingTable />`.
3. The doctor fills in the patient name, visit date and notes, then clicks **Generate Summary**.
4. The frontend gets a Clerk JWT and sends a `POST` to `/api/consultation` with `Authorization: Bearer <token>`.
5. FastAPI verifies the token using the Clerk JWKS URL, builds the prompt and calls OpenAI with `stream=True`.
6. Each chunk is sent back as an SSE event, and the page renders the growing Markdown output live.

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 22+ and npm
- [Python](https://www.python.org/) 3.12+
- [Docker](https://www.docker.com/) (for the container build)
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Clerk](https://clerk.com/) application with **Billing** enabled

### 1. Clone and install

```bash
git clone <your-repo-url>
cd saas

npm install
pip install -r requirements.txt
```

### 2. Set up Clerk

1. Create an application in the [Clerk dashboard](https://dashboard.clerk.com/).
2. Go to **Billing → Plans** and create a plan with the key **`premium_subscription`** (it must match the key in `pages/product.tsx`).
3. Copy your **Publishable key**, **Secret key** and **JWKS URL** (under **API Keys**).

### 3. Environment variables

Create a `.env.local` file in the project root:

```env
# Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json

# OpenAI
OPENAI_API_KEY=sk-...

# AWS (for deployment)
DEFAULT_AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

> ⚠️ Never commit `.env.local`. It is already listed in `.gitignore`.

---

## 🐳 Run with Docker (recommended)

The Dockerfile builds the Next.js static site, then copies it into a Python image where FastAPI serves both the pages and the API on port **8000**.

```bash
# Build the image (the Clerk publishable key is baked into the frontend at build time)
docker build --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_... -t medinotes-pro .

# Run the container
docker run -p 8000:8000 \
  -e CLERK_SECRET_KEY=sk_test_... \
  -e CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json \
  -e OPENAI_API_KEY=sk-... \
  medinotes-pro
```

Or pass your `.env.local` file directly:

```bash
docker run -p 8000:8000 --env-file .env.local medinotes-pro
```

Then open [http://localhost:8000](http://localhost:8000).

---

## ☁️ Deploy to AWS Lambda

The image already includes the [AWS Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter), which runs the FastAPI server inside Lambda with **response streaming** enabled (`AWS_LWA_INVOKE_MODE=response_stream`), so SSE works end to end.

1. Create an ECR repository and push the image:

   ```bash
   aws ecr get-login-password --region $DEFAULT_AWS_REGION | \
     docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com

   docker tag medinotes-pro:latest $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest
   docker push $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/medinotes-pro:latest
   ```

   > On Apple Silicon or other ARM machines, build with `--platform linux/amd64` (or set the Lambda architecture to arm64).

2. Create a Lambda function from the container image.
3. Add the environment variables `OPENAI_API_KEY`, `CLERK_SECRET_KEY` and `CLERK_JWKS_URL`.
4. Increase the timeout (for example 60 seconds or more) so long AI responses can finish.
5. Create a **Function URL** with invoke mode **`RESPONSE_STREAM`**.
6. Add the Function URL to your allowed origins/domains in the Clerk dashboard.

---

## 💻 Frontend-only Development

```bash
npm run dev
```

This starts the Next.js dev server on [http://localhost:3000](http://localhost:3000). It runs the frontend only: the API (`/api/consultation`) is served by FastAPI, so use Docker to test the full flow.

### Available scripts

| Command         | Description                          |
|-----------------|--------------------------------------|
| `npm run dev`   | Start the Next.js development server |
| `npm run build` | Build the static export into `out/`  |
| `npm run start` | Start the Next.js production server  |
| `npm run lint`  | Run ESLint                           |

---

## 🔌 API Reference

### `POST /api/consultation`

Generates the visit summary, next steps and patient email. The response is streamed.

**Headers**

```
Authorization: Bearer <Clerk JWT>
Content-Type: application/json
```

**Body**

```json
{
  "patient_name": "Jane Doe",
  "date_of_visit": "2026-11-10",
  "notes": "Pt presents with persistent cough x2 weeks, no fever. Chest clear. Advised fluids, rest. Review in 1 week if not improved."
}
```

**Response:** `text/event-stream`, Markdown with three sections:

- `### Summary of visit for the doctor's records`
- `### Next steps for the doctor`
- `### Draft of email to patient in patient-friendly language`

### `GET /health`

Health check used by Docker.

```json
{ "status": "healthy" }
```

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome. Fork the repo and open a pull request.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
