{
    "jest": {
      "transform": {
        "^.+\\.(ts|tsx)$": "ts-jest"
      },
      "transformIgnorePatterns": [
        "node_modules/(?!(axios)/)"
      ],
      "moduleNameMapper": {
        "^@/components/(.*)$": "<rootDir>/src/components/$1"
      },
      "testEnvironment": "jsdom",
      "setupFilesAfterEnv": [
        "<rootDir>/src/setupTests.ts"
      ]
    }
  }