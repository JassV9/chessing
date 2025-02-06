const express = require("express");
const cors = require("cors");
const { spawn } = require("child_process");

const app = express();
app.use(cors());
app.use(express.json());

// Add root route handler
app.get("/", (req, res) => {
  res.json({ message: "Chess server is running" });
});

// Update Stockfish path to your specific location
const STOCKFISH_PATH =
  "C:\\Users\\jason\\OneDrive\\Desktop\\aitesting\\chess-app\\server\\stockfish\\stockfish-windows-x86-64-avx2.exe";

let stockfish = null;

try {
  stockfish = spawn(STOCKFISH_PATH);
  console.log("Stockfish initialized successfully");

  stockfish.stderr.on("data", (data) => {
    console.error(`Stockfish Error: ${data}`);
  });

  stockfish.on("close", (code) => {
    console.log(`Stockfish process exited with code ${code}`);
  });
} catch (error) {
  console.error("Error initializing Stockfish:", error);
}

function sendToStockfish(command) {
  if (stockfish && stockfish.stdin) {
    stockfish.stdin.write(command + "\n");
  }
}

app.post("/move", (req, res) => {
  if (!stockfish) {
    return res.status(500).json({ error: "Stockfish not initialized" });
  }

  try {
    const { position } = req.body;

    let moveFound = false;

    stockfish.stdout.on("data", (data) => {
      const output = data.toString();
      if (output.includes("bestmove") && !moveFound) {
        moveFound = true;
        const move = output.split(" ")[1];
        res.json({ move });
      }
    });

    sendToStockfish("position startpos moves " + position);
    sendToStockfish("go depth 15");
  } catch (error) {
    console.error("Error processing move:", error);
    res.status(500).json({ error: "Error processing move" });
  }
});

app.post("/evaluate", (req, res) => {
  if (!stockfish) {
    return res.status(500).json({ error: "Stockfish not initialized" });
  }

  try {
    const { position } = req.body;

    let evalFound = false;

    stockfish.stdout.on("data", (data) => {
      const output = data.toString();
      if (output.includes("Total Evaluation:") && !evalFound) {
        evalFound = true;
        const eval = parseFloat(output.split("Total Evaluation:")[1]);
        res.json({ evaluation: eval });
      }
    });

    sendToStockfish("position startpos moves " + position);
    sendToStockfish("eval");
  } catch (error) {
    console.error("Error getting evaluation:", error);
    res.status(500).json({ error: "Error getting evaluation" });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
