import { io, Socket } from "socket.io-client";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

class WebSocketService {
  private socket: Socket | null = null;
  private isEnabled = false; // Disable socket.io by default

  connect(token?: string) {
    // Socket.io is disabled - backend uses native WebSocket
    // Enable only when needed for chat/collaboration features
    if (!this.isEnabled) return null;
    
    if (this.socket?.connected) return this.socket;

    this.socket = io(WS_URL, {
      auth: token ? { token } : undefined,
      transports: ["websocket"],
    });

    this.socket.on("connect", () => {
      console.log("WebSocket connected");
    });

    this.socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
    });

    this.socket.on("error", (error) => {
      console.error("WebSocket error:", error);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event: string, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  getSocket() {
    return this.socket;
  }
}

export const wsService = new WebSocketService();
