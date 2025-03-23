import "@testing-library/jest-dom";

// Add any global test setup here
// For example, mock global objects or set up fake timers

// Setup TextEncoder/TextDecoder for JSDOM
import { TextEncoder, TextDecoder } from "util";
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Add dummy sweetalert2 implementation
jest.mock("sweetalert2", () => ({
  fire: jest.fn().mockResolvedValue({ isConfirmed: true }),
}));
