module.exports = {
  testEnvironment: "jsdom",
  moduleFileExtensions: ["js"],
  transform: {
    "^.+\\.js$": "babel-jest",
  },
  moduleNameMapper: {
    // Handle CSS imports in tests
    "\\.(css|less|scss)$":
      "<rootDir>/milk2meat/frontend/__mocks__/styleMock.js",
  },
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testPathIgnorePatterns: ["/node_modules/", "/static/"],
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageReporters: ["json-summary", "text", "lcov"],
  collectCoverageFrom: [
    "milk2meat/frontend/js/**/*.js",
    "!milk2meat/frontend/js/**/*.test.js",
    "!milk2meat/frontend/js/**/__mocks__/**",
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 65,
      functions: 80,
      lines: 80,
    },
  },
};
