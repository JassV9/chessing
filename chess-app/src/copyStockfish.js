const fs = require("fs");
const path = require("path");

// Source paths
const sourceDir = path.join(__dirname, "../node_modules/stockfish");
const stockfishJs = path.join(sourceDir, "stockfish.js");
const stockfishWasm = path.join(sourceDir, "stockfish.wasm");

// Destination paths
const destDir = path.join(__dirname, "../public");
const destStockfishJs = path.join(destDir, "stockfish.js");
const destStockfishWasm = path.join(destDir, "stockfish.wasm");

// Copy files
try {
  fs.copyFileSync(stockfishJs, destStockfishJs);
  fs.copyFileSync(stockfishWasm, destStockfishWasm);
  console.log("Stockfish files copied successfully!");
} catch (error) {
  console.error("Error copying Stockfish files:", error);
}
