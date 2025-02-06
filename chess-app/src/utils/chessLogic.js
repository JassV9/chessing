export const PieceType = {
  PAWN: "p",
  ROOK: "r",
  KNIGHT: "n",
  BISHOP: "b",
  QUEEN: "q",
  KING: "k",
};

export const Color = {
  WHITE: "w",
  BLACK: "b",
};

export function initializeBoard() {
  const board = Array(8)
    .fill(null)
    .map(() => Array(8).fill(null));

  // Initialize pawns
  for (let i = 0; i < 8; i++) {
    board[1][i] = { type: PieceType.PAWN, color: Color.BLACK };
    board[6][i] = { type: PieceType.PAWN, color: Color.WHITE };
  }

  // Initialize other pieces
  const pieceOrder = [
    PieceType.ROOK,
    PieceType.KNIGHT,
    PieceType.BISHOP,
    PieceType.QUEEN,
    PieceType.KING,
    PieceType.BISHOP,
    PieceType.KNIGHT,
    PieceType.ROOK,
  ];

  for (let i = 0; i < 8; i++) {
    board[0][i] = { type: pieceOrder[i], color: Color.BLACK };
    board[7][i] = { type: pieceOrder[i], color: Color.WHITE };
  }

  return board;
}

export function getPieceSymbol(piece) {
  const symbols = {
    p: { w: "♙", b: "♟" },
    r: { w: "♖", b: "♜" },
    n: { w: "♘", b: "♞" },
    b: { w: "♗", b: "♝" },
    q: { w: "♕", b: "♛" },
    k: { w: "♔", b: "♚" },
  };

  return symbols[piece.type][piece.color];
}

export function isValidMove(board, from, to, currentPlayer) {
  if (!from || !to) return false;

  const piece = board[from.row][from.col];
  if (!piece || piece.color !== currentPlayer) return false;

  if (from.row === to.row && from.col === to.col) return false;

  const destPiece = board[to.row][to.col];
  if (destPiece && destPiece.color === currentPlayer) return false;

  // Piece-specific movement rules
  switch (piece.type) {
    case "p": // Pawn
      const direction = piece.color === "w" ? -1 : 1;
      const startRow = piece.color === "w" ? 6 : 1;

      // Normal move forward
      if (
        from.col === to.col &&
        to.row === from.row + direction &&
        !destPiece
      ) {
        return true;
      }
      // Initial two-square move
      if (
        from.col === to.col &&
        from.row === startRow &&
        to.row === from.row + 2 * direction &&
        !destPiece &&
        !board[from.row + direction][from.col]
      ) {
        return true;
      }
      // Capture diagonally
      if (
        Math.abs(to.col - from.col) === 1 &&
        to.row === from.row + direction &&
        destPiece
      ) {
        return true;
      }
      return false;

    case "r": // Rook
      return isValidRookMove(board, from, to);

    case "n": // Knight
      const rowDiff = Math.abs(to.row - from.row);
      const colDiff = Math.abs(to.col - from.col);
      return (
        (rowDiff === 2 && colDiff === 1) || (rowDiff === 1 && colDiff === 2)
      );

    case "b": // Bishop
      return isValidBishopMove(board, from, to);

    case "q": // Queen
      return (
        isValidRookMove(board, from, to) || isValidBishopMove(board, from, to)
      );

    case "k": // King
      return (
        Math.abs(to.row - from.row) <= 1 && Math.abs(to.col - from.col) <= 1
      );

    default:
      return false;
  }
}

function isValidRookMove(board, from, to) {
  if (from.row !== to.row && from.col !== to.col) return false;

  const rowDir = Math.sign(to.row - from.row);
  const colDir = Math.sign(to.col - from.col);

  let row = from.row + rowDir;
  let col = from.col + colDir;

  while (row !== to.row || col !== to.col) {
    if (board[row][col]) return false;
    row += rowDir;
    col += colDir;
  }

  return true;
}

function isValidBishopMove(board, from, to) {
  if (Math.abs(to.row - from.row) !== Math.abs(to.col - from.col)) return false;

  const rowDir = Math.sign(to.row - from.row);
  const colDir = Math.sign(to.col - from.col);

  let row = from.row + rowDir;
  let col = from.col + colDir;

  while (row !== to.row && col !== to.col) {
    if (board[row][col]) return false;
    row += rowDir;
    col += colDir;
  }

  return true;
}

export function makeMove(board, from, to) {
  // Create a deep copy of the board
  const newBoard = board.map((row) => [...row]);

  // Move the piece
  newBoard[to.row][to.col] = newBoard[from.row][from.col];
  newBoard[from.row][from.col] = null;

  return newBoard;
}

// Add more chess logic functions here
