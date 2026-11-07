# 💡 Business Idea Generator

An AI-powered SaaS app that generates fresh **business ideas for AI Agents** and streams them to the browser in real time.

The frontend is built with **Next.js (Pages Router) + React + Tailwind CSS**, and the backend is a **Python FastAPI** serverless function that calls the **OpenAI API** and streams the response using **Server-Sent Events (SSE)**. The project is designed to be deployed on **Vercel**.

---

## ✨ Features

- 🤖 Generates a new AI-agent business idea on every page load
- ⚡ Real-time streaming of the response (Server-Sent Events)
- 📝 Markdown rendering with headings, sub-headings and bullet points (GFM + line breaks)
- 🎨 Clean, responsive UI with Tailwind CSS and dark mode support
- ☁️ One-click deployment to Vercel (Next.js frontend + Python function)

---

## 🛠️ Tech Stack

| Layer     | Technology                                              |
|-----------|---------------------------------------------------------|
| Frontend  | Next.js 16, React 19, TypeScript                        |
| Styling   | Tailwind CSS 4, `@tailwindcss/typography`               |
| Markdown  | `react-markdown`, `remark-gfm`, `remark-breaks`         |
| Backend   | Python, FastAPI, Uvicorn                                |
| AI        | OpenAI API (`gpt-5-nano`)                               |
| Hosting   | Vercel                                                  |

---

## 📁 Project Structure

```
saas/
├── api/
│   └── index.py          # FastAPI endpoint (/api) – streams the AI idea via SSE
├── pages/
│   ├── _app.tsx          # App wrapper, imports global styles
│   ├── _document.tsx     # Custom HTML document
│   └── index.tsx         # Home page – reads the SSE stream & renders Markdown
├── public/               # Static assets (icons, svgs)
├── styles/
│   └── globals.css       # Tailwind CSS & global styles
├── next.config.ts        # Next.js config (Turbopack + Tailwind loader)
├── requirements.txt      # Python dependencies (fastapi, uvicorn, openai)
├── package.json          # Node dependencies & scripts
└── tsconfig.json         # TypeScript config
```

---

## ⚙️ How It Works

1. The user opens the home page (`pages/index.tsx`).
2. The page opens an `EventSource` connection to `/api`.
3. `api/index.py` sends a prompt to OpenAI with `stream=True`.
4. Each chunk of text is forwarded to the browser as an SSE `data:` event.
5. The frontend appends each chunk to a buffer and renders it live as Markdown.

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 20+ and npm
- [Python](https://www.python.org/) 3.12+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- [Vercel CLI](https://vercel.com/docs/cli) (recommended for running the Python API locally)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd saas
```

### 2. Install dependencies

```bash
# Node dependencies
npm install

# Python dependencies
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env.local` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

> ⚠️ Never commit your `.env.local` file or API keys to Git.

### 4. Run locally

Because the backend is a Python function inside `api/`, the easiest way to run both frontend and backend together is with the Vercel CLI:

```bash
npm i -g vercel
vercel dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

> Running `npm run dev` alone starts only the Next.js frontend — the `/api` Python endpoint will not be available.

---

## 📜 Available Scripts

| Command         | Description                          |
|-----------------|--------------------------------------|
| `npm run dev`   | Start the Next.js development server |
| `npm run build` | Build the app for production         |
| `npm run start` | Start the production server          |
| `npm run lint`  | Run ESLint                           |

---

## ☁️ Deployment (Vercel)

1. Push the project to GitHub.
2. Import the repository on [Vercel](https://vercel.com/new).
3. Add the environment variable `OPENAI_API_KEY` in **Project Settings → Environment Variables**.
4. Deploy 🎉

Or deploy directly from the terminal:

```bash
vercel          # preview deployment
vercel --prod   # production deployment
```

---

## 🔌 API Reference

### `GET /api`

Streams a newly generated AI-agent business idea.

- **Response type:** `text/event-stream`
- **Format:** Markdown text sent as SSE `data:` lines

Example:

```bash
curl -N http://localhost:3000/api
```

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome! Feel free to fork the repo and open a pull request.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
