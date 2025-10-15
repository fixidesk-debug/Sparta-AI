# Sparta AI Frontend - Quick Setup Script
# Run this from the frontend directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sparta AI Chat Interface Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the frontend directory
if (!(Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found!" -ForegroundColor Red
    Write-Host "Please run this script from the frontend directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Green
Write-Host ""

# Core dependencies
Write-Host "Installing React libraries..." -ForegroundColor Yellow
npm install react react-dom uuid

# Dev dependencies for types
Write-Host "Installing TypeScript type definitions..." -ForegroundColor Yellow
npm install --save-dev @types/react @types/react-dom @types/uuid @types/node

# Code highlighting
Write-Host "Installing syntax highlighting..." -ForegroundColor Yellow
npm install react-syntax-highlighter
npm install --save-dev @types/react-syntax-highlighter

# Virtualization for performance
Write-Host "Installing virtualization libraries..." -ForegroundColor Yellow
npm install react-window react-virtualized-auto-sizer
npm install --save-dev @types/react-window @types/react-virtualized-auto-sizer

# Data visualization
Write-Host "Installing Plotly for charts..." -ForegroundColor Yellow
npm install plotly.js react-plotly.js
npm install --save-dev @types/react-plotly.js

# Optional: State management
Write-Host "Installing React Query (optional)..." -ForegroundColor Yellow
npm install @tanstack/react-query

# Tailwind CSS (if not already installed)
if (!(npm list tailwindcss 2>&1 | Select-String "tailwindcss")) {
    Write-Host "Installing Tailwind CSS..." -ForegroundColor Yellow
    npm install tailwindcss postcss autoprefixer
    npx tailwindcss init -p
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review CHAT_INTERFACE_SETUP.md for detailed documentation" -ForegroundColor White
Write-Host "2. Fix remaining TypeScript type errors" -ForegroundColor White
Write-Host "3. Configure environment variables (.env file)" -ForegroundColor White
Write-Host "4. Update WebSocket URL to match backend" -ForegroundColor White
Write-Host "5. Run: npm start" -ForegroundColor White
Write-Host ""

Write-Host "📊 Component Status:" -ForegroundColor Cyan
Write-Host "✅ Types (chat.ts)" -ForegroundColor Green
Write-Host "✅ WebSocket Hook (useWebSocket.ts)" -ForegroundColor Green
Write-Host "✅ ErrorBoundary (ErrorBoundary.tsx)" -ForegroundColor Green
Write-Host "✅ CodeBlock (CodeBlock.tsx)" -ForegroundColor Green
Write-Host "✅ FileUpload (FileUpload.tsx)" -ForegroundColor Green
Write-Host "✅ TypingIndicator (TypingIndicator.tsx)" -ForegroundColor Green
Write-Host "✅ MessageInput (MessageInput.tsx)" -ForegroundColor Green
Write-Host "✅ ChartDisplay (ChartDisplay.tsx)" -ForegroundColor Green
Write-Host "✅ MessageList (MessageList.tsx)" -ForegroundColor Green
Write-Host "✅ ChatContainer (ChatContainer.tsx)" -ForegroundColor Green
Write-Host ""

Write-Host "⚠️  Known Issues to Fix:" -ForegroundColor Yellow
Write-Host "- WebSocket hook type mismatches in ChatContainer" -ForegroundColor White
Write-Host "- Unused variables (setConversationId, messageGroups)" -ForegroundColor White
Write-Host "- CSS inline styles in 3 components" -ForegroundColor White
Write-Host ""

Write-Host "📖 See CHAT_INTERFACE_SETUP.md for complete details" -ForegroundColor Cyan
Write-Host ""
