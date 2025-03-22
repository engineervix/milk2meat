module.exports = {
  testEnvironment: "jsdom",
  moduleFileExtensions: ["js"],
  transform: {
    "^.+\\.js$": "babel-jest",
  },
  moduleNameMapper: {
    // Handle CSS imports in tests
    "\\.(css|less|scss)$": "<rootDir>/milk2meat/assets/__mocks__/styleMock.js",
  },
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testPathIgnorePatterns: ["/node_modules/", "/static/"],
  collectCoverage: true,
  coverageDirectory: "coverage",
  collectCoverageFrom: [
    "milk2meat/assets/js/**/*.js",
    "!milk2meat/assets/js/**/*.test.js",
    "!milk2meat/assets/js/**/__mocks__/**",
  ],
  coverageThreshold: {
    global: {
      statements: 0,
      branches: 0,
      functions: 0,
      lines: 0,
    },
  },
};
