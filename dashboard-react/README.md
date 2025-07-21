# AI Agents Swarm - React Dashboard

A modern, real-time dashboard built with Next.js and TypeScript for monitoring the AI Agents Swarm automation system. This dashboard provides comprehensive insights into email processing, task management, and AI agent operations.

## 🚀 Features

- **Real-time WebSocket Updates**: Live system monitoring with instant notifications
- **Real-time Data Updates**: Auto-refreshes every 30 seconds with system metrics
- **Modern UI**: Built with Tailwind CSS and Headless UI components
- **Type Safety**: Full TypeScript support for better development experience
- **API Integration**: Communicates with the Python FastAPI backend
- **Error Handling**: Graceful fallbacks when backend is unavailable
- **Email Monitoring**: Real-time email processing status and statistics
- **Task Management**: Live task creation and status tracking
- **Agent Status**: Monitor email and Notion agent health
- **System Health**: Comprehensive system monitoring and diagnostics

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Heroicons & Lucide React
- **Data Fetching**: SWR for caching and real-time updates
- **UI Components**: Headless UI for accessibility

## 📦 Installation

### Prerequisites

- Node.js 18+ and npm 8+
- Python backend running on `http://localhost:8000` (optional for demo)

### Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Open Dashboard**
   - Visit `http://localhost:3000`
   - Dashboard will automatically detect if backend is available

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the dashboard-react directory:

```env
# API Backend URL (default: http://localhost:8000)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# WebSocket URL for real-time updates
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Optional: Enable debug mode
NODE_ENV=development

# Optional: Disable real-time features
NEXT_PUBLIC_DISABLE_WEBSOCKET=false
```

### Backend Integration

The dashboard communicates with the Python FastAPI backend via both REST API and WebSocket connections:

**REST API Endpoints:**
- `GET /health` - System health check with detailed diagnostics
- `GET /api/stats` - Comprehensive system statistics and metrics
- `GET /api/agents/status` - Real-time agent status information
- `GET /api/tasks/recent` - Recent tasks with full context
- `GET /api/logs` - System logs with filtering capabilities
- `GET /api/email/stats` - Email processing statistics
- `POST /api/trigger/email-processing` - Manual email processing trigger
- `POST /api/trigger/full-pipeline` - Full system pipeline execution

**WebSocket Endpoints:**
- `WS /ws` - Real-time system events and notifications
- Live task creation updates
- Agent status changes
- Email processing events
- System alerts and errors

### Docker Configuration

When running via Docker Compose, the dashboard automatically connects to the backend container:

```yaml
# In docker-compose.yml
dashboard:
  environment:
    - NEXT_PUBLIC_API_BASE_URL=http://api:8000
    - NEXT_PUBLIC_WS_URL=ws://api:8000
```

## 🔄 Integration with Python Backend

The dashboard automatically proxies API requests to the Python backend. When the backend is unavailable, it gracefully falls back to mock data for demonstration purposes.

### API Proxy Configuration

The dashboard uses Next.js rewrites to proxy `/api/backend/*` requests to the Python backend at `http://localhost:8000/*`.

## 🎨 Customization

### Theming

The dashboard uses a custom dark theme matching the original Streamlit design:

- **Primary Colors**: Navy blue gradient (#020617 to #1e293b)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Error**: Red (#ef4444)

### Tailwind Configuration

Edit `tailwind.config.js` to customize colors, fonts, and other design tokens.

### Component Structure

```
src/
├── app/                 # Next.js App Router pages
├── components/          # Reusable UI components
├── hooks/              # Custom React hooks
├── lib/                # Utility functions and API client
└── types/              # TypeScript type definitions
```

## 🔒 Security Considerations

- API requests are proxied through Next.js for security
- No sensitive data is stored in browser localStorage
- CORS headers are properly configured

## 🚀 Production Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Traditional Hosting

```bash
npm run build
npm run start
```

## 📄 License

This project is part of the AI Agents Swarm system. See the main project LICENSE file for details.
