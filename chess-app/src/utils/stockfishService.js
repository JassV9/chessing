let stockfish = null;

export function initializeStockfish() {
  return new Promise((resolve, reject) => {
    try {
      if (!stockfish) {
        stockfish = new Worker("/stockfish-worker.js");

        stockfish.onerror = (error) => {
          reject(error);
        };
      }

      const handleReady = (e) => {
        if (e.data === "readyok") {
          stockfish.removeEventListener("message", handleReady);
          resolve();
        }
      };

      stockfish.addEventListener("message", handleReady);
      stockfish.postMessage("uci");
      stockfish.postMessage("isready");
    } catch (error) {
      reject(error);
    }
  });
}

function boardToFen(board) {
  let fen = "";
  let emptyCount = 0;

  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const piece = board[row][col];
      if (piece) {
        if (emptyCount > 0) {
          fen += emptyCount;
          emptyCount = 0;
        }
        const pieceSymbol = piece.type;
        fen += piece.color === "w" ? pieceSymbol.toUpperCase() : pieceSymbol;
      } else {
        emptyCount++;
      }
    }
    if (emptyCount > 0) {
      fen += emptyCount;
      emptyCount = 0;
    }
    if (row < 7) fen += "/";
  }

  // Add other FEN components (assuming white to move, all castling rights, no en passant)
  fen += " w KQkq - 0 1";
  return fen;
}

function parseMove(moveString) {
  const files = "abcdefgh";
  const fromCol = files.indexOf(moveString[0]);
  const fromRow = 8 - parseInt(moveString[1]);
  const toCol = files.indexOf(moveString[2]);
  const toRow = 8 - parseInt(moveString[3]);

  return {
    from: { row: fromRow, col: fromCol },
    to: { row: toRow, col: toCol },
  };
}

export async function getMoveFromStockfish(board) {
  return new Promise((resolve, reject) => {
    if (!stockfish) {
      initializeStockfish();
    }

    const fen = boardToFen(board);
    let bestMove = null;

    const handleMessage = (e) => {
      const message = e.data;

      if (message.startsWith("bestmove")) {
        const moveString = message.split(" ")[1];
        if (moveString && moveString !== "(none)") {
          bestMove = parseMove(moveString);
          stockfish.removeEventListener("message", handleMessage);
          resolve(bestMove);
        } else {
          reject(new Error("No valid move found"));
        }
      }
    };

    stockfish.addEventListener("message", handleMessage);
    stockfish.postMessage("position fen " + fen);
    stockfish.postMessage("go depth 10");
  });
}

export async function getEvaluation(board) {
  return new Promise((resolve, reject) => {
    if (!stockfish) {
      initializeStockfish();
    }

    const fen = boardToFen(board);
    let evaluation = 0;

    const handleMessage = (e) => {
      const message = e.data;
      if (message.startsWith("info") && message.includes("score cp")) {
        const scoreMatch = message.match(/score cp (-?\d+)/);
        if (scoreMatch) {
          evaluation = parseInt(scoreMatch[1]) / 100;
          stockfish.removeEventListener("message", handleMessage);
          resolve(evaluation);
        }
      }
    };

    stockfish.addEventListener("message", handleMessage);
    stockfish.postMessage("position fen " + fen);
    stockfish.postMessage("go depth 10");
  });
}

// Initialize Stockfish when the service is loaded
initializeStockfish();
