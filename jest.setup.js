import "@testing-library/jest-dom";

// Add any global test setup here
// For example, mock global objects or set up fake timers

// Add dummy sweetalert2 implementation
jest.mock("sweetalert2", () => ({
  fire: jest.fn().mockResolvedValue({ isConfirmed: true }),
}));
