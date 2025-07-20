# AI Agents Swarm - React Dashboard

A modern, real-time dashboard built with Next.js and TypeScript for monitoring the AI Agents Swarm automation system.

## 🚀 Features

- **Real-time Data Updates**: Auto-refreshes every 30 seconds with system metrics
- **Modern UI**: Built with Tailwind CSS and Headless UI components
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Type Safety**: Full TypeScript support for better development experience
- **API Integration**: Communicates with the Python FastAPI backend
- **Error Handling**: Graceful fallbacks when backend is unavailable
- **Mock Data**: Demonstrates functionality even without backend connection

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

Create a `.env.local` file in the root directory:

```env
# API Backend URL
API_BASE_URL=http://localhost:8000

# Optional: Enable debug mode
NODE_ENV=development
```

### Backend Integration

The dashboard expects the following API endpoints from the Python backend:

- `GET /health` - System health check
- `GET /api/stats` - System statistics
- `GET /api/agents/status` - Agent status information
- `GET /api/tasks/recent` - Recent tasks list
- `GET /api/logs` - System logs
- `POST /api/trigger/email-processing` - Trigger email processing
- `POST /api/trigger/full-pipeline` - Trigger full pipeline

## 🎯 Usage

### Auto-Refresh Control

- **Auto-refresh ON**: Dashboard updates every 30 seconds
- **Auto-refresh OFF**: Manual refresh only
- Toggle button in the top-right corner

### Connection Status

- **Connected**: Green indicator when backend is reachable
- **Disconnected**: Red indicator with mock data fallback

### Real-time Features

- **System Metrics**: Email count, task count, uptime, errors
- **Agent Status**: Real-time status of email and Notion agents
- **Recent Tasks**: Latest tasks created from email processing
- **System Logs**: Live system logs with color-coded levels

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

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot connect to backend"**
   - Ensure Python backend is running on `http://localhost:8000`
   - Check `API_BASE_URL` environment variable
   - Dashboard will show mock data if backend is unavailable

2. **Build errors**
   - Run `npm install` to ensure all dependencies are installed
   - Check Node.js version (requires 18+)

3. **TypeScript errors**
   - Run `npm run type-check` to validate types
   - Check imports and type definitions

### Development Tips

- Use `npm run dev` for hot-reload development
- Check browser console for API errors
- Use browser dev tools to inspect network requests

## 📱 Mobile Support

The dashboard is fully responsive and optimized for:
- **Desktop**: Full feature set with side-by-side layout
- **Tablet**: Responsive grid layout
- **Mobile**: Stacked layout with touch-friendly controls

## 🔒 Security Considerations

- API requests are proxied through Next.js for security
- No sensitive data is stored in browser localStorage
- CORS headers are properly configured

## 🚀 Production Deployment

### Vercel (Recommended)

```bash
# Deploy to Vercel
npx vercel

# Set environment variables in Vercel dashboard
API_BASE_URL=https://your-backend-domain.com
```

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

## 📊 Performance

- **First Load**: ~200kb JavaScript bundle
- **Hydration**: ~50ms on modern devices
- **API Requests**: Cached with SWR for optimal performance
- **Real-time Updates**: Efficient polling with automatic error retry

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI Agents Swarm system. See the main project LICENSE file for details.
