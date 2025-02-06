import React from "react";
import styled from "styled-components";
import { getPieceSymbol } from "../utils/chessLogic";

const BoardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(8, 50px);
  grid-template-rows: repeat(8, 50px);
  gap: 0;
  border: 2px solid #333;
`;

const Square = styled.div`
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${(props) => (props.$isLight ? "#f0d9b5" : "#b58863")};
  cursor: pointer;
  font-size: 2em;
  ${(props) =>
    props.$isSelected &&
    `
    background-color: #7b61ff;
  `}
`;

function ChessBoard({ board, selectedSquare, onSquareClick }) {
  const renderSquare = (row, col) => {
    const isLight = (row + col) % 2 === 0;
    const piece = board[row][col];
    const isSelected =
      selectedSquare &&
      selectedSquare.row === row &&
      selectedSquare.col === col;

    return (
      <Square
        key={`${row}-${col}`}
        $isLight={isLight}
        $isSelected={isSelected}
        onClick={() => onSquareClick(row, col)}
      >
        {/* Convert piece object to symbol */}
        {piece ? getPieceSymbol(piece) : ""}
      </Square>
    );
  };

  return (
    <BoardContainer>
      {board.map((row, rowIndex) =>
        row.map((_, colIndex) => renderSquare(rowIndex, colIndex))
      )}
    </BoardContainer>
  );
}

export default ChessBoard;
