/// <reference types="vitest" />

// Provide globals like `test`, `expect` for the TS compiler when running vitest
declare const test: import('vitest').TestFn;
declare const expect: typeof import('vitest').expect;
