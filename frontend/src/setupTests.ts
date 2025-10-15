import '@testing-library/jest-dom';
import '@testing-library/jest-dom';

// Setup for axe-core accessibility testing
import 'jest-axe/extend-expect';

// Mock WebSocket globally if used
class WebSocketMock {
  send() {}
  close() {}
}

// @ts-ignore
global.WebSocket = WebSocketMock;
