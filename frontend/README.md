# SPARTA AI Frontend

Modern, eye-friendly frontend for SPARTA AI data analysis platform, inspired by Julius AI and Kiro IDE.

## Features

- **Dark Theme Optimized**: Kiro-inspired color palette designed for long working hours
- **Modern UI**: Clean, professional interface with smooth animations
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Chat**: Interactive AI-powered conversations
- **File Upload**: Drag-and-drop support for CSV, Excel, and JSON files
- **Markdown Support**: Rich text rendering in chat messages

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Radix UI Components
- React Query
- Framer Motion
- Socket.io Client

## Getting Started

### Development

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Docker

```bash
# From project root
docker-compose up frontend
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router
│   │   ├── page.tsx      # Home page
│   │   ├── layout.tsx    # Root layout
│   │   └── globals.css   # Global styles
│   ├── components/
│   │   ├── chat/         # Chat interface components
│   │   ├── layout/       # Layout components
│   │   └── ui/           # Reusable UI components
│   └── lib/
│       ├── api.ts        # API client
│       └── utils.ts      # Utility functions
├── public/               # Static assets
└── package.json
```

## Color Palette

The theme uses a carefully selected color palette optimized for reduced eye strain:

- **Background**: Soft dark blue-gray (#1C2128)
- **Primary**: Gentle purple-blue (#8B9BF8)
- **Accent**: Muted secondary tones
- **Text**: High contrast but not harsh white

## Building for Production

```bash
npm run build
npm start
```

## Docker Build

```bash
docker build -t sparta-ai-frontend .
docker run -p 3000:3000 sparta-ai-frontend
```

## License

MIT
